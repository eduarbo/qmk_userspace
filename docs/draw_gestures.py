#!/usr/bin/env python3
"""Render the two gesture tutorials with the artwork used by the reference maps."""

import argparse
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

sys.dont_write_bytecode = True
from cover.render import AMBER, DARK, FACE, MINT, MUTED, draw, maps, switches
from cover.tour import TAB, Frame
from layer_art import rect, text

DOCS = Path(__file__).resolve().parent
NS = "{http://www.w3.org/2000/svg}"
ET.register_namespace("", NS[1:-1])

# Each step keeps its physical keys and the cumulative text visible together.
SPACE, U, I = 31, 6, 7
THUMBS = {TAB: "Symbols", SPACE: "Shift"}
SPLIT = (
    ("Start on the letter layer.", "", {}, {}, 3),
    ("Hold Tab for Symbols.", "", {TAB: "Symbols"}, {}, 3.5),
    ("Keep Tab down. Hold Space for Shift.", "", THUMBS, {}, 4),
    ("Tap U for the opening brace.", "{", THUMBS, {U: "{"}, 4.5),
    ("Keep both held. Tap I to close.", "{}", THUMBS, {I: "}"}, 4.5),
    ("Release both thumbs.", "{}", {}, {}, 3.5),
)

RIGHT_CMD = {"right command": "Symbols"}
EXTRA_SHIFT = {**RIGHT_CMD, ";": "Shift"}
MACBOOK = (
    ("Hold right ⌘ for Symbols.", "", RIGHT_CMD, {}, 3.5),
    ("Tap ; for the tilde accent.", "", RIGHT_CMD, {";": "˜"}, 4),
    ("Release right ⌘.", "", {}, {}, 3),
    ("Tap N to finish the letter.", "ñ", {}, {"N": "ñ"}, 4.5),
    ("Hold right ⌘ again.", "ñ", RIGHT_CMD, {}, 3),
    ("Hold ; for the extra Shift.", "ñ", EXTRA_SHIFT, {}, 4),
    ("Keep both held. Tap B.", "ñ_", EXTRA_SHIFT, {"B": "_"}, 4.5),
    ("Release both keys.", "ñ_", {}, {}, 3.5),
)


def split_frame(board, step, mobile):
    cue, typed, held, tapped, _ = step
    layer = "Symbols" if TAB in held else "macOS base"
    frame = Frame(layer, cue, tuple(held), next(iter(tapped), None))
    return draw(
        *board,
        frame,
        mobile,
        heading="Braces",
        typed=typed,
        active_roles={**held, **tapped},
    )


def laptop_frame(source, step, mobile):
    cue, typed, held, tapped, _ = step
    w, h = (520, 340) if mobile else (1200, 451)
    pad = 23 if mobile else 34
    board = deepcopy(source)
    seen = set()
    for key in board.findall(NS + "g"):
        position = key.get("data-position")
        if position == "command" and key.get("data-hold") == "Symbols":
            position = "right command"
        if position in held or position in tapped:
            seen.add(position)
            key.find(f"{NS}rect[@class='face']").set(
                "fill", MINT if position in held else AMBER
            )
            for old in key.findall(NS + "text"):
                key.remove(old)
            name = "R ⌘" if position == "right command" else position
            key.append(ET.fromstring(text(0, 1, name, 20, weight=700, align="middle")))
            key.append(
                ET.fromstring(
                    text(
                        0, 19, (held | tapped)[position], 14, weight=650, align="middle"
                    )
                )
            )
    if seen != held.keys() | tapped.keys():
        raise ValueError(
            f"Missing gesture keys on the MacBook: {(held.keys() | tapped.keys()) - seen}"
        )
    transform = (
        "translate(18 146) scale(.555)" if mobile else "translate(34 116) scale(1.3)"
    )
    items = [
        f'<svg xmlns="{NS[1:-1]}" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        rect(0, 0, w, h, 0, DARK),
        text(
            pad, 32, "MACBOOK   /   KARABINER", 16, color=MUTED, mono=True, weight=650
        ),
        text(pad, 79, "MacBook rollover", 43 if mobile else 49, color=FACE, weight=720),
        text(
            pad if mobile else w - pad,
            117 if mobile else 72,
            cue,
            23 if mobile else 29,
            align="start" if mobile else "end",
            color=MINT,
            weight=600,
        ),
        f'<g transform="{transform}">{ET.tostring(board, encoding="unicode")}</g>',
    ]
    if typed:
        items.append(
            text(
                w - pad, 32, "Typed   " + typed, 21, color=FACE, align="end", weight=650
            )
        )
    if mobile:
        # The full ANSI keyboard stays in view. Repeat the active chord at reading size.
        if held:
            names = ["right ⌘" if key == "right command" else key for key in held]
            items.append(
                text(
                    pad, 316, "Hold   " + " + ".join(names), 23, color=MINT, weight=650
                )
            )
        if tapped:
            items.append(
                text(
                    w - pad,
                    316,
                    "Tap   " + next(iter(tapped)),
                    23,
                    color=AMBER,
                    align="end",
                    weight=650,
                )
            )
    return "".join(items + ["</svg>"])


def write_movies(filename, render, board, timeline):
    with tempfile.TemporaryDirectory() as temp:
        for mobile, suffix in [(False, ""), (True, "-mobile")]:
            sequence = []
            for index, step in enumerate(timeline):
                png = Path(temp) / f"{index}.png"
                subprocess.run(
                    ["rsvg-convert", "-o", str(png)],
                    input=render(board, step, mobile).encode(),
                    check=True,
                )
                sequence.extend(["-delay", str(round(step[-1] * 100)), str(png)])
            destination = DOCS / "gestures" / f"{filename}{suffix}.gif"
            subprocess.run(
                [
                    "magick",
                    *sequence,
                    "+dither",
                    "-layers",
                    "Optimize",
                    "-loop",
                    "0",
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
    macbook = ET.parse(args.macbook_svg).find(f".//{NS}g[@id='board']")
    if macbook is None:
        raise ValueError(
            "Regenerate the MacBook reference with npm run docs in macos/karabiner."
        )
    write_movies("split-braces", split_frame, (switches(), *maps()), SPLIT)
    write_movies("macbook-symbols", laptop_frame, macbook, MACBOOK)


if __name__ == "__main__":
    main()
