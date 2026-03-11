import time
from importlib.metadata import PackageNotFoundError, version

import click

from .keyboard import send
from .mouse import double_click, left_click, move, move_to, right_click
from .utils import parse_point
from .pasteboard import read, write
from .screenshot import capture

__all__ = ["cli"]


def app_version() -> str:
    try:
        return version("weavgui")
    except PackageNotFoundError:
        return "0.0.0"


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    version=app_version(),
    prog_name="weavgui",
    message="%(prog)s %(version)s",
)
def cli() -> None:
    """Orchestrate and automate graphical desktop workflows."""


@cli.command("screenshot")
def screenshot_command() -> None:
    """Capture a desktop screenshot with cursor markers.

    Always saves to screenshot.png in the current working directory.
    Cursor crosshair and reference boxes are always drawn.
    """
    capture()


@cli.command("keystroke")
@click.argument("keys", type=str)
def keystroke_command(keys: str) -> None:
    """Simulate a keystroke, e.g. c, ctrl+c, command+c.

    A screenshot is automatically captured to screenshot.png after a 1 s delay.
    """
    send(keys)
    time.sleep(1)
    capture()


@cli.group("mouse")
def mouse_group() -> None:
    """Mouse controls."""


@mouse_group.command("move")
@click.argument("delta", type=str)
def mouse_move_command(delta: str) -> None:
    """Move mouse cursor by relative delta, e.g. '(100,-50)'.

    A screenshot is automatically captured to screenshot.png after a 500 ms delay.
    """
    try:
        dx, dy = parse_point(delta)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    move(dx=dx, dy=dy)
    time.sleep(0.5)
    capture()


@mouse_group.command("moveto")
@click.argument("position", type=str)
def mouse_moveto_command(position: str) -> None:
    """Move mouse cursor to absolute position, e.g. '(500,300)'.

    A screenshot is automatically captured to screenshot.png after a 500 ms delay.
    """
    try:
        x, y = parse_point(position)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    move_to(x=x, y=y)
    time.sleep(0.5)
    capture()


@mouse_group.command("click")
def mouse_click_command() -> None:
    """Left click at current cursor position.

    A screenshot is automatically captured to screenshot.png after a 2 s delay.
    """
    left_click()
    time.sleep(2)
    capture()


@mouse_group.command("doubleclick")
def mouse_doubleclick_command() -> None:
    """Double click at current cursor position.

    A screenshot is automatically captured to screenshot.png after a 2 s delay.
    """
    double_click()
    time.sleep(2)
    capture()


@mouse_group.command("rightclick")
def mouse_rightclick_command() -> None:
    """Right click at current cursor position.

    A screenshot is automatically captured to screenshot.png after a 2 s delay.
    """
    right_click()
    time.sleep(2)
    capture()


@cli.group("pasteboard")
def pasteboard_group() -> None:
    """Pasteboard (clipboard) controls."""


@pasteboard_group.command("read")
def pasteboard_read_command() -> None:
    """Read text from pasteboard and print to stdout."""
    read()


@pasteboard_group.command("write")
@click.argument("text", nargs=-1, required=True)
def pasteboard_write_command(text: tuple[str, ...]) -> None:
    """Write text to pasteboard. Multiple words are joined with a single space."""
    write(" ".join(text))
