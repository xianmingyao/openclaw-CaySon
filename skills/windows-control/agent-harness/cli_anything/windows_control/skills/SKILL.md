---
name: cli-anything-windows-control
description: Windows UI Automation CLI harness - complete mouse, keyboard, window, system, and UI control via jingmai-agent action system
---

# Windows Control CLI Skill

AI agent skill for controlling Windows through the `cli-windows-control` CLI.

## Installation

```bash
cd agent-harness
pip install -e .
```

## Command Groups

### Mouse Control

```bash
# Click at coordinates
cli-windows-control mouse click --x 100 --y 200

# Double-click
cli-windows-control mouse double-click --x 500 --y 300

# Move cursor
cli-windows-control mouse move --x 400 --y 200

# Drag
cli-windows-control mouse drag --start-x 100 --start-y 100 --end-x 400 --end-y 300

# Control-level click (with modifier key)
cli-windows-control mouse click-input --x 200 --y 150 --pressed CONTROL --double

# Fractional coordinates (0.0-1.0 relative to screen)
cli-windows-control mouse click-fraction --frac-x 0.5 --frac-y 0.5
```

### Keyboard Control

```bash
# Type text
cli-windows-control keyboard type --text "Hello World{ENTER}"

# Press key
cli-windows-control keyboard press --keys enter

# Hotkey combination
cli-windows-control keyboard hotkey --keys ctrl+c
cli-windows-control keyboard hotkey --keys alt+tab
```

### Window Management

```bash
# List all visible windows
cli-windows-control window list

# Get current window details
cli-windows-control window info

# Open or focus an application
cli-windows-control window open --name notepad --keyword "记事本"
```

### UI Inspection

```bash
# Screenshot of active window
cli-windows-control ui screenshot

# Full desktop screenshot
cli-windows-control ui screenshot --full

# Get UI control tree (XML)
cli-windows-control ui tree --depth 10

# List interactive controls
cli-windows-control ui controls --depth 8
```

### System Operations

```bash
# System information
cli-windows-control system info

# Run command
cli-windows-control system run --command "dir" --shell cmd
cli-windows-control system run --command "Get-Process" --shell powershell

# Check process
cli-windows-control system process --name python

# Wait
cli-windows-control system wait --seconds 2
```

### File Operations

```bash
# List files
cli-windows-control file list --path C:\ --pattern "*.txt"

# Read file
cli-windows-control file read --path C:\test.txt --limit 100

# Write file
cli-windows-control file write --path C:\output.txt --content "Hello"

# Check existence
cli-windows-control file exists --path C:\test.txt
```

## JSON Output for AI Agents

Always use `--json` flag for programmatic output:

```bash
cli-windows-control --json window list
cli-windows-control --json system info
cli-windows-control --json ui controls --depth 8
```

## Interactive REPL

```bash
# Enter interactive mode
cli-windows-control

# Then type commands:
windows-control> mouse click --x 100 --y 200
windows-control> keyboard type --text "Hello"
windows-control> quit
```

## Error Handling

- Non-zero exit code on failure
- Error messages in `error` field (JSON mode) or stderr (human mode)
- Always verify coordinates before clicking
- Use `--json` for reliable parsing in scripts
