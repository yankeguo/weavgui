from __future__ import annotations

import platform
from pathlib import Path

import click
import pyautogui
from mss import mss
from PIL import Image, ImageDraw

RED = (255, 0, 0)
BLUE = (0, 102, 255)
INNER_BOX_DISTANCE = 100
OUTER_BOX_DISTANCE = 300
LINE_WIDTH = 2
BOX_LINE_WIDTH = 2


def _capture_primary_monitor() -> Image.Image:
    with mss() as sct:
        if len(sct.monitors) < 2:
            raise click.ClickException("Primary monitor not found.")
        monitor = sct.monitors[1]
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.rgb)


def _normalize_macos_logical_resolution(image: Image.Image) -> Image.Image:
    if platform.system() != "Darwin":
        return image

    logical_size = pyautogui.size()
    if logical_size.width <= 0 or logical_size.height <= 0:
        return image

    scale_x = image.width / logical_size.width
    scale_y = image.height / logical_size.height
    needs_resize = scale_x > 1.01 or scale_y > 1.01
    if not needs_resize:
        return image

    return image.resize(
        (logical_size.width, logical_size.height),
        Image.Resampling.LANCZOS,
    )


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


def _draw_cursor_markers(image: Image.Image, cursor_x: int, cursor_y: int) -> None:
    draw = ImageDraw.Draw(image)
    width, height = image.size

    draw.line([(0, cursor_y), (width - 1, cursor_y)], fill=RED, width=LINE_WIDTH)
    draw.line([(cursor_x, 0), (cursor_x, height - 1)], fill=RED, width=LINE_WIDTH)

    for distance in (INNER_BOX_DISTANCE, OUTER_BOX_DISTANCE):
        color = RED if distance == INNER_BOX_DISTANCE else BLUE
        left = cursor_x - distance
        top = cursor_y - distance
        right = cursor_x + distance
        bottom = cursor_y + distance
        draw.rectangle(
            [(left, top), (right, bottom)],
            outline=color,
            width=BOX_LINE_WIDTH,
        )


def take_snapshot(output: str, without_cursor: bool) -> None:
    output_path = Path(output).expanduser()
    if output_path.suffix.lower() != ".png":
        raise click.ClickException("Output file must use .png extension.")

    try:
        image = _capture_primary_monitor()
        image = _normalize_macos_logical_resolution(image)

        if not without_cursor:
            cursor = pyautogui.position()
            cursor_x = _clamp(int(cursor.x), 0, image.width - 1)
            cursor_y = _clamp(int(cursor.y), 0, image.height - 1)
            _draw_cursor_markers(image, cursor_x, cursor_y)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format="PNG")
        click.echo(f"Snapshot saved to: {output_path}")
        if not without_cursor:
            click.echo(
                "\n".join(
                    [
                        "Cursor marker details:",
                        "- Coordinate system: primary-display logical coordinates (pixels).",
                        "- Origin: top-left of the screenshot (0, 0).",
                        "- Axis directions: x increases to the right, y increases downward.",
                        f"- Crosshair center (mouse position): ({cursor_x}, {cursor_y}).",
                        f"- Inner box: {INNER_BOX_DISTANCE * 2}x{INNER_BOX_DISTANCE * 2}px, color red.",
                        f"- Outer box: {OUTER_BOX_DISTANCE * 2}x{OUTER_BOX_DISTANCE * 2}px, color blue.",
                    ]
                )
            )
    except click.ClickException:
        raise
    except Exception as exc:  # pragma: no cover - system dependent failures
        raise click.ClickException(f"Failed to capture snapshot: {exc}") from exc
