# weavgui

A command-line interface that lets you orchestrate and automate your graphical desktop environment with code-level precision

## Usage (uv)

```bash
uv sync
uv run weavgui --version
uv run python -m weavgui --version
uv run weavgui screenshot -o out.png
uv run weavgui screenshot -o out-no-cursor.png --without-cursor
uv run weavgui mouse move 100 100
uv run weavgui mouse move -- -100 0
uv run weavgui mouse click
uv run weavgui mouse doubleclick
uv run weavgui mouse rightclick
uv run weavgui pasteboard write hello world
uv run weavgui pasteboard read
```
