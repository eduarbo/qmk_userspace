#!/usr/bin/env python3
"""Draw the two README GIFs from the same key groups as the static maps."""

import argparse
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path
from textwrap import wrap
from xml.etree import ElementTree as ET

from layer_art import INK, MINT, rect, text

DOCS = Path(__file__).resolve().parent
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
ORANGE = "#ffbb82"
LIGHT = "#f9f1dd"
SECONDARY = "#adcbc3"

# Seconds, instruction, output so far, held physical keys and optional tapped key.
# Each active key carries its physical legend and its job in this particular gesture.
SPLIT = [
    (1.65, "Start on the letter layer.", "", {}, {}),
    (1.70, "Hold the Tab thumb for Symbols.", "", {"Tab": "Symbols"}, {}),
    (
        1.80,
        "Keep Tab down. Hold A for Shift.",
        "",
        {"Tab": "Symbols", "A": "Shift"},
        {},
    ),
    (
        1.55,
        "Tap U for the opening brace.",
        "{",
        {"Tab": "Symbols", "A": "Shift"},
        {"U": "{"},
    ),
    (
        1.55,
        "Keep both held and tap I to close.",
        "{}",
        {"Tab": "Symbols", "A": "Shift"},
        {"I": "}"},
    ),
    (2.05, "Release A and Tab. Back to letters.", "{}", {}, {}),
]
LAPTOP = [
    (1.45, "Hold right Command for Symbols.", "", {"right command": "Symbols"}, {}),
    (
        1.75,
        "Tap semicolon for the tilde dead key.",
        "",
        {"right command": "Symbols"},
        {";": "˜"},
    ),
    (1.45, "Release right Command before the letter.", "", {}, {}),
    (1.55, "Tap N to finish the letter.", "ñ", {}, {"N": "ñ"}),
    (
        1.50,
        "Hold right Command for Symbols again.",
        "ñ",
        {"right command": "Symbols"},
        {},
    ),
    (
        1.85,
        "This time, hold semicolon for Shift.",
        "ñ",
        {"right command": "Symbols", ";": "Shift"},
        {},
    ),
    (
        1.65,
        "Keep both held and tap B.",
        "ñ_",
        {"right command": "Symbols", ";": "Shift"},
        {"B": "_"},
    ),
    (1.90, "Release both keys. Back to letters.", "ñ_", {}, {}),
]


def key_nodes(board):
    return [node for node in board.iter() if node.get("id", "").startswith("key-")]


def gesture_board(source, held, tapped):
    board = deepcopy(source)
    seen = set()
    for key in key_nodes(board):
        position = key.attrib["data-position"]
        if key.get("data-hold") == "Symbols" and position == "command":
            position = "right command"
        face = key.find(f"{{{NS}}}rect[@class='face']")
        x, y, w, h = (float(face.get(k)) for k in ("x", "y", "width", "height"))
        cx, cy = x + w / 2, y + h / 2
        for child in list(key):
            if child.tag == f"{{{NS}}}text" or (
                child.tag == f"{{{NS}}}rect" and child.get("height") == "2"
            ):
                key.remove(child)
        active = position in held or position in tapped
        color = MINT if position in held else ORANGE
        face.set("fill", color if active else "#dce2d3")
        short = {
            "right command": "R ⌘",
            "command": "L ⌘",
            "option": "⌥",
            "caps lock": "Caps",
            "control": "Ctrl",
            "space": "Space",
        }.get(position, position)
        if active:
            seen.add(position)
            face.set("stroke", INK)
            face.set("stroke-width", "2")
            role = held.get(position) or tapped[position]
            key.append(
                ET.fromstring(text(cx, cy + 1, short, 18, align="middle", weight=750))
            )
            key.append(
                ET.fromstring(text(cx, cy + 17, role, 13, align="middle", weight=700))
            )
            if position in tapped:
                key.append(
                    ET.fromstring(
                        rect(
                            x + 5,
                            y + 4,
                            w - 10,
                            h - 8,
                            4,
                            "none",
                            'stroke="#8a471b" stroke-dasharray="3 3"',
                        )
                    )
                )
        else:
            size = min(19, h * 0.67, w * 1.3 / max(1, len(short)))
            key.append(
                ET.fromstring(
                    text(cx, cy + size * 0.34, short, size, align="middle", weight=650)
                )
            )
    if seen != held.keys() | tapped.keys():
        raise ValueError(
            f"Gesture keys missing from the board: {(held.keys() | tapped.keys()) - seen}"
        )
    return ET.tostring(board, encoding="unicode")


def movie_frame(title, platform, timeline, step, source, is_laptop):
    _, instruction, output, held, tapped = timeline[step]
    right = 918
    body = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="552" viewBox="0 0 960 552">',
        (
            '<defs><pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse">'
            '<circle cx="2" cy="2" r="1" fill="#365350"/></pattern></defs>'
        ),
        rect(0, 0, 960, 552, 0, INK),
        rect(0, 135, 960, 307, 0, "url(#grid)"),
        text(32, 32, platform, 14, mono=True, weight=650, color=SECONDARY),
        text(30, 91, title, 46, color=LIGHT, weight=750),
        rect(732, 20, 196, 86, 12, "#203e42", 'stroke="#53716c"'),
        text(748, 43, "OUTPUT", 12, color=SECONDARY, mono=True, weight=650),
        text(747, 87, output, 39, mono=True, color=MINT, weight=700),
        rect(750 + len(output) * 24, 56, 2.5, 34, 1, MINT),
        '<path d="M32 121h896" stroke="#58716b"/>',
        f'<g transform="translate(0 {38 if is_laptop else 8})">',
        gesture_board(source, held, tapped),
        "</g>",
        text(33, 478, instruction, 24, color=LIGHT, weight=650),
        rect(33, 502, 17, 17, 5, MINT),
        text(60, 516, "Hold", 16, color=LIGHT),
        rect(128, 502, 17, 17, 5, ORANGE),
        text(155, 516, "Tap", 16, color=LIGHT),
    ]
    width = 22
    for i in range(len(timeline)):
        body.append(
            rect(
                right - (len(timeline) - i) * (width + 5),
                509,
                width,
                5,
                2.5,
                MINT if i <= step else "#42605d",
            )
        )
    body.append("</svg>")
    return "\n".join(body)


def phone_frame(title, platform, timeline, step, source, is_laptop):
    _, instruction, output, held, tapped = timeline[step]
    if is_laptop:
        keys = ["right command", ";", "B" if step >= 4 else "N"]
    else:
        keys = ["Tab", "A", "I" if step >= 4 else "U"]
    body = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="470" height="464" viewBox="0 0 470 464">',
        rect(0, 0, 470, 464, 0, INK),
        text(18, 26, platform, 13, mono=True, color=SECONDARY),
        text(
            17,
            61,
            "Braces  { }" if not is_laptop else title,
            31,
            color=LIGHT,
            weight=700,
        ),
        rect(347, 14, 104, 56, 7, "#254347"),
        text(358, 31, "OUTPUT", 10, mono=True, color=SECONDARY),
        text(357, 58, output, 25, mono=True, color=MINT, weight=700),
        rect(359 + len(output) * 15, 39, 2, 22, 1, MINT),
        f'<g transform="translate(7 {31 if is_laptop else 22}) scale(.475)">{gesture_board(source, held, tapped)}</g>',
    ]
    for i, key in enumerate(keys):
        x = 18 + 146 * i
        state = "HOLD" if key in held else "TAP" if key in tapped else ""
        color = MINT if key in held else ORANGE if key in tapped else "#314c50"
        ink = INK if state else LIGHT
        name = "Right ⌘" if key == "right command" else key
        body += [
            rect(x, 242, 139, 65, 8, color),
            text(x + 11, 261, state, 12, color=ink, mono=True, weight=650),
            text(x + 11, 293, name, 25, color=ink, weight=700),
        ]
    for i, line in enumerate(wrap(instruction, 32)):
        body.append(text(18, 350 + i * 28, line, 21, color=LIGHT, weight=650))
    body.append(
        text(18, 427, f"{step + 1} / {len(timeline)}", 14, color=SECONDARY, mono=True)
    )
    for i in range(len(timeline)):
        body.append(
            rect(
                445 - (len(timeline) - i) * 18,
                418,
                14,
                4,
                2,
                MINT if i <= step else "#42605d",
            )
        )
    return "\n".join(body + ["</svg>"])


def draw_movie(filename, svg, title, platform, timeline, is_laptop=False):
    source = ET.parse(svg).find(f".//{{{NS}}}g[@id='board']")
    if source is None:
        raise ValueError(f"{svg} has no board group; regenerate its static map first.")
    with tempfile.TemporaryDirectory() as temp:
        for render, destination in [
            (movie_frame, filename),
            (phone_frame, filename.with_name(filename.stem + "-mobile.gif")),
        ]:
            frames = []
            for step, (seconds, *_) in enumerate(timeline):
                contents = render(title, platform, timeline, step, source, is_laptop)
                path = Path(temp) / f"frame-{step:02d}.png"
                subprocess.run(
                    ["rsvg-convert", "-o", str(path)],
                    input=contents.encode(),
                    check=True,
                )
                frames.extend(["-delay", str(round(seconds * 100)), str(path)])
            subprocess.run(
                [
                    "magick",
                    *frames,
                    "-loop",
                    "0",
                    "-layers",
                    "Optimize",
                    str(destination),
                ],
                check=True,
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--macbook-svg",
        type=Path,
        default=DOCS.parent.parent / "dotfiles/macos/karabiner/docs/macbook.svg",
    )
    args = parser.parse_args()
    target = DOCS / "gestures"
    target.mkdir(exist_ok=True)
    draw_movie(
        target / "split-braces.gif",
        DOCS / "layers/macos.svg",
        "Type a pair of braces",
        "QMK  /  PIANTOR + CORNE",
        SPLIT,
    )
    draw_movie(
        target / "macbook-symbols.gif",
        args.macbook_svg,
        "Type ñ and _",
        "KARABINER-ELEMENTS  /  MACBOOK",
        LAPTOP,
        is_laptop=True,
    )


if __name__ == "__main__":
    main()
