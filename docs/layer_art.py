"""SVG primitives shared by the Piantor maps and gesture illustrations."""

from html import escape

INK = "#183131"
SANS = "Inter, Arial, sans-serif"
MONO = "'IBM Plex Mono', Menlo, Consolas, monospace"


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
