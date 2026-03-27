# cli-anything-windows-control

**Windows UI Automation CLI for AI agents** — Full mouse, keyboard, window, and system control via the jingmai-agent action system.

## Overview

This CLI harness provides AI agents with complete Windows UI automation capabilities:

- **Mouse control**: click, double-click, move, drag (absolute + fractional coordinates)
- **Keyboard control**: type text, press keys, hotkey combinations
- **Scroll**: mouse wheel and scroll at coordinates
- **Window management**: list windows, get window info, open/focus applications
- **UI inspection**: screenshots, UI control trees, control enumeration
- **System operations**: run commands, check processes, get system info
- **File operations**: read, write, list files

## Prerequisites

- Python 3.10+
- Windows 10/11
- jingmai-agent installed at `E:\PY\jingmai-agent`

### Install dependencies

```bash
pip install pyautogui pyperclip Pillow psutil
```

## Installation

```bash
cd agent-harness
pip install -e .
```

Or install the generated CLI directly:

```bash
pip install .
```

## Usage

### One-shot commands

```bash
# Mouse operations
cli-windows-control mouse click --x 100 --y 200
cli-windows-control mouse double-click --x 500 --y 300
cli-windows-control mouse move --x 400 --y 200
cli-windows-control mouse drag --start-x 100 --start-y 100 --end-x 400 --end-y 300

# Keyboard operations
cli-windows-control keyboard type --text "Hello World"
cli-windows-control keyboard press --keys enter
cli-windows-control keyboard hotkey --keys ctrl+c

# Scroll
cli-windows-control scroll scroll --scroll-y -3
cli-windows-control scroll wheel --amount 5

# Window management
cli-windows-control window list
cli-windows-control window info
cli-windows-control window open --name notepad --keyword "notepad"

# UI inspection
cli-windows-control ui screenshot
cli-windows-control ui screenshot --full
cli-windows-control ui tree --depth 10
cli-windows-control ui controls --depth 8

# System operations
cli-windows-control system info
cli-windows-control system run --command "dir" --shell cmd
cli-windows-control system process --name python
cli-windows-control system wait --seconds 2

# File operations
cli-windows-control file list --path C:\ --pattern "*.txt"
cli-windows-control file read --path C:\test.txt --limit 100
cli-windows-control file write --path C:\output.txt --content "Hello"
```

### JSON output (for AI agents)

```bash
cli-windows-control --json mouse click --x 100 --y 200
cli-windows-control --json window list
cli-windows-control --json system info
```

### Interactive REPL

```bash
cli-windows-control
```

## Architecture

```
cli-windows-control
├── windows_control_cli.py   # Main Click CLI (subcommands)
├── utils/
│   └── repl_skin.py         # REPL interface styling
└── core/                    # (reserved for future core modules)
```

Backend: jingmai-agent actions at `E:\PY\jingmai-agent\app\service\actions/`

## Command Groups

| Group | Commands | Description |
|-------|----------|-------------|
| `mouse` | click, double-click, move, drag, click-input, click-fraction, drag-fraction | Mouse control |
| `keyboard` | type, set-text, press, hotkey | Keyboard control |
| `scroll` | scroll, wheel | Scroll operations |
| `window` | list, info, open | Window management |
| `ui` | screenshot, tree, controls, targets | UI inspection |
| `system` | info, run, process, wait | System operations |
| `file` | list, read, write, exists | File operations |

## License

MIT License
