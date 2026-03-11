from __future__ import annotations

import click
import pyperclip

__all__ = ["read", "write"]


def read() -> None:
    try:
        text = pyperclip.paste()
        click.echo(text)
    except Exception as exc:  # pragma: no cover - platform dependent failures
        raise click.ClickException(f"Failed to read pasteboard: {exc}") from exc


def write(text: str) -> None:
    try:
        pyperclip.copy(text)
        click.echo(f"Pasteboard updated ({len(text)} chars).")
    except Exception as exc:  # pragma: no cover - platform dependent failures
        raise click.ClickException(f"Failed to write pasteboard: {exc}") from exc
