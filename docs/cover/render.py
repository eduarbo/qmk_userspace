"""Render the Piantor from the pinned PCB and compose both README animations.

blender -b --factory-startup --python-exit-code 1 -P docs/cover/render.py
Set PIANTOR_LEFT_PCB for an offline build. The two PCB halves are mirror images.
"""

import hashlib
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from tour import animate

SCENE = bpy.context.scene
REV = "cd847afb4f9a86e8c1c8e36f243140644013afb2"
PCB = f"https://raw.githubusercontent.com/beekeeb/piantor/{REV}/pcb/left/keyboard_pcb.kicad_pcb"
SHA256 = "9e4333e7cbea29ddf55aef41336867b514ba896b76d31e6b5a08a6b9183c3a9d"
WIDTH, HEIGHT = 720, 554


def material(name, color, roughness=0.38, metal=0):
    rgb = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4 for s in rgb]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*linear, 1)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metal
    return mat


def solid(name, rings, mat, parent, bevel=0):
    n = len(rings[0])
    vertices = [v for ring in rings for v in ring]
    faces = [tuple(reversed(range(n)))]
    for j in range(len(rings) - 1):
        for i in range(n):
            k = (i + 1) % n
            faces.append((j * n + i, j * n + k, (j + 1) * n + k, (j + 1) * n + i))
    faces.append(tuple(range(len(vertices) - n, len(vertices))))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    SCENE.collection.objects.link(obj)
    obj.parent = parent
    obj.data.materials.append(mat)
    for poly in mesh.polygons[1:-1]:
        poly.use_smooth = not bevel
    if bevel:
        modifier = obj.modifiers.new("Rounded shell edge", "BEVEL")
        modifier.width, modifier.segments = bevel, 5
        obj.modifiers.new("Planar face normals", "WEIGHTED_NORMAL")
    return obj


def rounded(width, depth, z, radius):
    outline = []
    for cx, cy, a in [(1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)]:
        for k in range(8):
            angle = math.radians(a + 90 * k / 7)
            outline.append(
                (
                    cx * (width / 2 - radius) + radius * math.cos(angle),
                    cy * (depth / 2 - radius) + radius * math.sin(angle),
                    z,
                )
            )
    return outline


def area(name, pos, energy, size, color):
    lamp = bpy.data.lights.new(name, "AREA")
    lamp.energy, lamp.shape, lamp.size, lamp.color = energy, "DISK", size, color
    obj = bpy.data.objects.new(name, lamp)
    SCENE.collection.objects.link(obj)
    obj.location = pos
    obj.rotation_euler = (
        (Vector((0, 0, 0)) - obj.location).to_track_quat("-Z", "Y").to_euler()
    )


def read_pcb():
    path = os.environ.get("PIANTOR_LEFT_PCB")
    data = Path(path).read_bytes() if path else urlopen(PCB, timeout=30).read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("Piantor PCB does not match the pinned source")
    source = data.decode()
    parts = {}
    for block in source.split("\n  (footprint ")[1:]:
        ref = re.search(r'\(fp_text reference "([^"]+)"', block)[1]
        at = [float(n) for n in re.search(r"\(at ([^)]+)", block)[1].split()]
        parts[ref] = at if len(at) == 3 else at + [0]
    # Follow Edge.Cuts after snapping off the optional sixth column at its mouse bites.
    start, seam = (81.6, 62.4), (81.6, 111.6)
    edges = {}
    for line in source.splitlines():
        if '(layer "Edge.Cuts")' not in line or "(gr_" not in line:
            continue
        pts = [
            tuple(round(float(v), 4) for v in pair.split())
            for pair in re.findall(r"\((?:start|mid|end) ([-.\d ]+)\)", line)
        ]
        if not pts or min(x for x, _ in pts) < 81.6:
            continue
        if all(x == 81.6 for x, _ in pts):
            continue
        edges[pts[0]] = edges.get(pts[0], []) + [pts]
        edges[pts[-1]] = edges.get(pts[-1], []) + [pts[::-1]]
    outline = [start]
    prev, here = None, start
    while here != seam:
        (segment,) = (seg for seg in edges[here] if seg[-1] != prev)
        if len(segment) == 3:
            a, m, b = map(Vector, segment)
            control = 2 * m - (a + b) / 2
            for i in range(1, 8):
                t = i / 8
                outline.append(
                    tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * control + t * t * b)
                )
        outline.append(segment[-1])
        prev, here = here, segment[-1]
    return parts, outline


def build(side, parts, outline):
    sign = 1 if side == "left" else -1

    def xy(x, y):
        return (sign * (x - 142.2) / 18, (88.3 - y) / 18)

    half = bpy.data.objects.new(side, None)
    SCENE.collection.objects.link(half)
    half.rotation_euler.z = math.radians(-4.2 * sign)
    pcb = material("Solder mask", "#174b45", 0.42)
    fr4 = material("Board edge", "#b29b6f", 0.5)
    black = material("Plate and sockets", "#232c31", 0.32)
    graphite = material("Graphite", "#424648", 0.4)
    silver = material("Brushed steel", "#aab2b4", 0.29, 0.76)
    gold = material("Plated pads", "#c9ae71", 0.34, 0.45)
    green = material("Pico board", "#246b50", 0.45)
    ivory = material("Porcelain keycaps", "#f0e8d5", 0.35)
    apricot = material("Thumb keycaps", "#d7a581", 0.36)

    def block(name, x, y, z, w, h, thick, mat, radius=0.04):
        obj = solid(
            name, [rounded(w, h, level, radius) for level in (0, thick)], mat, half
        )
        obj.location = (x, y, z)
        return obj

    def pcb_sheet(name, lower, upper, mat):
        pts = [xy(*p) for p in outline]
        if (
            sum((pts[i - 1][0] * y - x * pts[i - 1][1]) for i, (x, y) in enumerate(pts))
            < 0
        ):
            pts.reverse()
        solid(
            name,
            [[(x, y, z) for x, y in pts] for z in (lower, upper)],
            mat,
            half,
            0.015,
        )

    pcb_sheet("Bottom plate", 0, 0.12, black)
    pcb_sheet("Laminate", 0.14, 0.215, fr4)
    pcb_sheet("Piantor PCB", 0.215, 0.24, pcb)
    x, y = xy(*parts["U2"][:2])
    block("Headers", x, y, 0.245, 1.06, 2.66, 0.15, black)
    block("Raspberry Pi Pico", x, y, 0.396, 21 / 18, 51 / 18, 0.07, green, 0.072)
    block("Micro USB shell", x, y + 1.34, 0.466, 0.46, 0.30, 0.14, silver, 0.03)
    block("USB opening", x, y + 1.484, 0.48, 0.34, 0.028, 0.08, black, 0.008)
    block("RP2040", x, y - 0.19, 0.468, 0.40, 0.40, 0.064, graphite, 0.022)
    block("BOOTSEL", x - 0.23, y + 0.63, 0.466, 0.19, 0.14, 0.057, silver, 0.018)
    block("Flash", x + 0.18, y + 0.38, 0.466, 0.19, 0.25, 0.045, black, 0.018)
    block("Crystal", x - 0.26, y - 0.65, 0.466, 0.18, 0.13, 0.05, silver, 0.012)
    silk = material("Silkscreen", "#f7f0d8", 0.65)

    def print_pcb(value, px, py, size):
        font = bpy.data.curves.new(value, "FONT")
        font.body, font.size, font.align_x = value, size, "CENTER"
        obj = bpy.data.objects.new(value, font)
        SCENE.collection.objects.link(obj)
        obj.parent = half
        obj.location = (px, py, 0.478)
        obj.data.materials.append(silk)

    print_pcb("Pico", x, y - 1.02, 0.17)
    print_pcb("RP2040", x, y + 0.075, 0.09)
    print_pcb("BOOTSEL", x, y + 0.83, 0.07)
    for dx, dy in [
        (-0.27, 0.21),
        (0.24, -0.46),
        (0.27, -0.64),
        (-0.28, -0.43),
        (0.13, 0.56),
        (0.29, 0.12),
        (-0.22, 0.94),
    ]:
        block("SMD contact", x + dx, y + dy, 0.468, 0.098, 0.048, 0.012, silver, 0.009)
        block("Passive", x + dx, y + dy, 0.48, 0.057, 0.046, 0.012, graphite, 0.006)
    for dx in (-0.31, 0.31):
        for dy in (-1.17, 1.16):
            block(
                "Pico mounting pad",
                x + dx,
                y + dy,
                0.468,
                0.13,
                0.13,
                0.011,
                gold,
                0.063,
            )
            block(
                "Mounting bore", x + dx, y + dy, 0.48, 0.085, 0.085, 0.005, black, 0.04
            )
    for n in range(20):
        for dx in (-0.49, 0.49):
            block(
                "Castellated pad",
                x + dx,
                y + (9.5 - n) * 2.54 / 18,
                0.468,
                0.13,
                0.071,
                0.008,
                gold,
                0.028,
            )
            block(
                "Plated bore",
                x + dx,
                y + (9.5 - n) * 2.54 / 18,
                0.478,
                0.042,
                0.042,
                0.005,
                black,
                0.020,
            )
    x, y = xy(*parts["J1"][:2])
    block("TRRS jack", x - sign * 0.38, y, 0.24, 0.78, 0.36, 0.28, black)
    for ref in ("H1", "H2", "H3", "H4"):
        x, y = xy(*parts[ref][:2])
        block("Mounting screw", x, y, 0.24, 0.19, 0.19, 0.035, silver, 0.088)
        block("Hex recess", x, y, 0.276, 0.078, 0.078, 0.005, black, 0.026)
    positions = {}
    for row in range(4):
        for col in (range(3) if row == 3 else range(1, 6)):
            ref = f"K{row}{col}"
            x, y, deg = parts[ref]
            x, y = xy(x, y)
            index = (
                (30 + (col if sign == 1 else 5 - col))
                if row == 3
                else row * 10 + (col - 1 if sign == 1 else 10 - col)
            )
            # Choc spacing is 18 × 17 mm. Each ring follows the skirt, bevel or dish.
            profile = [
                (17.4, 16.4, 4.55, 1.5),
                (17.5, 16.5, 5.15, 1.7),
                (16.8, 15.8, 6.9, 1.7),
                (15.9, 14.9, 7.45, 1.8),
                (14.8, 13.8, 7.52, 1.7),
                (12.2, 11.2, 7.32, 1.5),
                (8.4, 7.4, 7.03, 1.4),
                (4.3, 3.3, 6.92, 0.9),
            ]
            key = solid(
                ref,
                [rounded(*(v / 18 for v in ring)) for ring in profile],
                apricot if row == 3 else ivory,
                half,
            )
            key.location = (x, y, 0.06)
            key.rotation_euler.z = math.radians(sign * deg)
            positions[index] = key
    return positions


def render_half(folder, side, parts, outline):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    positions = build(side, parts, outline)
    area("Window", (-4, 5, 9), 930, 7, (1, 0.94, 0.83))
    area("Bounce", (4, -4, 7), 490, 6, (0.81, 0.91, 1))
    area("Rim", (4, 5, 4), 230, 5, (0.84, 1, 0.93))
    SCENE.world.color = (0.2, 0.2, 0.2)
    SCENE.render.engine = "CYCLES"
    SCENE.cycles.samples = 24
    SCENE.cycles.use_denoising = True
    camera = bpy.data.cameras.new("Overhead")
    cam = bpy.data.objects.new("Overhead", camera)
    SCENE.collection.objects.link(cam)
    SCENE.camera = cam
    direction = Vector((0, -0.37, 1)).normalized()
    cam.location = Vector((0, 0, 0.2)) + direction * 18
    cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    camera.type = "ORTHO"
    camera.ortho_scale = 7.38
    SCENE.render.resolution_x, SCENE.render.resolution_y = WIDTH, HEIGHT
    SCENE.render.resolution_percentage = 100
    SCENE.render.film_transparent = True
    SCENE.render.image_settings.color_mode = "RGBA"
    SCENE.render.image_settings.file_format = "PNG"
    SCENE.render.filepath = str(folder / f"{side}.png")
    bpy.context.view_layer.update()

    def project(key, offset):
        p = world_to_camera_view(SCENE, cam, key.matrix_world @ Vector(offset))
        return (WIDTH * p.x, HEIGHT * (1 - p.y))

    anchors = {}
    for index, key in positions.items():
        x, y = project(key, (0, 0, 0.403))
        u, v = project(key, (0.4, 0, 0.403))
        anchors[index] = (x, y, math.degrees(math.atan2(v - y, u - x)))
    bpy.ops.render.render(write_still=True)
    return anchors


if __name__ == "__main__":
    if not bpy.app.background:
        raise SystemExit("Use a new background Blender process")
    parts, outline = read_pcb()
    with tempfile.TemporaryDirectory() as folder:
        folder = Path(folder)
        anchors = {s: render_half(folder, s, parts, outline) for s in ("left", "right")}
        animate(folder, anchors)
