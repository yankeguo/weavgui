from __future__ import annotations

import click
import pyautogui

from .utils import coordinate_system_lines

__all__ = ["move", "move_to", "left_click", "double_click", "right_click"]


def move(dx: float, dy: float) -> None:
    try:
        width, height = _get_screen_size()

        current = pyautogui.position()
        start_nx = current.x / width
        start_ny = current.y / height

        target_nx = start_nx + dx
        target_ny = start_ny + dy

        _validate_normalized(target_nx, target_ny)

        pixel_x = round(target_nx * width)
        pixel_y = round(target_ny * height)
        pyautogui.moveTo(pixel_x, pixel_y)

        click.echo(
            "\n".join(
                [
                    "Mouse move details:",
                    *coordinate_system_lines(),
                    f"- Start position: ({start_nx:.4f}, {start_ny:.4f}).",
                    f"- Relative delta: (dx={dx:.4f}, dy={dy:.4f}).",
                    f"- End position: ({target_nx:.4f}, {target_ny:.4f}).",
                ]
            )
        )
    except click.ClickException:
        raise
    except Exception as exc:  # pragma: no cover - system dependent failures
        raise click.ClickException(f"Failed to move mouse: {exc}") from exc


def move_to(x: float, y: float) -> None:
    try:
        _validate_normalized(x, y)

        width, height = _get_screen_size()
        pixel_x = round(x * width)
        pixel_y = round(y * height)
        pyautogui.moveTo(pixel_x, pixel_y)

        click.echo(
            "\n".join(
                [
                    "Mouse moveto details:",
                    *coordinate_system_lines(),
                    f"- Target position: ({x:.4f}, {y:.4f}).",
                ]
            )
        )
    except click.ClickException:
        raise
    except Exception as exc:  # pragma: no cover - system dependent failures
        raise click.ClickException(f"Failed to move mouse: {exc}") from exc


def left_click() -> None:
    _do_click(action_name="click", button="left", is_double=False)


def double_click() -> None:
    _do_click(action_name="doubleclick", button="left", is_double=True)


def right_click() -> None:
    _do_click(action_name="rightclick", button="right", is_double=False)


def _do_click(action_name: str, button: str, is_double: bool) -> None:
    try:
        width, height = _get_screen_size()
        current = pyautogui.position()
        nx = current.x / width
        ny = current.y / height

        if is_double:
            pyautogui.doubleClick(button=button)
        else:
            pyautogui.click(button=button)

        click.echo(
            "\n".join(
                [
                    f"Mouse {action_name} details:",
                    *coordinate_system_lines(),
                    f"- Action position: ({nx:.4f}, {ny:.4f}).",
                    f"- Button: {button}.",
                ]
            )
        )
    except click.ClickException:
        raise
    except Exception as exc:  # pragma: no cover - system dependent failures
        raise click.ClickException(f"Failed to execute mouse {action_name}: {exc}") from exc


def _get_screen_size() -> tuple[int, int]:
    screen_size = pyautogui.size()
    width = int(screen_size.width)
    height = int(screen_size.height)
    if width <= 0 or height <= 0:
        raise click.ClickException("Failed to read primary display size.")
    return width, height


def _validate_normalized(x: float, y: float) -> None:
    if x < 0.0 or x >= 1.0 or y < 0.0 or y >= 1.0:
        raise click.ClickException(
            "Target position is out of bounds for normalized coordinates: "
            f"target=({x:.4f}, {y:.4f}), valid range=[0.0, 1.0)."
        )
