from __future__ import annotations

__all__ = ["clamp", "coordinate_system_lines"]


def clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


def coordinate_system_lines() -> list[str]:
    return [
        "- Coordinate system: primary-display logical coordinates (pixels).",
        "- Origin: top-left of the display (0, 0).",
        "- Axis directions: x increases to the right, y increases downward.",
    ]
