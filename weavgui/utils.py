from __future__ import annotations

import re

__all__ = ["clamp", "coordinate_system_lines", "parse_point"]

_POINT_RE = re.compile(r"^\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)$")


def parse_point(value: str) -> tuple[int, int]:
    m = _POINT_RE.match(value.strip())
    if not m:
        raise ValueError(f"Invalid coordinate format: {value!r}, expected (x,y)")
    return int(m.group(1)), int(m.group(2))


def clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


def coordinate_system_lines() -> list[str]:
    return [
        "- Coordinate system: primary-display logical coordinates (pixels).",
        "- Origin: top-left of the display (0, 0).",
        "- Axis directions: x increases to the right, y increases downward.",
    ]
