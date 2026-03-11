from __future__ import annotations

import platform
import subprocess

import click
import pyautogui

MODIFIER_ALIASES = {
    "ctrl": "ctrl",
    "control": "ctrl",
    "cmd": "command",
    "command": "command",
    "alt": "alt",
    "option": "alt",
    "shift": "shift",
}
MODIFIER_KEYWORDS = {"ctrl", "command", "alt", "shift"}


def send(spec: str) -> None:
    keys = _parse_spec(spec)
    if platform.system() == "Darwin" and _can_use_applescript(keys):
        _send_applescript(keys)
        return

    try:
        pyautogui.hotkey(*keys)
        click.echo(f"Keystroke sent: {'+'.join(keys).upper()}.")
    except Exception as exc:  # pragma: no cover - platform dependent failures
        raise click.ClickException(f"Failed to trigger keystroke: {exc}") from exc


def _parse_spec(spec: str) -> tuple[str, ...]:
    parts = [part.strip().lower() for part in spec.split("+")]
    keys = [part for part in parts if part]
    if not keys:
        raise click.ClickException("Keystroke cannot be empty.")
    return tuple(MODIFIER_ALIASES.get(key, key) for key in keys)


def _can_use_applescript(keys: tuple[str, ...]) -> bool:
    non_modifiers = [key for key in keys if key not in MODIFIER_KEYWORDS]
    if len(non_modifiers) != 1:
        return False
    if len(non_modifiers[0]) != 1:
        return False
    return all(key in MODIFIER_KEYWORDS or len(key) == 1 for key in keys)


def _send_applescript(keys: tuple[str, ...]) -> None:
    non_modifier = next(key for key in keys if key not in MODIFIER_KEYWORDS)
    modifiers = [key for key in keys if key in MODIFIER_KEYWORDS]
    using_clause = ""
    if modifiers:
        using_clause = (
            " using {" + ", ".join(f"{item} down" for item in modifiers) + "}"
        )
    script = (
        f'tell application "System Events" to keystroke "{non_modifier}"{using_clause}'
    )
    try:
        subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            text=True,
        )
        click.echo(f"Keystroke sent: {'+'.join(keys).upper()}.")
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        message = "Failed to trigger keystroke via osascript."
        if stderr:
            message = f"{message} {stderr}"
        message = (
            f"{message} Ensure Terminal/Cursor has Accessibility permission "
            "in System Settings > Privacy & Security > Accessibility."
        )
        raise click.ClickException(message) from exc
