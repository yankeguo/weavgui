---
name: weavgui
description: Automate desktop GUI operations using the weavgui CLI: taking screenshots, moving the mouse, clicking, typing keystrokes, and reading/writing the system pasteboard. Use when asked to interact with the desktop graphically — clicking UI elements, reading on-screen content, filling forms, navigating applications, or any task requiring precise mouse control and visual feedback.
---

# Skill: weavgui Desktop Automation

## Installation

```bash
uv tool install weavgui
```

Verify:

```bash
weavgui --version
```

> **macOS requirement**: mouse and keystroke automation requires Accessibility permission.  
> Grant it at: `System Settings > Privacy & Security > Accessibility`

---

## Coordinate System

All mouse and screenshot commands share the same coordinate space:

- Origin `(0, 0)` is the **top-left** of the primary display
- `x` increases to the right, `y` increases downward
- Coordinates are **logical pixels** (on macOS Retina, screenshots are auto-downscaled to match)

---

## Core Commands

### Screenshot

```bash
weavgui screenshot -o <path.png>             # with cursor markers
weavgui screenshot -o <path.png> --without-cursor  # clean screenshot
```

Default screenshot draws cursor markers at the current mouse position:

- Red crosshair lines
- Red inner box (200×200 px)
- Blue outer box (600×600 px)

The command also prints the current mouse coordinates and display bounds to stdout.

### Mouse Move

```bash
weavgui mouse move <dx> <dy>       # positive values
weavgui mouse move -- <dx> <dy>    # use -- when dx or dy is negative
```

Moves the mouse by a **relative delta**. Fails if the target would leave the display bounds. The command prints the start position, end position, and display bounds to stdout.

### Mouse Click

```bash
weavgui mouse click         # left click
weavgui mouse doubleclick   # double left click
weavgui mouse rightclick    # right click
```

All clicks happen at the **current cursor position**.

### Keystroke

```bash
weavgui keystroke <keys>
```

Examples: `c`, `ctrl+c`, `command+c`, `shift+a`, `command+z`

### Pasteboard

```bash
weavgui pasteboard write <text...>   # write to clipboard
weavgui pasteboard read              # read from clipboard
```

---

## Critical Workflow: Precise Mouse Positioning

**Never guess a target coordinate and click immediately.**

Mouse move accepts only relative deltas. You do not know the current mouse position or the exact pixel position of a UI element in advance. The correct approach is an **iterative positioning loop**:

```
screenshot → analyze image → move mouse → screenshot → analyze image → move mouse → ... → click
```

### Step-by-step

1. **Take a screenshot** and load the image into context:

   ```bash
   weavgui screenshot -o /tmp/screen.png
   ```

   Then read `/tmp/screen.png` as an image attachment.

2. **Analyze the screenshot**: Identify the target UI element. Read the cursor marker position from the stdout output (printed automatically). Estimate the pixel delta `(dx, dy)` needed to move from the current crosshair to the target.

3. **Move the mouse**:

   ```bash
   weavgui mouse move <dx> <dy>
   # or for negative values:
   weavgui mouse move -- <dx> <dy>
   ```

4. **Take another screenshot** and load it:

   ```bash
   weavgui screenshot -o /tmp/screen.png
   ```

5. **Verify position**: Check that the crosshair (red lines) is now centered on the target. If not, repeat from step 2 with a corrected delta.

6. **Click only when the cursor is confirmed on-target**:

   ```bash
   weavgui mouse click
   ```

### Why this loop matters

- `mouse move` only accepts relative deltas — you cannot teleport to an absolute coordinate.
- Screen content, window positions, and scroll state can all shift between steps.
- Even a single iteration of screenshot → analyze → move can land the cursor accurately.
- For high-precision targets (small buttons, text fields), two or three iterations are typical.

### Example: clicking a button labeled "Submit"

```bash
# Step 1: initial screenshot
weavgui screenshot -o /tmp/screen.png
# → attach /tmp/screen.png, observe crosshair at (500, 400), Submit button at approx (720, 610)
# → estimate dx=220, dy=210

# Step 2: move toward target
weavgui mouse move 220 210

# Step 3: verify screenshot
weavgui screenshot -o /tmp/screen.png
# → attach /tmp/screen.png, crosshair now at (720, 608) — close enough

# Step 4: click
weavgui mouse click
```

---

## Delegate to a Subagent

The iterative positioning loop loads multiple screenshots into context, which can consume significant tokens. **When possible, launch a subagent (Task tool) to perform the entire positioning-and-click sequence**, keeping the main conversation context clean.

### How to delegate

Use the Task tool with a prompt that describes:

1. The target element (e.g. "the Submit button in the bottom-right of the dialog")
2. The action to perform once positioned (e.g. `mouse click`, `mouse doubleclick`)
3. Any follow-up actions (e.g. type text, press a key)

Example prompt for the Task tool:

```
Use the weavgui CLI to click the "Submit" button visible on screen.

Workflow:
1. Run `weavgui screenshot -o /tmp/screen.png`, then read the image file.
2. Identify the "Submit" button in the screenshot. Read the crosshair position from stdout.
3. Estimate (dx, dy) from the crosshair to the button center, run `weavgui mouse move <dx> <dy>`.
4. Take another screenshot, verify the crosshair is on the button. Adjust if needed.
5. Run `weavgui mouse click`.
6. Take a final screenshot to confirm the click took effect.

Return a summary of what happened and the final mouse position.
```

### Benefits

- **Saves main context**: screenshots stay inside the subagent and are discarded when it finishes.
- **Isolation**: if the loop takes many iterations, the main conversation is unaffected.
- **Composability**: you can launch multiple subagents in sequence (e.g. one to click a field, another to type text) without accumulating images.

### When NOT to delegate

- If you only need a single screenshot for analysis (no mouse interaction), just run the command directly.
- If the task is a single click where you are already confident about the position.

---

## Text Input Workflow

To type text into a focused field:

1. Click the target field (using the positioning loop above)
2. Optionally select all existing text: `weavgui keystroke command+a`
3. Write new text to the pasteboard: `weavgui pasteboard write <your text>`
4. Paste: `weavgui keystroke command+v`

```bash
weavgui mouse click
weavgui keystroke command+a
weavgui pasteboard write Hello World
weavgui keystroke command+v
```

---

## Tips

- Always prefer the **iterative screenshot loop** over single-shot coordinate estimation.
- Use `--without-cursor` only when you need a clean image for analysis without the marker overlay.
- After any keyboard shortcut that changes screen state (e.g. `command+z`, `return`), take a fresh screenshot before proceeding.
- The stdout output of `weavgui screenshot` includes the current mouse position — use this as a precise anchor for the next delta calculation.
