from __future__ import annotations

import platform
from pathlib import Path

import click
import pyautogui
from mss import mss
from PIL import Image, ImageDraw

from .utils import clamp, echo_coordinate_system

RED = (255, 0, 0)
BLUE = (0, 102, 255)
INNER_BOX_DISTANCE = 100
OUTER_BOX_DISTANCE = 300
LINE_WIDTH = 2
BOX_LINE_WIDTH = 2


def capture(output: str, without_cursor: bool) -> None:
    output_path = Path(output).expanduser()
    if output_path.suffix.lower() != ".png":
        raise click.ClickException("Output file must use .png extension.")

    try:
        image = _grab_primary_monitor()
        image = _to_logical_resolution(image)

        cursor_x = cursor_y = 0
        if not without_cursor:
            cursor = pyautogui.position()
            cursor_x = clamp(int(cursor.x), 0, image.width - 1)
            cursor_y = clamp(int(cursor.y), 0, image.height - 1)
            _draw_markers(image, cursor_x, cursor_y)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, format="PNG")
        click.echo(f"Screenshot saved to: {output_path}")
        if not without_cursor:
            click.echo(
                "\n".join(
                    [
                        "Cursor marker details:",
                        *echo_coordinate_system(),
                        f"- Crosshair center (mouse position): ({cursor_x}, {cursor_y}).",
                        f"- Inner box: {INNER_BOX_DISTANCE * 2}x{INNER_BOX_DISTANCE * 2}px, color red.",
                        f"- Outer box: {OUTER_BOX_DISTANCE * 2}x{OUTER_BOX_DISTANCE * 2}px, color blue.",
                    ]
                )
            )
    except click.ClickException:
        raise
    except Exception as exc:  # pragma: no cover - system dependent failures
        raise click.ClickException(f"Failed to capture screenshot: {exc}") from exc


def _grab_primary_monitor() -> Image.Image:
    with mss() as sct:
        if len(sct.monitors) < 2:
            raise click.ClickException("Primary monitor not found.")
        monitor = sct.monitors[1]
        shot = sct.grab(monitor)
        return Image.frombytes("RGB", shot.size, shot.rgb)


def _to_logical_resolution(image: Image.Image) -> Image.Image:
    if platform.system() != "Darwin":
        return image

    logical_size = pyautogui.size()
    if logical_size.width <= 0 or logical_size.height <= 0:
        return image

    scale_x = image.width / logical_size.width
    scale_y = image.height / logical_size.height
    if scale_x <= 1.01 and scale_y <= 1.01:
        return image

    return image.resize(
        (logical_size.width, logical_size.height),
        Image.Resampling.LANCZOS,
    )


def _draw_markers(image: Image.Image, cursor_x: int, cursor_y: int) -> None:
    draw = ImageDraw.Draw(image)
    width, height = image.size

    draw.line([(0, cursor_y), (width - 1, cursor_y)], fill=RED, width=LINE_WIDTH)
    draw.line([(cursor_x, 0), (cursor_x, height - 1)], fill=RED, width=LINE_WIDTH)

    for distance in (INNER_BOX_DISTANCE, OUTER_BOX_DISTANCE):
        color = RED if distance == INNER_BOX_DISTANCE else BLUE
        draw.rectangle(
            [
                (cursor_x - distance, cursor_y - distance),
                (cursor_x + distance, cursor_y + distance),
            ],
            outline=color,
            width=BOX_LINE_WIDTH,
        )
