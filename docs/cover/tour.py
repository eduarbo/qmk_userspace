"""Typeset the live key legends on the projected Blender keycaps and encode the loop."""

import base64
import subprocess
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
INK = "#1a302e"
PAPER = "#f6f0e2"
MINT = "#a5edc3"
APRICOT = "#ffb677"
NS = "{http://www.w3.org/2000/svg}"
# Scene title, layer, ordered thumb holds (QMK index and role), tap, output.
SCENES = [
    ("Meet the thumbs", "Base", [], None, ""),
    ("Open Spotlight", "Base", [(33, "Cmd")], 31, "⌘ Space"),
    ("Type a capital", "Base", [(31, "Shift")], 10, "A"),
    ("Move down a line", "Symbols", [(34, "Symbols")], 16, "↓"),
    ("Go back a page", "Super", [(30, "Super")], 12, "⌘ ["),
    ("Mute the audio", "F-Keys", [(30, "Super"), (35, "F-Keys")], 17, "Mute"),
]


def read_legends():
    layers = {}
    for name, slug in [
        ("Base", "macos"),
        ("Symbols", "symbols"),
        ("Super", "super"),
        ("F-Keys", "fkeys"),
    ]:
        caps = {}
        for node in ET.parse(HERE.parent / "layers" / f"{slug}.svg").iter(NS + "g"):
            if "data-position" not in node.attrib:
                continue
            i = int(node.attrib["id"].removeprefix("key-"))
            # The centered text is the output legend. Corner labels are lookup aids.
            lines = [
                t.text
                for t in node.findall(NS + "text")
                if t.get("x") == "33.5" and t.text
            ]
            caps[i] = (node.attrib["data-position"], lines)
        assert set(caps) == set(range(36))
        layers[name] = caps
    return layers


def text(
    x,
    y,
    words,
    size,
    color,
    weight=600,
    anchor="start",
    family="Arial, sans-serif",
    italic=False,
):
    style = ' font-style="italic"' if italic else ""
    return (
        f'<text x="{x:g}" y="{y:g}" fill="{color}" font-family="{family}" font-size="{size:g}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{style}>{escape(words)}</text>'
    )


def rect(x, y, w, h, r, fill, extra=""):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{r:g}" fill="{fill}" {extra}/>'


def keyface(index, anchor, layer, layers, held, tapped):
    x, y, angle = anchor
    physical = layers["Base"][index][0]
    active = index in held or index == tapped
    fill = MINT if index in held else APRICOT
    body = [f'<g transform="translate({x:.2f} {y:.2f}) rotate({angle:.2f})">']
    if active:
        body.append(
            rect(-39, -34, 78, 69, 8, fill, 'stroke="#18362e" stroke-width="3"')
        )
    if index >= 30:
        second = held.get(index, layers[layer][index][1][-1])
        if index == tapped:
            second = "Tap"
        body.extend(
            [
                text(
                    0, -1, physical, 26 if len(physical) < 5 else 22, INK, 700, "middle"
                ),
                text(
                    0,
                    20,
                    second,
                    min(22, 137 / max(1, len(second))),
                    INK,
                    600,
                    "middle",
                ),
            ]
        )
    else:
        lines = layers[layer][index][1]
        # The Super overview shows the browser bindings implemented in firmware.
        detail = layer != "Base" and (layer != "Super" or physical in "ERTSDFG")
        if detail and lines:
            # Symbols accent taps and the navigation/media actions have their usual QWERTY key above.
            action = " ".join(s for s in lines if s != "Shift")
            action = {
                "Play Pause": "Play",
                "Mission Control": "Mission",
                "Caps Word": "Caps W.",
                "Dev Tools": "Tools",
                "Inspect": "Insp.",
                "Forward": "Fwd",
                "Pause JS": "Pause",
                "Prev tab": "←Tab",
                "Next tab": "Tab→",
                "Fast fwd": "Fwd",
            }.get(action, action)
            size = min(30, 133 / max(len(action), 1))
            body.extend(
                [
                    text(0, -10, physical, 20, INK, 600, "middle"),
                    text(0, 20, action, size, INK, 750, "middle"),
                ]
            )
        else:
            body.append(text(0, 10, physical, 32, INK, 650, "middle"))
    return "".join(body + ["</g>"])


def chord_label(x, y, role, value, phone):
    body = []
    if role in {"HOLD", "TAP"}:
        color = MINT if role == "HOLD" else APRICOT
        body.append(
            rect(x, y - 14, 15, 15, 4, color, 'stroke="#547261" stroke-width="1"')
        )
    body.append(
        text(x + (21 if body else 0), y, role, 14 if phone else 15, "#53645e", 700)
    )
    body.append(text(x, y + 29, value, 25 if phone else 28, INK, 700))
    return "".join(body)


def frame(phone, layers, hands, anchors, scene_index, held_count, pressed):
    title, target_layer, chord, tap, output = SCENES[scene_index]
    held = dict(chord[:held_count])
    layer = "Super" if target_layer == "F-Keys" and held_count == 1 else target_layer
    w, h, footer = (520, 928, 778) if phone else (1280, 680, 548)
    top = 94 if phone else 93
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}">',
        '<defs><pattern id="grain" width="12" height="12" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".65" fill="#c0c9ac" opacity=".15"/></pattern></defs>',
        rect(0, 0, w, footer, 0, "#263d3d"),
        rect(0, top, w, footer - top, 0, "url(#grain)"),
    ]
    pad = 24 if phone else 38
    svg.extend(
        [
            text(
                pad,
                58 if phone else 67,
                "Piantor",
                55 if phone else 66,
                PAPER,
                500,
                family="Georgia, serif",
                italic=True,
            ),
            text(
                w - pad,
                32 if phone else 37,
                "36 KEYS  /  QMK",
                15 if phone else 18,
                MINT,
                700,
                "end",
            ),
            text(
                w - pad,
                60 if phone else 68,
                "macOS  ·  " + layer,
                21 if phone else 24,
                PAPER,
                600,
                "end",
            ),
            rect(pad, top - 10, w - 2 * pad, 1, 0, "#688079"),
        ]
    )
    if phone:
        transforms = {"left": (32, 88, 0.63), "right": (32, 429, 0.63)}
    else:
        transforms = {"left": (19, 92, 0.85), "right": (648, 92, 0.85)}
    for side, (x, y, scale) in transforms.items():
        svg.append(f'<g transform="translate({x} {y}) scale({scale})">')
        svg.append(f'<image width="720" height="554" xlink:href="{hands[side]}"/>')
        for i, anchor in anchors[side].items():
            svg.append(
                keyface(i, anchor, layer, layers, held, tap if pressed else None)
            )
        svg.append("</g>")
    svg.append(rect(0, footer, w, h - footer, 0, PAPER))
    bar_x, bar_w = pad, (w - 2 * pad) / len(SCENES)
    for i in range(len(SCENES)):
        svg.append(
            rect(
                bar_x + i * bar_w,
                footer + 1,
                bar_w - 4,
                4,
                2,
                "#ce7246" if i == scene_index else "#d2d6c7",
            )
        )
    svg.append(
        text(
            pad,
            footer + (48 if phone else 61),
            title,
            34 if phone else 44,
            INK,
            600,
            family="Georgia, serif",
        )
    )
    if not chord:
        if phone:
            svg.extend(
                [
                    text(pad, footer + 89, "Upper legend · tap", 23, INK),
                    text(pad, footer + 119, "Lower legend · hold", 23, INK),
                ]
            )
        else:
            svg.append(
                text(
                    pad,
                    footer + 103,
                    "Upper legend · tap     /     Lower legend · hold",
                    24,
                    INK,
                    500,
                )
            )
    else:
        physical = layers["Base"]
        hold_text = " then ".join(physical[i][0] for i, _ in chord)
        mod = " + ".join(role for _, role in chord)
        if not phone:
            svg.append(
                text(
                    pad,
                    footer + 104,
                    {"Super": "Super  ·  ⌘ ⌥ ⌃", "F-Keys": "Super → F-Keys"}.get(
                        layer, mod
                    ),
                    22,
                    "#445b54",
                )
            )
        xs = [pad, 243, 360] if phone else [590, 895, 1055]
        base_y = footer + (84 if phone else 53)
        for x, role, value in zip(
            xs,
            ["HOLD", "TAP", "OUTPUT"],
            [hold_text, physical[tap][0], output if pressed else "…"],
        ):
            svg.append(chord_label(x, base_y, role, value, phone))
    return "".join(svg + ["</svg>"])


def animate(folder, anchors):
    layers = read_legends()
    hands = {}
    for side in anchors:
        png = (folder / f"{side}.png").read_bytes()
        hands[side] = "data:image/png;base64," + base64.b64encode(png).decode()
    for phone, stem in [(False, "layout"), (True, "layout-mobile")]:
        frames = []
        for index, (_, _, chord, _, _) in enumerate(SCENES):
            beats = (
                [(0, False, 330)]
                if not chord
                else [
                    *((n, False, 70) for n in range(1, len(chord) + 1)),
                    (len(chord), True, 260),
                ]
            )
            for n, pressed, delay in beats:
                path = folder / f"{stem}-{index}-{n}-{int(pressed)}.png"
                svg = frame(phone, layers, hands, anchors, index, n, pressed)
                subprocess.run(
                    ["rsvg-convert", "-o", str(path)], input=svg.encode(), check=True
                )
                if not frames:
                    subprocess.run(
                        [
                            "magick",
                            str(path),
                            "-strip",
                            "-quality",
                            "93",
                            str(HERE / f"{stem}.webp"),
                        ],
                        check=True,
                    )
                frames.extend(["-delay", str(delay), str(path)])
        palette = folder / f"{stem}-palette.png"
        subprocess.run(
            [
                "magick",
                *frames[2::3],
                "-resize",
                "40%",
                "-append",
                "+dither",
                "-colors",
                "256",
                "-unique-colors",
                str(palette),
            ],
            check=True,
        )
        subprocess.run(
            [
                "magick",
                *frames,
                "-dither",
                "FloydSteinberg",
                "-remap",
                str(palette),
                "-layers",
                "Optimize",
                "-loop",
                "0",
                str(HERE / f"{stem}.gif"),
            ],
            check=True,
        )
