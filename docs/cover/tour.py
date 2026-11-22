"""Typeset the live key legends on the projected Blender keycaps and encode the loop."""

import base64
import subprocess
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from draw_layout import read_keymap
from layer_art import legend

HERE = Path(__file__).resolve().parent
INK = "#1a302e"
PAPER = "#f6f0e2"
MINT = "#a5edc3"
APRICOT = "#ffb677"
# Short references use the order of LAYOUT_split_3x5_3. Each recipe starts on Base.
# title, still filename, holds (position, role, resulting layer), tap, result.
SCENES = [
    ("Open Raycast", "raycast", [], 35, "Raycast opens"),
    ("Type a capital A", "capital", [(31, "Shift", "Base")], 10, "A"),
    ("Move the cursor down", "cursor", [(34, "Symbols", "Symbols")], 16, "↓  Down"),
    ("Go back in the browser", "back", [(30, "Super", "Super")], 12, "⌘ [  ·  Back"),
    (
        "Mute the audio",
        "mute",
        [(30, "Super", "Super"), (35, "F-Keys", "F-Keys")],
        17,
        "Mute",
    ),
]
HOLD_DELAY, RESULT_DELAY = 380, 620  # GIF centiseconds


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


def keyface(index, anchor, layer, keymap, physical, held, tapped):
    x, y, angle = anchor
    key = legend(keymap[layer][index])
    body = [f'<g transform="translate({x:.2f} {y:.2f}) rotate({angle:.2f})">']
    active = index in held or index == tapped
    if active:
        fill = MINT if index in held else APRICOT
        body.append(
            rect(-39, -34, 78, 69, 8, fill, 'stroke="#18362e" stroke-width="3"')
        )

    # Every key face uses the same tap, hold and shifted legends as the reference map.
    # The step strip below always names the physical key to press.
    value = key["t"]
    secondary = key.get("h", "")
    corner = key.get("s", "")
    ink = INK if active or (not held and tapped is None) else "#4a5651"
    if index in held:
        value, secondary, corner = physical, held[index], ""
    elif index == tapped:
        secondary = value if physical != value else ""
        value, corner = physical, ""
    if not value and layer == "Super":
        # Super passes this key to the host with Cmd+Option+Control held.
        value = keymap["Base"][index]
    show_position = layer != "Base" and index not in held and physical != value
    if show_position:
        body.append(text(-33, -18, physical, min(17, 80 / len(physical)), ink, 650))
    if corner == "one-shot":
        corner = "1×"
    if corner:
        body.append(text(33, -18, corner, min(17, 88 / len(corner)), ink, 600, "end"))
    lines = value.splitlines()
    first_y = (4 if secondary else 12) if len(lines) < 2 else (-3 if corner else 0)
    if len(lines) > 1 and show_position:
        first_y = 5
    if secondary and corner:
        first_y = 5
    for j, line in enumerate(lines):
        body.append(
            text(
                0,
                first_y + j * 21,
                line,
                min(32 if len(lines) == 1 else 21, 132 / max(len(line), 1)),
                ink,
                700,
                "middle",
            )
        )
    if secondary:
        body.append(
            text(0, 25, secondary, min(21, 124 / len(secondary)), ink, 600, "middle")
        )
    return "".join(body + ["</g>"])


def step_card(x, y, width, label, value, state, phone):
    colors = {"hold": MINT, "tap": APRICOT, "result": INK, "waiting": "#e5e6da"}
    ink = PAPER if state == "result" else "#52635b" if state == "waiting" else INK
    wide = not phone
    return "".join(
        [
            rect(x, y, width, 78 if wide else 70, 9, colors[state]),
            text(x + 12, y + 23, label, 17 if wide else 16, ink, 700),
            text(
                x + 12,
                y + (59 if wide else 52),
                value,
                min(33 if wide else 29, (width - 20) * 1.67 / max(len(value), 1)),
                ink,
                700,
            ),
        ]
    )


def frame(phone, physical, keymap, hands, anchors, scene, count, pressed):
    idle = scene is None
    title, _, holds, tap, result = scene or ("Tap or hold a thumb", "", [], None, "")
    acquired = holds[:count]
    held = {i: role for i, role, _ in acquired}
    layer = acquired[-1][2] if acquired else "Base"
    w, h, footer = (520, 976, 778) if phone else (1280, 735, 548)
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
                keyface(
                    i,
                    anchor,
                    layer,
                    keymap,
                    physical[i],
                    held,
                    tap if pressed else None,
                )
            )
        svg.append("</g>")
    svg.append(rect(0, footer, w, h - footer, 0, PAPER))
    svg.append(
        text(
            pad,
            footer + 53,
            title,
            37 if phone else 46,
            INK,
            600,
            family="Georgia, serif",
        )
    )
    if idle:
        svg.append(
            text(
                pad, footer + 100, "Upper thumb legend · tap", 26 if phone else 30, INK
            )
        )
        svg.append(
            text(
                pad, footer + 140, "Lower thumb legend · hold", 26 if phone else 30, INK
            )
        )
    else:
        cards = [
            (
                f"{n+1}  HOLD · {role.upper()}",
                physical[i],
                "hold" if n < count else "waiting",
            )
            for n, (i, role, _) in enumerate(holds)
        ]
        cards.append(
            (f"{len(holds)+1}  TAP", physical[tap], "tap" if pressed else "waiting")
        )
        cards.append(
            ("RESULT", result if pressed else "…", "result" if pressed else "waiting")
        )
        # Give the result its own line on phones so a three-key chord still reads at a glance.
        gap = 10
        cols = len(cards) - 1 if phone else len(cards)
        width = (w - 2 * pad - (cols - 1) * gap) / cols
        for n, (label, value, state) in enumerate(cards):
            x = pad + n * (width + gap)
            if phone and n == len(cards) - 1:
                svg.append(text(pad, footer + 169, "RESULT", 16, INK, 700))
                svg.append(text(pad + 82, footer + 174, value, 30, INK, 700))
            else:
                svg.append(step_card(x, footer + 68, width, label, value, state, phone))
    return "".join(svg + ["</svg>"])


def animate(folder, anchors):
    physical, keymap = read_keymap()
    keymap["Base"] = keymap["macOS base"]
    hands = {}
    for side in anchors:
        png = (folder / f"{side}.png").read_bytes()
        hands[side] = "data:image/png;base64," + base64.b64encode(png).decode()
    stills = HERE / "steps"
    stills.mkdir(exist_ok=True)
    for phone, stem in [(False, "layout"), (True, "layout-mobile")]:
        frames = []
        for index, scene in enumerate([None, *SCENES]):
            beats = [(0, False, 430)]
            if scene:
                holds = scene[2]
                beats = [(0, False, 260)] + [
                    (n, False, HOLD_DELAY) for n in range(1, len(holds) + 1)
                ]
                beats.append((len(holds), True, RESULT_DELAY))
            for n, pressed, delay in beats:
                path = folder / f"{stem}-{index}-{n}-{int(pressed)}.png"
                svg = frame(phone, physical, keymap, hands, anchors, scene, n, pressed)
                subprocess.run(
                    ["rsvg-convert", "-o", str(path)], input=svg.encode(), check=True
                )
                still = None
                if not scene:
                    still = HERE / f"{stem}.webp"
                elif pressed and not phone:
                    still = stills / f"{scene[1]}.webp"
                if still:
                    subprocess.run(
                        ["magick", str(path), "-strip", "-quality", "93", str(still)],
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
