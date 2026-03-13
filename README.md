# weavgui

[English](README.md) | [中文](README.zh.md)

> **Requirements:** You need a **vision-capable LLM**, and the Claw-style platform must support **loading images directly from files into context**. We recommend [weavbot](https://github.com/yankeguo/weavbot) for this workflow.

**Turn any vision-capable LLM into a desktop GUI operator.**

weavgui provides a minimal CLI toolkit that closes the loop between _seeing_ and _acting_: take an annotated screenshot, feed it to a vision model, move the mouse, and repeat — until the model clicks exactly where it needs to.

```
screenshot (with crosshair) → vision model analyzes image → mouse move / click → screenshot → ...
```

No browser required. No DOM. No accessibility tree. Just pixels and a feedback loop.

```shell
npx skills add https://github.com/yankeguo/weavgui/tree/main/skills/weavgui -a openclaw -y
```

![Screenshot with cursor crosshair and bounding boxes](assets/image1.png)

## Installation

```bash
uv tool install weavgui
```

To upgrade an existing installation:

```bash
uv tool upgrade weavgui
```

## Quick Start

```bash
weavgui --version
weavgui screenshot
weavgui mouse move '(100,100)'
weavgui mouse moveto '(500,300)'
weavgui mouse click
weavgui pasteboard write hello world
weavgui pasteboard read
weavgui keystroke command+c
```

## Auto-Screenshot Behavior

Every action command automatically captures a screenshot to **`screenshot.png`** in the current working directory after a short delay. No flags needed.

| Command | Auto-screenshot delay |
|---|---|
| `screenshot` | immediate (no delay) |
| `mouse move`, `mouse moveto` | 500 ms |
| `mouse click`, `doubleclick`, `rightclick` | 2 s |
| `keystroke` | 1 s |

The screenshot always includes cursor markers (crosshair + reference boxes). Read `screenshot.png` as an image after any command to observe the result.

## Coordinate System

Mouse and screenshot-related commands share the same coordinate convention:

- Primary-display logical coordinates (pixels)
- Origin at top-left: `(0, 0)`
- `x` increases to the right, `y` increases downward
- Single-display only (primary monitor)
- On macOS Retina, screenshots are downscaled to logical resolution so that pixel coordinates match mouse coordinates

## Command Reference

### Global

| Command | Description |
|---|---|
| `weavgui --version` | Print CLI version |
| `weavgui -h` | Show help |

### `screenshot`

Capture a screenshot of the primary display and save it as `screenshot.png` in the current working directory.

```
weavgui screenshot
```

The cursor position is always annotated:

- Red crosshair spanning the full screenshot
- Red small box centered on cursor (`100×100 px`, radius 50)
- Green medium box centered on cursor (`200×200 px`, radius 100)
- Blue large box centered on cursor (`600×600 px`, radius 300)

The three boxes serve as **positioning references** for the next `mouse move` / `mouse moveto` command:

| Target location | Suggested delta range |
|---|---|
| Inside the red box | Fine adjustment, `±50 px` |
| Between red and green boxes | Medium adjustment, `±50–100 px` |
| Between green and blue boxes | Coarse adjustment, `±100–300 px` |
| Outside the blue box | Large move needed — estimate from the full screenshot |

```bash
weavgui screenshot
# → saves screenshot.png with cursor markers
# → prints cursor position and display bounds to stdout
```

### `mouse`

#### `mouse move '(dx,dy)'`

Move the cursor by a relative pixel delta. The argument uses `(dx,dy)` format. Fails if the target position would leave the primary display bounds. After moving, waits 500 ms and saves a screenshot to `screenshot.png`.

```bash
weavgui mouse move '(100,100)'
weavgui mouse move '(-100,50)'
```

#### `mouse moveto '(x,y)'`

Move the cursor to an absolute position. The argument uses `(x,y)` format. Fails if the position is outside the primary display bounds. After moving, waits 500 ms and saves a screenshot to `screenshot.png`.

```bash
weavgui mouse moveto '(500,300)'
```

#### `mouse click`

Left click at the current cursor position. Waits 2 s then saves a screenshot to `screenshot.png`.

```bash
weavgui mouse click
```

#### `mouse doubleclick`

Double left click at the current cursor position. Waits 2 s then saves a screenshot to `screenshot.png`.

```bash
weavgui mouse doubleclick
```

#### `mouse rightclick`

Right click at the current cursor position. Waits 2 s then saves a screenshot to `screenshot.png`.

```bash
weavgui mouse rightclick
```

### `pasteboard`

#### `pasteboard read`

Read text from the system pasteboard and print to stdout.

```bash
weavgui pasteboard read
```

#### `pasteboard write <text...>`

Write text to the system pasteboard. Multiple arguments are joined by a single space.

```bash
weavgui pasteboard write hello world
```

### `keystroke`

Simulate keyboard input. Supports single keys and combinations joined with `+`. Waits 1 s then saves a screenshot to `screenshot.png`.

```
weavgui keystroke <keys>
```

| Input | Meaning |
|---|---|
| `c` | Press `c` |
| `ctrl+c` | Press Ctrl+C |
| `command+c` | Press Command+C |
| `shift+a` | Press Shift+A |
| `alt+f4` | Press Alt+F4 |

Modifier aliases:

| Alias | Resolves to |
|---|---|
| `control` | `ctrl` |
| `cmd` | `command` |
| `option` | `alt` |

On macOS, single-key combos with `command` are sent via AppleScript for better reliability.

```bash
weavgui keystroke c
weavgui keystroke ctrl+c
weavgui keystroke command+c
```

## Development

Clone the repository and install dependencies:

```bash
git clone https://github.com/yankeguo/weavgui.git
cd weavgui
uv sync
```

Run commands from source:

```bash
uv run weavgui --version
uv run weavgui screenshot
```

## Notes

- Mouse and keystroke automation requires **Accessibility** permission.
- If commands fail on macOS, go to `System Settings > Privacy & Security > Accessibility` and grant access to your terminal application.

## License

MIT
