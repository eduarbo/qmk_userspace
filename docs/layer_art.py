"""Vector drawing for the 36-key reference. Input positions are QMK layout units."""

from html import escape
from textwrap import wrap
from xml.etree import ElementTree as ET

W, H = 960, 504
PAPER, INK, MUTED = "#f6f0e2", "#142d31", "#41595b"
CREAM, MINT, LILAC = "#fff8e8", "#9ee6ca", "#cdbaff"
SLATE, QUIET = "#334d50", "#d2d9cf"
SANS = "Inter, Arial, sans-serif"
MONO = "'IBM Plex Mono', Menlo, Consolas, monospace"

# Subtitle and one concrete way into or out of each map.
NOTES = {
    "macos": (
        "The six thumb keys",
        "Hold either Return thumb and tap Space for Command + Space.",
    ),
    "winux": (
        "Windows and Linux",
        "Hold either Return thumb for Control. Reconnect to return to macOS.",
    ),
    "symbols": (
        "Digits, punctuation and arrows",
        "Hold Tab for Symbols. Either mint accent key adds Shift while held.",
    ),
    "super": (
        "Browser, windows and apps",
        "Hold Esc for Super. Add the Tab thumb for Hyper.",
    ),
    "fkeys": (
        "Function keys and media",
        "Hold Esc, then the Space or F16 thumb. Tap K to mute.",
    ),
    "adjust": (
        "Firmware controls",
        "Hold Esc and a Return thumb. J toggles Gamepad. K switches bases.",
    ),
    "gamepad": (
        "One-handed movement",
        "To leave, hold the left Alt and right Return thumbs, then tap J.",
    ),
}


def text(
    x, y, value, size, *, color=INK, weight=500, align="start", mono=False, extra=""
):
    face = MONO if mono else SANS
    return (
        f'<text x="{x:g}" y="{y:g}" text-anchor="{align}" font-family="{face}" '
        f'font-size="{size:g}" font-weight="{weight}" fill="{color}" {extra}>{escape(str(value))}</text>'
    )


def rect(x, y, w, h, radius, fill, extra=""):
    return (
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{radius:g}" '
        f'fill="{fill}" {extra}/>'
    )


def legend(key):
    return {"t": key} if isinstance(key, str) else key


def key_color(slug, index, key):
    if key.get("type") == "held":
        return INK, "#ffffff"
    if key.get("type") == "trans" or not key["t"]:
        return QUIET, MUTED
    if slug == "symbols" and key.get("h") == "Shift":
        return MINT, INK
    if index >= 30:
        if key.get("h") in {"Symbols", "Super", "Hyper", "F-Keys", "Adjust"}:
            return LILAC, INK
        if key.get("h"):
            return MINT, INK
    return CREAM, INK


def cap(index, x, y, key, source, slug):
    fill, ink = key_color(slug, index, key)
    label = key["t"].splitlines()
    drawing = [
        f'<g class="key" id="key-{index}" data-position="{escape(source, quote=True)}" transform="translate({x:g} {y:g})">',
        rect(0, 4, 67, 55, 8, "#172f33"),
        rect(0, 1, 67, 54, 8, "#a3afa3"),
        rect(1, 0, 65, 52, 7, fill, 'class="face"'),
    ]
    base = slug in {"macos", "winux"}
    if not base and index < 30 and key["t"]:
        drawing.append(text(6, 12, source, 10, color=ink, mono=True, weight=650))
    if key.get("s"):
        drawing.append(
            text(61, 12, key["s"], 11, color=ink, mono=True, align="end", weight=650)
        )
    ymid = 32 if base or not key.get("h") else 29
    if len(label) == 2:
        ymid = 27 if key.get("s") or not base else 22
    if key.get("h") and base:
        ymid = 25
    if key.get("s") and key.get("h"):
        ymid = 32
    for i, line in enumerate(label):
        size = (
            23
            if len(line) <= 2 and len(label) == 1
            else min(17, 96 / max(1, len(line)))
        )
        if key.get("s") and key.get("h"):
            size = min(size, 16)
        if len(label) > 1:
            size = min(size, 13.5)
        drawing.append(
            text(33.5, ymid + i * 15, line, size, color=ink, weight=700, align="middle")
        )
    if key.get("h"):
        drawing.append(
            text(33.5, 46, key["h"], 11.5, color=ink, align="middle", weight=650)
        )
    if base and index in {13, 16}:
        drawing.append(rect(26, 42, 15, 2, 1, "#aab3a9"))
    if key.get("type") == "held":
        drawing.append(rect(22, 43, 23, 3, 1.5, MINT))
    drawing.append("</g>")
    return "".join(drawing)


def hull(points):
    """Outline a hand from the outer corners of its switches (monotone chain)."""
    points = sorted(set(points))

    def half(seq):
        result = []
        for x, y in seq:
            while len(result) >= 2:
                (ax, ay), (bx, by) = result[-2:]
                if (bx - ax) * (y - ay) > (by - ay) * (x - ax):
                    break
                result.pop()
            result.append((x, y))
        return result

    return half(points)[:-1] + half(reversed(points))[:-1]


def split_board(positions, keys, physical, slug):
    drawing = []
    for side in (0, 1):
        ids = [
            i for i in range(36) if (i % 10 >= 5 if i < 30 else i >= 33) == bool(side)
        ]
        coords = [
            (39 + positions[i]["x"] * 74, 131 + positions[i]["y"] * 61) for i in ids
        ]
        corners = [
            (x + dx, y + dy) for x, y in coords for dx in (0, 67) for dy in (0, 58)
        ]
        outline = " ".join(f"{x:g},{y:g}" for x, y in hull(corners))
        drawing.append(f'<g id="{"right" if side else "left"}-hand">')
        for offset, color, border in [
            (5, "#adad9f", 19),
            (0, "#183b40", 18),
            (-1, SLATE, 14),
        ]:
            drawing.append(
                f'<polygon points="{outline}" transform="translate(0 {offset})" '
                f'fill="{color}" stroke="{color}" stroke-width="{border}" stroke-linejoin="round"/>'
            )
        for index, (x, y) in zip(ids, coords):
            drawing.append(cap(index, x, y, legend(keys[index]), physical[index], slug))
        drawing.append("</g>")
    return "\n".join(drawing)


def draw_map(title, slug, positions, keys, physical):
    subtitle, example = NOTES[slug]
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)} · Piantor and Corne</title><desc id="desc">{escape(subtitle + ". " + example)}</desc>',
        rect(0, 0, W, H, 19, PAPER),
        text(32, 32, "QMK  /  PIANTOR + CORNE", 13, color=MUTED, mono=True, weight=650),
        text(31, 79, title, 42, weight=750),
        text(928, 72, subtitle, 19, color=MUTED, align="end"),
        '<path d="M32 103H928 M32 442H928" stroke="#b2bcb1"/>',
        '<g id="board">',
        split_board(positions, keys, physical, slug),
        "</g>",
        rect(32, 463, 6, 19, 3, "#34776b"),
        text(49, 478, example, 17, weight=600),
        "</svg>",
    ]
    return "\n".join(body) + "\n"


def mobile_map(art, title, slug):
    """Stack the two unrotated hands so a phone can display the hold legends."""
    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)
    root = ET.fromstring(art)
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="490" height="847" viewBox="0 0 490 847" role="img" aria-labelledby="title">',
        f'<title id="title">{escape(title)} · left and right hands</title>',
        rect(0, 0, 490, 847, 16, PAPER),
        text(23, 27, "QMK  /  PIANTOR + CORNE", 13, mono=True, color=MUTED),
        text(22, 65, title, 34, weight=750),
    ]
    for name, x, y, label_y in [("left", -7, -21, 97), ("right", -480, 318, 436)]:
        group = root.find(f".//{{{ns}}}g[@id='{name}-hand']")
        lines += [
            text(
                23,
                label_y,
                name.upper() + " HAND",
                13,
                mono=True,
                color=MUTED,
                weight=650,
            ),
            f'<g transform="translate({x} {y})">{ET.tostring(group, encoding="unicode")}</g>',
        ]
    lines.append('<path d="M23 770h444" stroke="#b2bcb1"/>')
    for row, part in enumerate(wrap(NOTES[slug][1], 51)):
        lines.append(text(23, 798 + row * 23, part, 17, weight=600))
    return "\n".join(lines + ["</svg>", ""])
