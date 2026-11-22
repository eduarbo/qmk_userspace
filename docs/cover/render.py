"""Build the README covers with Blender, rsvg-convert and ImageMagick 7.

Run from the repository root: blender -b --factory-startup --python-exit-code 1 -P docs/cover/render.py
"""

import math
import subprocess
import tempfile
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
SCENE = bpy.context.scene
NS = "{http://www.w3.org/2000/svg}"
PAPER = "#f6efdf"
INK = "#182c31"
ACCENTS = {
    "Super": "#bca2f3",
    "Shift": "#e8bb85",
    "Cmd": "#8ccebc",
    "Symbols": "#a2c9ec",
    "Ctrl": "#e19f95",
}


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


def lettering(value, x, y, z, size, mat, parent):
    font = bpy.data.curves.new(value, "FONT")
    font.body = value
    font.align_x = font.align_y = "CENTER"
    font.size = size
    obj = bpy.data.objects.new(value, font)
    SCENE.collection.objects.link(obj)
    obj.parent = parent
    obj.location = (x, y, z)
    # Printed legends sit optically flush with the dished key surface.
    obj.visible_shadow = False
    obj.data.materials.append(mat)


def build_split():
    board = ET.parse(HERE.parent / "layers/macos.svg").getroot()
    ivory = material("Ivory keycaps", "#eadfc9")
    dark = material("Legends", "#101e21", 0.78)
    dark.node_tree.nodes["Principled BSDF"].inputs[
        "Specular IOR Level"
    ].default_value = 0.03
    body = material("Pine enclosure", "#375256", 0.27, 0.36)
    seam = material("Case seam", "#162a2c", 0.44)
    function_mats = {key: material(key, color) for key, color in ACCENTS.items()}
    positions = []
    roles = []
    for side in ["left", "right"]:
        group = board.find(f".//{NS}g[@id='{side}-hand']")
        half = bpy.data.objects.new(side, None)
        SCENE.collection.objects.link(half)
        # Use real column stagger and thumb positions. The two drawing axes have different pitches.
        caps = []
        for g in group.findall(NS + "g"):
            x, y = map(
                float,
                g.get("transform").removeprefix("translate(").removesuffix(")").split(),
            )
            lines = ["".join(t.itertext()) for t in g.findall(NS + "text")]
            caps.append(((x - 39) / 74, -(y - 131) / 61, lines))
        center_x = sum(x for x, y, labels in caps) / len(caps)
        center_y = sum(y for x, y, labels in caps) / len(caps)
        half.location = ((center_x - 5.5) * 1.08, center_y + 1.7, 0.02)
        half.rotation_euler.z = math.radians(-12 if side == "left" else 12)
        shape = group.find(NS + "polygon")
        points = []
        for pair in shape.get("points").split():
            x, y = map(float, pair.split(","))
            points.append(
                ((x - 39) / 74 - 0.45 - center_x, -(y - 131) / 61 + 0.47 - center_y)
            )
        points.reverse()
        for name, levels, mat, edge in [
            ("Base", (0.01, 0.26), body, 0.09),
            ("Gasket", (0.22, 0.295), seam, 0.02),
            ("Plate", (0.285, 0.37), body, 0.035),
        ]:
            solid(
                name,
                [[(x * 1.045, y * 1.065, z) for x, y in points] for z in levels],
                mat,
                half,
                edge,
            )
        for x, y, labels in caps:
            x -= center_x
            y -= center_y
            tap = labels[0]
            hold = labels[1] if len(labels) > 1 else None
            if hold:
                roles.append((tap, hold))
            # Three bevels and a lowered center give the cap a dished, low-profile top.
            profile = [
                (0.90, 0.90, 0.39, 0.09),
                (0.94, 0.94, 0.44, 0.12),
                (0.85, 0.85, 0.62, 0.12),
                (0.78, 0.78, 0.665, 0.115),
                (0.68, 0.68, 0.667, 0.11),
                (0.54, 0.54, 0.65, 0.095),
                (0.32, 0.32, 0.629, 0.08),
                (0.15, 0.15, 0.625, 0.05),
            ]
            key = solid(
                tap,
                [rounded(*ring) for ring in profile],
                function_mats.get(hold, ivory),
                half,
            )
            key.location = (x, y, 0)
            if tap == "⌫":
                tap = "Bksp"
            lettering(
                tap,
                x,
                y + (0.094 if hold else 0),
                0.675,
                0.21 if len(tap) > 1 else 0.28,
                dark,
                half,
            )
            if hold:
                lettering(hold, x, y - 0.14, 0.675, 0.137, dark, half)
            positions.append((half, x, y))
    assert len(positions) == 36 and len(roles) == 6 and roles[2] == roles[3]
    return positions, roles[:3] + roles[4:]


def area(name, pos, energy, size, color):
    lamp = bpy.data.lights.new(name, "AREA")
    lamp.energy, lamp.shape, lamp.size, lamp.color = energy, "DISK", size, color
    obj = bpy.data.objects.new(name, lamp)
    SCENE.collection.objects.link(obj)
    obj.location = pos
    obj.rotation_euler = (
        (Vector((0, 0, 0)) - obj.location).to_track_quat("-Z", "Y").to_euler()
    )


def render_scene(out):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    positions, roles = build_split()
    bpy.ops.mesh.primitive_plane_add(size=200)
    bpy.context.object.data.materials.append(material("Backdrop", "#233e43", 0.60))
    area("Softbox", (-5, 4, 12), 1750, 9, (1, 0.91, 0.78))
    area("Cool fill", (4, -3, 8), 850, 8, (0.76, 0.90, 1))
    area("Rim", (5, 5, 5), 550, 6, (0.67, 1, 0.87))
    SCENE.world.color = (0.18, 0.18, 0.18)
    SCENE.render.engine = "CYCLES"
    SCENE.cycles.samples = 48
    SCENE.cycles.use_denoising = True
    camera = bpy.data.cameras.new("Cover")
    cam = bpy.data.objects.new("Cover", camera)
    SCENE.collection.objects.link(cam)
    SCENE.camera = cam
    camera.type = "ORTHO"
    direction = Vector((1.0, -11.0, 15.2)).normalized()
    rotation = (-direction).to_track_quat("-Z", "Y")
    cam.rotation_euler = rotation.to_euler()
    right, up = rotation @ Vector((1, 0, 0)), rotation @ Vector((0, 1, 0))
    bpy.context.view_layer.update()
    points = [
        half.matrix_world @ Vector((x + dx, y + dy, z))
        for half, x, y in positions
        for dx in [-0.55, 0.55]
        for dy in [-0.55, 0.55]
        for z in [0, 0.7]
    ]
    xs = [v.dot(right) for v in points]
    ys = [v.dot(up) for v in points]
    camera.ortho_scale = (max(xs) - min(xs)) / 0.715
    center = right * ((max(xs) + min(xs)) / 2 - 0.12 * camera.ortho_scale)
    center += up * ((max(ys) + min(ys)) / 2)
    cam.location = center + direction * 28
    SCENE.render.resolution_x, SCENE.render.resolution_y = 1760, 680
    SCENE.render.resolution_percentage = 100
    SCENE.render.image_settings.file_format = "PNG"
    SCENE.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    return roles


def caption(x, y, words, size, color, weight=500, align="start", mono=False):
    family = "Menlo, monospace" if mono else "Arial, sans-serif"
    return f'<text x="{x}" y="{y}" text-anchor="{align}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(words)}</text>'


def compose(temp, photo, roles, mobile):
    width, height = (800, 828) if mobile else (1440, 741)
    top = 494 if mobile else 556
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
    ]
    if mobile:
        # Crop the negative space used by the desktop title, retaining both hands.
        image_args = ["-crop", "1390x680+386+0", "+repage", "-resize", "800x"]
        px, py = 0, 81
        svg += [
            caption(26, 57, "36 keys", 48, PAPER, 750),
            caption(775, 51, "QMK  ·  PIANTOR / CORNE", 20, PAPER, 600, "end", True),
        ]
    else:
        image_args = ["-resize", "1440x556!"]
        px, py = 0, 0
        svg += [
            caption(44, 71, "QMK", 22, "#b3d2c5", 600, mono=True),
            caption(35, 232, "36", 155, PAPER, 750),
            caption(45, 284, "keys", 60, PAPER, 550),
            caption(47, 374, "Piantor", 36, PAPER, 600),
            caption(47, 414, "Corne", 36, PAPER, 600),
        ]
    svg.append(
        f'<rect x="0" y="{top}" width="{width}" height="{height - top}" fill="{PAPER}"/>'
    )
    if mobile:
        svg += [
            caption(25, top + 54, "MacBook", 39, INK, 700),
            caption(774, top + 50, "Karabiner-Elements", 25, INK, 500, "end"),
        ]
        x, cap_y = 109, top + 106
        widths = [117, 117, 152, 117, 117]
        printed_keys = ["L ⌥", "L ⌘", "Space bar", "R ⌘", "R ⌥"]
        svg += [
            caption(24, cap_y + 104, "Tap", 22, INK),
            caption(24, cap_y + 158, "Hold", 22, INK),
        ]
    else:
        svg += [
            caption(45, top + 78, "MacBook", 44, INK, 700),
            caption(47, top + 115, "Karabiner-Elements", 22, INK),
        ]
        x, cap_y = 382, top + 25
        widths = [171, 171, 269, 171, 171]
        printed_keys = [
            "Left Option",
            "Left Cmd",
            "Space bar",
            "Right Cmd",
            "Right Option",
        ]
        svg += [
            caption(288, cap_y + 79, "Tap", 18, INK),
            caption(288, cap_y + 124, "Hold", 18, INK),
        ]
    for (tap, hold), printed, cap_w in zip(roles, printed_keys, widths):
        middle = x + cap_w / 2
        key_h = 57 if mobile else 43
        svg += [
            f'<rect x="{x}" y="{cap_y}" width="{cap_w}" height="{key_h}" rx="10" fill="{ACCENTS[hold]}"/>',
            caption(
                middle,
                cap_y + (36 if mobile else 28),
                printed,
                25 if mobile else 21,
                INK,
                650,
                "middle",
            ),
            caption(
                middle,
                cap_y + (104 if mobile else 79),
                tap,
                23 if mobile else 24,
                INK,
                700,
                "middle",
            ),
            caption(
                middle, cap_y + (158 if mobile else 124), hold, 22, INK, 500, "middle"
            ),
        ]
        x += cap_w + (9 if mobile else 14)
    overlay = temp / "overlay.svg"
    overlay.write_text("\n".join(svg + ["</svg>"]))
    subprocess.run(
        ["rsvg-convert", str(overlay), "-o", str(temp / "type.png")], check=True
    )
    subprocess.run(
        [
            "magick",
            "-size",
            f"{width}x{height}",
            "xc:#253d40",
            "(",
            str(photo),
            *image_args,
            ")",
            "-geometry",
            f"+{px}+{py}",
            "-composite",
            str(temp / "type.png"),
            "-geometry",
            "+0+0",
            "-composite",
            "-strip",
            "-quality",
            "92",
            str(HERE / ("layout-mobile.webp" if mobile else "layout.webp")),
        ],
        check=True,
    )


if __name__ == "__main__":
    if not bpy.app.background:
        raise SystemExit("Run the cover renderer in a new background Blender process.")
    with tempfile.TemporaryDirectory() as folder:
        temp = Path(folder)
        photo = temp / "split.png"
        roles = render_scene(photo)
        for mobile in (False, True):
            compose(temp, photo, roles, mobile)
