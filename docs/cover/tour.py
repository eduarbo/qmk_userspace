"""Piantor layer changes. Indices follow the firmware's LAYOUT_split_3x5_3 order."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Frame:
    layer: str
    cue: str
    held: tuple[int, ...] = ()
    tap: int | None = None
    still: str | None = None
    seconds: float = 3.8


ESC, RETURN_L, RETURN_R, TAB, F16 = 30, 32, 33, 34, 35
J, K = 16, 17

# The two latched modes have a separate tap frame on the originating map.
# The final Winux frame loops to the power-up macOS base.
TOUR = (
    Frame("macOS base", "Default on power-up.", still="macos", seconds=6),
    Frame("Symbols", "Hold Tab.", (TAB,), still="symbols", seconds=8),
    Frame("Hyper", "Keep Tab down. Hold Esc.", (TAB, ESC), still="hyper", seconds=8),
    Frame("Super", "Release Tab. Keep Esc down.", (ESC,), still="super", seconds=8),
    Frame("F-Keys", "Keep Esc down. Hold F16.", (ESC, F16), still="fkeys", seconds=8),
    Frame("Super", "Release F16. Keep Esc down.", (ESC,)),
    Frame(
        "Adjust",
        "Keep Esc down. Hold Return.",
        (ESC, RETURN_L),
        still="adjust",
        seconds=7,
    ),
    Frame("Adjust", "Tap J to turn on Gamepad.", (ESC, RETURN_L), tap=J),
    Frame(
        "Gamepad", "Release both thumbs. Gamepad stays on.", still="gamepad", seconds=8
    ),
    Frame("Gamepad + Adjust", "Hold Alt, then right Return.", (ESC, RETURN_R)),
    Frame("Gamepad + Adjust", "Tap J to leave Gamepad.", (ESC, RETURN_R), tap=J),
    Frame("macOS base", "Release both thumbs."),
    Frame("Super", "Hold Esc.", (ESC,)),
    Frame("Adjust", "Keep Esc down. Hold Return.", (ESC, RETURN_L)),
    Frame("Adjust", "Tap K to switch bases.", (ESC, RETURN_L), tap=K),
    Frame(
        "Winux base", "Release both thumbs. Winux stays on.", still="winux", seconds=8
    ),
)
