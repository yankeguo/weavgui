from __future__ import annotations


def clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


def echo_coordinate_system() -> list[str]:
    return [
        "- Coordinate system: primary-display logical coordinates (pixels).",
        "- Origin: top-left of the display (0, 0).",
        "- Axis directions: x increases to the right, y increases downward.",
    ]
