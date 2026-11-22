"""Generate the layer tour with Python 3.9+, rsvg-convert and ImageMagick 7."""

import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE.parent))
from draw_layout import read_keymap
from layer_art import legend, rect, text
from tour import ESC, TOUR

PCB = "https://raw.githubusercontent.com/beekeeb/piantor/cd847afb4f9a86e8c1c8e36f243140644013afb2/pcb/left/keyboard_pcb.kicad_pcb"
LAUNCHER = "https://raw.githubusercontent.com/eduarbo/dotfiles/1bc5984127eefbd46bdf3b0e4034b4e6df126f12/macos/hammerspoon/docs/launcher.svg"
DARK, FACE, INK = "#193132", "#f6f0e0", "#183131"
MINT, AMBER, MUTED = "#a3eccb", "#ffc28e", "#bdd0c8"
NS = "{http://www.w3.org/2000/svg}"


def source(env, url, digest):
    local = os.environ.get(env)
    if local:
        data = Path(local).read_bytes()
    else:
        with urlopen(url, timeout=30) as response:
            data = response.read()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError(f"Source differs from the pinned revision: {url}")
    return data


def switches():
    pcb = source(
        "PIANTOR_LEFT_PCB",
        PCB,
        "9e4333e7cbea29ddf55aef41336867b514ba896b76d31e6b5a08a6b9183c3a9d",
    )
    halves = ({}, {})
    for part in pcb.decode().split("\n  (footprint ")[1:]:
        ref = re.search(r'\(fp_text reference "K([0-3])([0-5])"', part)
        if not ref:
            continue
        row, col = map(int, ref.groups())
        if (row < 3 and col == 0) or (row == 3 and col > 2):
            continue
        at = [float(v) for v in re.search(r"\(at ([^)]+)", part)[1].split()]
        x, y = at[:2]
        # KiCad angles are counterclockwise. SVG's y axis points down.
        angle = -at[2] if len(at) == 3 else 0
        left, right = (
            (30 + col, 35 - col)
            if row == 3
            else (10 * row + col - 1, 10 * row + 10 - col)
        )
        halves[0][left] = (x, y, angle)
        halves[1][right] = (x, y, -angle)
    if set(halves[0]) | set(halves[1]) != set(range(36)):
        raise ValueError("Expected 36 Piantor switch centers")
    return halves


def hyper_map(physical, base):
    svg = source(
        "HYPER_LAUNCHER_SVG",
        LAUNCHER,
        "9db6b0229653e72080cdfc727bacb3088c1a3880609b597c964d5fbb1157367d",
    )
    apps = {}
    for group in ET.fromstring(svg).iter(NS + "g"):
        position = next(
            (
                el
                for el in group.findall(NS + "text")
                if "shifted" in el.get("class", "").split()
            ),
            None,
        )
        if position is None:
            continue
        action = group.find(f"{NS}text[@class='key tap']")
        apps[position.text] = (
            "\n".join(t.strip() for t in action.itertext() if t.strip())
            if action is not None
            else ""
        )
    if set(apps) != set(physical[:30]) - {"⌫"} | {"/"}:
        raise ValueError("Hyper launcher is missing physical positions")
    return [apps.get(key, "") for key in physical[:30]] + base[30:]


def maps():
    physical, layers = read_keymap()
    base = layers["macOS base"]
    layers["Hyper"] = hyper_map(physical, base)
    # Specify the held keys per frame. Other Adjust thumbs inherit the base.
    layers["Adjust"] = layers["Adjust"][:30] + base[30:]
    # Gamepad has higher QMK priority. Its transparent positions expose Adjust.
    layers["Gamepad + Adjust"] = [
        adjust if legend(game).get("type") == "trans" else game
        for game, adjust in zip(layers["Gamepad"], layers["Adjust"])
    ]
    return physical, layers


def keycap(angle, index, physical, binding, frame):
    key = legend(binding)
    held, tapped = index in frame.held, index == frame.tap
    tap, hold, alternate = key["t"], key.get("h", ""), key.get("s", "")
    if held:
        tap = "Alt" if frame.layer == "Gamepad + Adjust" and index == ESC else physical
        hold = "held"
        alternate = ""
    elif tapped:
        tap, hold, alternate = physical, "tap", ""
    blank = not tap
    fill = "#d7dfd3" if key.get("type") == "trans" else FACE
    if held:
        fill = MINT
    elif tapped:
        fill = AMBER
    elif blank:
        fill = "#344b4c"
    body = [
        f'<g transform="rotate({angle:g})">',
        rect(-41, -36, 82, 76, 9, "#0e2426"),
        rect(-41, -38, 82, 74, 9, fill),
    ]
    show_position = physical != tap and (tap or frame.layer in {"Hyper", "Super"})
    if show_position and frame.layer not in {"macOS base", "Winux base"}:
        body.append(
            text(
                -34,
                -22,
                physical,
                min(15, 74 / len(physical)),
                color=MUTED if blank else INK,
                weight=600,
            )
        )
    if alternate:
        alternate = "1×" if alternate == "one-shot" else alternate
        body.append(
            text(
                34,
                -22,
                alternate,
                min(16, 84 / len(alternate)),
                color=INK,
                align="end",
                weight=650,
            )
        )
    lines = tap.splitlines()
    first = (3 if hold else 11) if len(lines) == 1 else 0
    for j, line in enumerate(lines):
        size = min(32 if len(lines) == 1 else 21, 126 / max(1, len(line)))
        body.append(
            text(0, first + 22 * j, line, size, color=INK, align="middle", weight=700)
        )
    if hold:
        body.append(
            text(
                0,
                24,
                hold,
                min(20, 118 / len(hold)),
                color=INK,
                align="middle",
                weight=600,
            )
        )
    return "".join(body + ["</g>"])


def draw(halves, physical, layers, frame, mobile):
    w, h = (520, 884) if mobile else (1200, 552)
    title = {
        "macOS base": "Base · macOS",
        "Winux base": "Base · Winux",
        "Super": "Super · ⌘⌥⌃",
        "Hyper": "Hyper · ⌘⌥⌃⇧",
    }.get(frame.layer, frame.layer)
    pad = 23 if mobile else 34
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        rect(0, 0, w, h, 0, DARK),
        text(pad, 32, "PIANTOR   /   36", 16, color=MUTED, mono=True, weight=650),
        text(pad, 79, title, 44 if mobile else 49, color=FACE, weight=720),
    ]
    if mobile:
        svg.append(text(pad, 117, frame.cue, 23, color=MINT, weight=600))
    else:
        svg.append(
            text(w - pad, 72, frame.cue, 29, color=MINT, align="end", weight=600)
        )
    scale = 4.0 if mobile else 4.95
    for side, positions in enumerate(halves):
        for index, (x, y, angle) in positions.items():
            inset = (32 if mobile else 35) + (x - 83) * scale
            cx = w - inset if side else inset
            top = (142 + 363 * side) if mobile else 106
            cy = top + (y - 43) * scale
            cap_scale = scale / 4.95
            svg.append(
                f'<g transform="translate({cx:.2f} {cy:.2f}) scale({cap_scale:.4f})">'
            )
            svg.append(
                keycap(
                    angle,
                    index,
                    physical[index],
                    layers[frame.layer][index],
                    frame,
                )
            )
            svg.append("</g>")
    return "".join(svg + ["</svg>"])


def main():
    halves = switches()
    physical, layers = maps()
    stills = HERE / "steps"
    stills.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        for mobile, stem in [(False, "layout"), (True, "layout-mobile")]:
            sequence = []
            for i, frame in enumerate(TOUR):
                png = Path(folder) / f"{stem}-{i}.png"
                subprocess.run(
                    ["rsvg-convert", "-o", str(png)],
                    input=draw(halves, physical, layers, frame, mobile).encode(),
                    check=True,
                )
                if i and frame.still and not mobile:
                    subprocess.run(
                        [
                            "magick",
                            str(png),
                            "-define",
                            "webp:lossless=true",
                            str(stills / f"{frame.still}.webp"),
                        ],
                        check=True,
                    )
                if i == 0:
                    subprocess.run(
                        [
                            "magick",
                            str(png),
                            "-define",
                            "webp:lossless=true",
                            str(HERE / f"{stem}.webp"),
                        ],
                        check=True,
                    )
                sequence.extend(["-delay", str(round(frame.seconds * 100)), str(png)])
            subprocess.run(
                [
                    "magick",
                    *sequence,
                    "+dither",
                    "-layers",
                    "Optimize",
                    "-loop",
                    "0",
                    str(HERE / f"{stem}.gif"),
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
