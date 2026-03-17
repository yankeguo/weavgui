from __future__ import annotations

import re

__all__ = ["clamp", "coordinate_system_lines", "parse_point"]

_POINT_RE = re.compile(r"^\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)$")


def parse_point(value: str) -> tuple[float, float]:
    m = _POINT_RE.match(value.strip())
    if not m:
        raise ValueError(f"Invalid coordinate format: {value!r}, expected (x,y)")
    return float(m.group(1)), float(m.group(2))


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


def coordinate_system_lines() -> list[str]:
    return [
        "- Coordinate system: normalized coordinates (0.0 to 1.0).",
        "- Origin: top-left (0.0, 0.0), bottom-right (1.0, 1.0).",
        "- Axis directions: x increases to the right, y increases downward.",
    ]
