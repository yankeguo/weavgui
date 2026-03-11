from __future__ import annotations

import click
import pyautogui

from .utils import coordinate_system_lines

__all__ = ["move", "move_to", "left_click", "double_click", "right_click"]


def move(dx: int, dy: int) -> None:
    try:
        current = pyautogui.position()
        start_x = int(current.x)
        start_y = int(current.y)
        target_x = start_x + int(dx)
        target_y = start_y + int(dy)

        width, height = _validate_target(target_x, target_y)
        pyautogui.moveTo(target_x, target_y)

        click.echo(
            "\n".join(
                [
                    "Mouse move details:",
                    *coordinate_system_lines(),
                    f"- Start position: ({start_x}, {start_y}).",
                    f"- Relative delta: (dx={dx}, dy={dy}).",
                    f"- End position: ({target_x}, {target_y}).",
                    f"- Display bounds: x:[0,{width - 1}], y:[0,{height - 1}].",
                ]
            )
        )
    except click.ClickException:
        raise
    except Exception as exc:  # pragma: no cover - system dependent failures
        raise click.ClickException(f"Failed to move mouse: {exc}") from exc


def move_to(x: int, y: int) -> None:
    try:
        width, height = _validate_target(x, y)
        pyautogui.moveTo(x, y)

        click.echo(
            "\n".join(
                [
                    "Mouse moveto details:",
                    *coordinate_system_lines(),
                    f"- Target position: ({x}, {y}).",
                    f"- Display bounds: x:[0,{width - 1}], y:[0,{height - 1}].",
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
        x, y, width, height = _current_position_with_bounds()
        if is_double:
            pyautogui.doubleClick(button=button)
        else:
            pyautogui.click(button=button)

        click.echo(
            "\n".join(
                [
                    f"Mouse {action_name} details:",
                    *coordinate_system_lines(),
                    f"- Action position: ({x}, {y}).",
                    f"- Button: {button}.",
                    f"- Display bounds: x:[0,{width - 1}], y:[0,{height - 1}].",
                ]
            )
        )
    except click.ClickException:
        raise
    except Exception as exc:  # pragma: no cover - system dependent failures
        raise click.ClickException(
            f"Failed to execute mouse {action_name}: {exc}"
        ) from exc


def _validate_target(target_x: int, target_y: int) -> tuple[int, int]:
    screen_size = pyautogui.size()
    width = int(screen_size.width)
    height = int(screen_size.height)
    if width <= 0 or height <= 0:
        raise click.ClickException("Failed to read primary display size.")

    if target_x < 0 or target_y < 0 or target_x >= width or target_y >= height:
        raise click.ClickException(
            "Target position is out of bounds for primary display logical coordinates: "
            f"target=({target_x}, {target_y}), "
            f"bounds=x:[0,{width - 1}], y:[0,{height - 1}]."
        )

    return width, height


def _current_position_with_bounds() -> tuple[int, int, int, int]:
    current = pyautogui.position()
    x = int(current.x)
    y = int(current.y)
    width, height = _validate_target(x, y)
    return x, y, width, height
