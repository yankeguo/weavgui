from importlib.metadata import PackageNotFoundError, version

import click

from .keyboard import send
from .mouse import double_click, left_click, move, right_click
from .pasteboard import read, write
from .screenshot import capture


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
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=str),
    required=True,
    help="Output PNG file path.",
)
@click.option(
    "--without-cursor",
    is_flag=True,
    default=False,
    help="Do not draw cursor markers in the screenshot.",
)
def screenshot_command(output: str, without_cursor: bool) -> None:
    """Capture a desktop screenshot."""
    capture(output=output, without_cursor=without_cursor)


@cli.command("keystroke")
@click.argument("keys", type=str)
def keystroke_command(keys: str) -> None:
    """Simulate a keystroke, e.g. c, ctrl+c, command+c."""
    send(keys)


@cli.group("mouse")
def mouse_group() -> None:
    """Mouse controls."""


@mouse_group.command("move")
@click.argument("dx", type=int)
@click.argument("dy", type=int)
def mouse_move_command(dx: int, dy: int) -> None:
    """Move mouse cursor by relative delta."""
    move(dx=dx, dy=dy)


@mouse_group.command("click")
def mouse_click_command() -> None:
    """Left click at current cursor position."""
    left_click()


@mouse_group.command("doubleclick")
def mouse_doubleclick_command() -> None:
    """Double click at current cursor position."""
    double_click()


@mouse_group.command("rightclick")
def mouse_rightclick_command() -> None:
    """Right click at current cursor position."""
    right_click()


@cli.group("pasteboard")
def pasteboard_group() -> None:
    """Pasteboard (clipboard) controls."""


@pasteboard_group.command("read")
def pasteboard_read_command() -> None:
    """Read text from pasteboard."""
    read()


@pasteboard_group.command("write")
@click.argument("text", nargs=-1, required=True)
def pasteboard_write_command(text: tuple[str, ...]) -> None:
    """Write text to pasteboard."""
    write(" ".join(text))


def main() -> int:
    cli()
    return 0
