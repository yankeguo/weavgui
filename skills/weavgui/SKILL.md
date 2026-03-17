---
name: weavgui
description: "Automate desktop GUI operations using the weavgui CLI: taking screenshots, moving the mouse, clicking, typing keystrokes, and reading/writing the system pasteboard. Use when asked to interact with the desktop graphically — clicking UI elements, reading on-screen content, filling forms, navigating applications, or any task requiring precise mouse control and visual feedback."
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

## Auto-Screenshot Behavior

Every action command automatically captures a screenshot to **`screenshot.png`** in the current working directory.

For workflow purposes, treat `screenshot.png` as ready immediately when each command exits; do not add extra waiting steps.

After each command, read `screenshot.png` as an image to observe the current state of the screen.

---

## Coordinate System

All mouse and screenshot commands share the same coordinate space:

- **Normalized coordinates**: values range from `0.0` to `1.0`
- Origin `(0.0, 0.0)` is the **top-left** of the primary display
- Bottom-right is `(1.0, 1.0)`
- `x` increases to the right, `y` increases downward
- `x` is a fraction of screen width, `y` is a fraction of screen height
- Single-display only (primary monitor)

---

## Core Commands

### Screenshot

```bash
weavgui screenshot
```

Always saves to `screenshot.png` in the current working directory. Always draws cursor markers:

- Red crosshair lines
- Red small box (normalized radius 0.03)
- Green medium box (normalized radius 0.07)
- Blue large box (normalized radius 0.20)

The three concentric boxes are **positioning references** — use them to gauge how far to move the mouse next:

| Target location | Delta range |
|---|---|
| Inside red box | Fine: `±0.03` |
| Between red and green | Medium: `±0.03–0.07` |
| Between green and blue | Coarse: `±0.07–0.20` |
| Outside blue box | Large move — estimate from full screenshot |

The command also prints the current mouse position in normalized coordinates to stdout.

### Mouse Move

```bash
weavgui mouse move '(dx,dy)'
```

Moves the mouse by a **relative delta** in normalized coordinates. The argument uses `(dx,dy)` format — negative values work naturally. Fails if the target would leave the valid range `[0.0, 1.0)`. Prints the start position, end position, and delta to stdout. Automatically saves a screenshot to `screenshot.png`.

### Mouse Move To

```bash
weavgui mouse moveto '(x,y)'
```

Moves the mouse to an **absolute normalized position**. Fails if the position is outside the valid range `[0.0, 1.0)`. Automatically saves a screenshot to `screenshot.png`.

### Mouse Click

```bash
weavgui mouse click         # left click
weavgui mouse doubleclick   # double left click
weavgui mouse rightclick    # right click
```

All clicks happen at the **current cursor position**. A screenshot is automatically saved to `screenshot.png`.

### Keystroke

```bash
weavgui keystroke <keys>
```

Examples: `c`, `ctrl+c`, `command+c`, `shift+a`, `command+z`

A screenshot is automatically saved to `screenshot.png`.

### Pasteboard

```bash
weavgui pasteboard write <text...>   # write to clipboard
weavgui pasteboard read              # read from clipboard
```

---

## Critical Workflow: Precise Mouse Positioning

**Never guess a target coordinate and click immediately.**
**Never perform a blind click.**

Before any click action (`click`, `doubleclick`, `rightclick`), require a **move-then-verify confirmation** that the cursor is truly on target. This avoids false assumptions where the pointer did not move exactly as expected.

Minimum confirmation standard:

- After every mouse move, the auto-screenshot is already written when the command exits; read `screenshot.png` immediately.
- Verify from that screenshot that the crosshair center is on the target.
- Never click immediately after a move command without loading and analyzing the auto-screenshot first.
- If verification is uncertain, do **not** click. Continue the move-and-verify loop.

`mouse move` accepts relative deltas; `mouse moveto` accepts absolute coordinates — both in normalized form `(0.0–1.0)`. The correct approach is an **iterative positioning loop**:

```
screenshot → analyze image → move mouse → (auto-screenshot) → analyze image → move mouse → ... → click
```

### Step-by-step

1. **Take a screenshot** and read the image into context:

   ```bash
   weavgui screenshot
   ```

   Then read `screenshot.png` as an image attachment.

2. **Analyze the screenshot**: Identify the target UI element. Read the cursor marker position from the stdout output (printed automatically). Use the three reference boxes to gauge your delta:
   - Target inside the **red box** (radius 0.03) → fine delta, within `±0.03`
   - Target inside the **green box** (radius 0.07) → medium delta, within `±0.07`
   - Target inside the **blue box** (radius 0.20) → coarse delta, within `±0.20`
   - Target outside the **blue box** → large move, estimate from the full screenshot

3. **Move the mouse**:

   ```bash
   weavgui mouse move '(dx,dy)'
   ```

   When `mouse move` exits, its auto-screenshot is already available at `screenshot.png`. Read it immediately.

4. **Verify position**: Check that the crosshair (red lines) is now centered on the target. If not, repeat from step 2 with a corrected delta.

5. **Click only after the post-move screenshot is loaded and verified (no blind click)**:

   ```bash
   # after mouse move, read auto-captured screenshot.png and verify target alignment
   weavgui mouse click
   ```

   When `mouse click` exits, its auto-screenshot is already available at `screenshot.png`. Read it to confirm the action took effect.

### Why this loop matters

- Even with `mouse moveto`, you need to know the target's normalized position — which requires a screenshot to determine.
- Screen content, window positions, and scroll state can all shift between steps.
- Even a single iteration of screenshot → analyze → move can land the cursor accurately.
- For high-precision targets (small buttons, text fields), two or three iterations are typical.

### Example: clicking a button labeled "Submit"

```bash
# Step 1: initial screenshot
weavgui screenshot
# → read screenshot.png, observe crosshair at (0.2604, 0.3704), Submit button at approx (0.3750, 0.5648)
# → estimate dx=0.1146, dy=0.1944

# Step 2: move toward target (auto-screenshot is ready when command exits)
weavgui mouse move '(0.1146,0.1944)'
# → read screenshot.png, crosshair now at (0.3750, 0.5630) — close enough

# Step 3: click (auto-screenshot is ready when command exits)
weavgui mouse click
# → read screenshot.png to confirm the click took effect
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
1. Run `weavgui screenshot`, then read screenshot.png as an image.
2. Identify the "Submit" button. Read the crosshair position from stdout.
3. Estimate (dx, dy) from the crosshair to the button center, run `weavgui mouse move '(dx,dy)'`.
4. Read `screenshot.png` right after command exit, verify the crosshair is on the button. Adjust if needed.
5. Run `weavgui mouse click`.
6. Read `screenshot.png` right after command exit to confirm the click took effect.

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

- Every action command auto-captures `screenshot.png` — always read it after each command to observe the result.
- Always prefer the **iterative screenshot loop** over single-shot coordinate estimation.
- Never blind-click: after any mouse move, always read and analyze the auto-screenshot before any click.
- After any keyboard shortcut that changes screen state (e.g. `command+z`, `return`), read `screenshot.png` immediately after command exit before proceeding.
- The stdout output of every command includes the current mouse position in normalized coordinates — use this as a precise anchor for the next delta calculation.
