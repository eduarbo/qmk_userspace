#!/usr/bin/env python3
"""Draw the layer diagrams in docs/layers from users/eduarbo/wrappers.h.

Run from anywhere: `python3 docs/draw_layout.py`. It needs `uvx` to run a pinned
keymap-drawer and reads the Piantor geometry from $QMK_HOME (default
~/dev/eduarbo/qmk_firmware), falling back to the QMK API when that is missing.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

KEYMAP_DRAWER = "keymap-drawer==0.23.0"
ROOT = Path(__file__).resolve().parent.parent
WRAPPERS = ROOT / "users/eduarbo/wrappers.h"
OUTPUT = ROOT / "docs/layers"
QMK_HOME = Path(os.environ.get("QMK_HOME", Path.home() / "dev/eduarbo/qmk_firmware"))
INFO_JSON = QMK_HOME / "keyboards/beekeeb/piantor/keyboard.json"

ROWS = ["L1", "R1", "L2", "R2", "L3", "R3"]  # LAYOUT_split_3x5_3 key order
THUMB_L, THUMB_R = 30, 33  # first index of each thumb cluster (outer to inner on the left)

LABELS = {
    "KC_SCLN": ";", "KC_COMM": ",", "KC_DOT": ".", "KC_BSPC": "⌫",
    "KC_EQL": "=", "KC_MINS": "-", "KC_BSLS": "\\", "KC_LBRC": "[", "KC_RBRC": "]",
    "KC_SLSH": "/", "KC_GRV": "`", "KC_QUOT": "'",
    "KC_LEFT": "←", "KC_DOWN": "↓", "KC_UP": "↑", "KC_RIGHT": "→",
    "KC_PGUP": {"t": "PgUp", "s": "Home"}, "KC_PGDN": {"t": "PgDn", "s": "End"},
    "KC_ESC": "Esc", "KC_SPC": "Space", "KC_ENT": "Return",
    "KC_LALT": "Alt", "KC_LSFT": "Shift", "KC_RSFT": "Shift",
    "KC_PSCR": "PrtSc", "KC_SCRL": "ScrLk", "KC_PAUS": "Pause",
    "KC_VOLU": "Vol+", "KC_VOLD": "Vol−", "KC_MUTE": "Mute",
    "KC_MRWD": "Prev", "KC_MPLY": "Play", "KC_MFFD": "Next",
    "KC_BRID": "Bright −", "KC_BRIU": "Bright +", "KC_MCTL": "Mission\nControl",
    "ACUTE_LSFT": {"t": "´", "h": "Shift"}, "TILDE_LSFT": {"t": "˜", "h": "Shift"},
    "CW_TOGG": "Caps\nWord",
    "ESC_SUPR": {"t": "Esc", "h": "Super"}, "SPC_LSFT": {"t": "Space", "h": "Shift"},
    "ENT_RGUI": {"t": "Return", "h": "Cmd"}, "ENT_RCTL": {"t": "Return", "h": "Ctrl"},
    "TAB_SYMB": {"t": "Tab", "h": "Symbols"},
    "F16_RCTL": {"t": "F16", "h": "Ctrl"}, "F16_RGUI": {"t": "F16", "h": "Win"},
    "DB_TOGG": "Debug", "QK_RBT": "Reboot", "EE_CLR": "Clear\nsettings", "QK_BOOT": "Boot\nloader",
    "TG_BASE": "macOS\n⇄ Winux", "TG_GAME": "Gamepad", "XXXXXXX": "",
}

# Super is a chord, not a QMK layer: QMK emits E/R/T/S/D/F/G (process_records.c),
# Karabiner's superLayer.ts maps Q/A/Z/X/C/V/B, and the rest are app hotkeys.
SUPER = [
    {"t": "Screen\nshot", "s": "⇧⌘3"}, "Mic", {"t": "Dev\nTools", "s": "⌥⌘I"},
    {"t": "Inspect", "s": "⇧⌘C"}, {"t": "Pause\nJS", "s": "⌘\\"},
    "Sound\noutput", "Bitwarden", "ChatGPT", "Clipboard", "",
    {"t": "Area\nshot", "s": "⇧⌘4"}, {"t": "Prev\ntab", "s": "⇧⌃⇥"}, {"t": "Back", "s": "⌘["},
    {"t": "Forward", "s": "⌘]"}, {"t": "Next\ntab", "s": "⌃⇥"},
    "Window\n←½", "Next\nscreen", "Maximize", "Window\n→½", "Window\ngrid",
    {"t": "Record", "s": "⇧⌘5"}, {"t": "App\nwindows", "s": "⌃↓"},
    {"t": "Next\nwindow", "s": "⌘`"}, {"t": "Next\napp", "s": "⌘⇥"},
    {"t": "Mission\nControl", "s": "⌃↑"},
    "", "Emoji", "Snippets", "Actions", "",
    {"t": "Super", "type": "held"}, {"t": "F16", "h": "F-Keys"}, {"t": "⌘", "s": "one-shot", "h": "Adjust"},
    {"t": "⌘", "s": "one-shot", "h": "Adjust"}, {"t": "⌥", "s": "one-shot", "h": "Hyper"},
    {"t": "⌃", "s": "one-shot", "h": "F-Keys"},
]

# (title, slug, block prefix, thumb blocks, thumb overrides by index)
LAYERS = [
    ("macOS base", "macos", "QWERTY", ("BASE_MAC_MODS_L", "BASE_MAC_MODS_R"), {}),
    ("Winux base", "winux", "QWERTY", ("BASE_MODS_L", "BASE_MODS_R"), {}),
    ("Symbols", "symbols", "SYMBOLS", ("SYMBOLS_MODS_L", "SYMBOLS_MODS_R"), {
        30: {"t": "⇧ Esc", "h": "Hyper"}, 31: {"t": "⇧ Space", "h": "Shift"},
        32: {"t": "⌘ Return", "h": "Cmd"}, 33: {"t": "⌘ Return", "h": "Cmd"},
        34: {"t": "Symbols", "type": "held"},
    }),
    ("Super", "super", None, None, {}),
    ("F-Keys", "fkeys", "F_KEYS", ("F_KEYS_MODS_L", "F_KEYS_MODS_R"), {
        30: {"t": "Super", "type": "held"}, 35: {"t": "F-Keys", "type": "held"},
    }),
    ("Adjust", "adjust", "ADJUST", ("ADJUST_MODS_L", "ADJUST_MODS_R"), {
        30: {"t": "Super", "type": "held"}, 32: {"t": "Return", "type": "held"},
    }),
    ("Gamepad", "gamepad", "GAMEPAD", ("GAMEPAD_MODS_L", "GAMEPAD_MODS_R"), {}),
]


def parse_wrappers(source: str) -> dict[str, list[str]]:
    """Collect #define blocks. Every `#if defined(...)` is false: the shared builds
    enable neither RGB feature, so the `#else` branches apply."""
    blocks: dict[str, list[str]] = {}
    frames: list[dict[str, bool]] = []  # {"parent", "taken", "active"} per #if level
    active = True
    for line in source.splitlines():
        line = line.strip()
        if line.startswith("#if"):
            frames.append({"parent": active, "taken": False, "active": False})
        elif line.startswith("#elif"):
            frames[-1]["active"] = False
        elif line.startswith("#else"):
            frames[-1]["active"] = frames[-1]["parent"] and not frames[-1]["taken"]
            frames[-1]["taken"] = True
        elif line.startswith("#endif"):
            frames.pop()
        elif active and (match := re.match(r"#define\s+(\w+)\s+(\S.*)$", line)):
            blocks[match.group(1)] = [token.strip() for token in match.group(2).split(",")]
        active = frames[-1]["active"] if frames else True
    return blocks


def expand(tokens: list[str], blocks: dict[str, list[str]]) -> list[str]:
    result = []
    for token in tokens:
        result.extend(expand(blocks[token], blocks) if token in blocks else [token])
    return result


def block(blocks: dict[str, list[str]], name: str) -> list[str]:
    key = next(k for k in blocks if k.strip("_") == name)
    return expand(blocks[key], blocks)


def label(token: str) -> str | dict:
    if token in LABELS:
        return LABELS[token]
    if match := re.fullmatch(r"KC_([A-Z0-9]|F\d+)", token):
        return match.group(1)
    raise SystemExit(f"No diagram label for {token}; add it to LABELS in {__file__}")


def layer_keys(blocks, prefix, thumbs, overrides, base_tokens):
    tokens = [t for row in ROWS for t in block(blocks, f"{prefix}_{row}")]
    tokens += block(blocks, thumbs[0]) + block(blocks, thumbs[1])
    keys = []
    for index, token in enumerate(tokens):
        if index in overrides:
            keys.append(overrides[index])
        elif token == "_______":
            fallback = label(base_tokens[index])
            keys.append({**fallback, "type": "trans"} if isinstance(fallback, dict) else {"t": fallback, "type": "trans"})
        else:
            keys.append(label(token))
    return tokens, keys


def main() -> None:
    blocks = parse_wrappers(WRAPPERS.read_text())
    base_tokens = [t for row in ROWS for t in block(blocks, f"QWERTY_{row}")]
    base_tokens += block(blocks, "BASE_MAC_MODS_L") + block(blocks, "BASE_MAC_MODS_R")

    layers = {}
    for title, _, prefix, thumbs, overrides in LAYERS:
        layers[title] = SUPER if prefix is None else layer_keys(blocks, prefix, thumbs, overrides, base_tokens)[1]

    layout = (
        {"qmk_info_json": str(INFO_JSON), "layout_name": "LAYOUT_split_3x5_3"}
        if INFO_JSON.exists()
        else {"qmk_keyboard": "beekeeb/piantor", "layout_name": "LAYOUT_split_3x5_3"}
    )
    keymap = {
        "layout": layout,
        "draw_config": {
            "dark_mode": "auto",
            "key_w": 70,
            "key_h": 60,
            "shrink_wide_legends": 6,
            "append_colon_to_layer_header": False,
            "style_layer_activators": False,
            "outer_pad_h": 20,
            # The README headings name each layer, so hide the drawn header.
            "svg_extra_style": "svg.keymap { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; } text.label { display: none; }",
        },
        "layers": layers,
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as handle:
        json.dump(keymap, handle, ensure_ascii=False)
    try:
        for title, slug, *_ in LAYERS:
            subprocess.run(
                ["uvx", "--from", KEYMAP_DRAWER, "keymap", "draw", handle.name, "-s", title, "-o", OUTPUT / f"{slug}.svg"],
                check=True,
            )
    finally:
        os.unlink(handle.name)
    print(f"Wrote {len(LAYERS)} diagrams to {OUTPUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    sys.exit(main())
