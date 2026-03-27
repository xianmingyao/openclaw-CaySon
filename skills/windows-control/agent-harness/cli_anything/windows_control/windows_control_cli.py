#!/usr/bin/env python3
"""
Windows Control CLI — Command-line interface for Windows UI automation.

This CLI provides full access to Windows automation capabilities:
- Mouse control (click, double-click, drag, move)
- Keyboard control (type, keypress, hotkeys)
- Window management (list, activate, open apps)
- System operations (run command, check process, wait)
- UI information (screenshot, window info, controls)

Usage:
    # One-shot commands
    cli-anything-windows-control mouse click --x 100 --y 200
    cli-anything-windows-control keyboard type --text "Hello"
    cli-anything-windows-control window list
    cli-anything-windows-control ui screenshot
    cli-anything-windows-control system info
    cli-anything-windows-control --json mouse click --x 500 --y 300

    # Interactive REPL
    cli-anything-windows-control
"""

import sys
import os
import json
import asyncio

# Add jingmai-agent path for import
_JINGMAI_PATH = r"E:\PY\jingmai-agent"
if os.path.exists(_JINGMAI_PATH) and _JINGMAI_PATH not in sys.path:
    sys.path.insert(0, _JINGMAI_PATH)
    # Suppress jingmai-agent loguru logs to avoid stderr noise in PowerShell
    os.environ["LOGURU_LEVEL"] = "ERROR"

import click
from typing import Optional

# Global state
_json_output = False
_repl_mode = False
_last_result = None


# ── Output Helpers ────────────────────────────────────────────────────────────

def output(data, message: str = ""):
    """Print output in JSON or human-readable format."""
    if _json_output:
        click.echo(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def _run_action(action_class, **kwargs):
    """Run a jingmai-agent action and return normalized result."""
    import subprocess, json
    # Use subprocess to isolate stderr (PowerShell treats stderr as error)
    # Build a one-liner that runs the action and outputs JSON
    import_module = action_class.__module__
    class_name = action_class.__name__
    kwargs_str = json.dumps(kwargs, ensure_ascii=False, default=str)

    script = f"""
import sys, os, asyncio, json
sys.path.insert(0, r'{_JINGMAI_PATH}')
os.environ['LOGURU_LEVEL'] = 'ERROR'
sys.stderr = open(os.devnull, 'w')
try:
    from {import_module} import {class_name}
    action = {class_name}()
    action.set_context(1.0, (1920, 1080))
    result = asyncio.run(action.execute(**{kwargs_str}))
    sys.stderr.close()
    output = json.dumps({{
        'success': result.success,
        'data': json.loads(result.data.json()) if hasattr(result.data, 'json') else result.data,
        'error': result.error,
        'metadata': {{k: str(v) for k, v in result.metadata.items()}} if result.metadata else {{}}
    }}, ensure_ascii=False, default=str)
    sys.stdout.write(output)
except Exception as e:
    sys.stderr.close()
    sys.stdout.write(json.dumps({{'success': False, 'error': str(e)}}))
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace"
        )
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        else:
            return {"success": False, "error": f"No output: {result.stderr[:200]}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Action timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _handle_result(result: dict, success_msg: str = ""):
    """Handle action result with proper output."""
    global _last_result
    _last_result = result

    if result.get("success"):
        if _json_output:
            output(result)
        else:
            if success_msg and result.get("metadata"):
                click.echo(f"[OK] {success_msg}")
                for k, v in result["metadata"].items():
                    click.echo(f"  {k}: {v}")
            elif result.get("data"):
                output(result["data"])
            else:
                click.echo(f"[OK] {success_msg or 'Success'}")
    else:
        error_msg = result.get("error", "Unknown error")
        if _json_output:
            output(result)
        else:
            click.echo(f"[FAIL] {error_msg}", err=True)
        if not _repl_mode:
            sys.exit(1)


# ── Main CLI Group ────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON for agent consumption")
@click.pass_context
def cli(ctx, use_json):
    """Windows Control CLI — Full Windows UI automation for AI agents.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Mouse Commands ─────────────────────────────────────────────────────────────

@cli.group()
def mouse():
    """Mouse control commands (click, move, drag)."""
    pass


@mouse.command("click")
@click.option("--x", type=int, required=True, help="X coordinate")
@click.option("--y", type=int, required=True, help="Y coordinate")
@click.option("--button", default="left", help="Mouse button: left/right/middle")
def mouse_click(x, y, button):
    """Click at specified screen coordinates."""
    from app.service.actions.mouse_actions import ClickAction
    result = _run_action(ClickAction, x=x, y=y, button=button)
    _handle_result(result, f"Clicked at ({x}, {y}) with {button} button")


@mouse.command("double-click")
@click.option("--x", type=int, required=True, help="X coordinate")
@click.option("--y", type=int, required=True, help="Y coordinate")
def mouse_double_click(x, y):
    """Double-click at specified screen coordinates."""
    from app.service.actions.mouse_actions import DoubleClickAction
    result = _run_action(DoubleClickAction, x=x, y=y)
    _handle_result(result, f"Double-clicked at ({x}, {y})")


@mouse.command("move")
@click.option("--x", type=int, required=True, help="X coordinate")
@click.option("--y", type=int, required=True, help="Y coordinate")
def mouse_move(x, y):
    """Move mouse cursor to specified coordinates."""
    from app.service.actions.mouse_actions import MoveAction
    result = _run_action(MoveAction, x=x, y=y)
    _handle_result(result, f"Moved to ({x}, {y})")


@mouse.command("drag")
@click.option("--start-x", type=int, required=True, help="Start X coordinate")
@click.option("--start-y", type=int, required=True, help="Start Y coordinate")
@click.option("--end-x", type=int, required=True, help="End X coordinate")
@click.option("--end-y", type=int, required=True, help="End Y coordinate")
@click.option("--duration", type=float, default=0.5, help="Drag duration in seconds")
def mouse_drag(start_x, start_y, end_x, end_y, duration):
    """Drag from start coordinates to end coordinates."""
    from app.service.actions.mouse_actions import DragAction
    result = _run_action(
        DragAction,
        start_x=start_x, start_y=start_y,
        end_x=end_x, end_y=end_y,
        duration=duration
    )
    _handle_result(result, f"Dragged from ({start_x},{start_y}) to ({end_x},{end_y})")


@mouse.command("click-input")
@click.option("--x", type=int, required=True, help="X coordinate")
@click.option("--y", type=int, required=True, help="Y coordinate")
@click.option("--button", default="left", help="Mouse button")
@click.option("--double", is_flag=True, help="Perform double-click")
@click.option("--pressed", default="", help="Modifier key to hold (CONTROL/SHIFT/ALT)")
def mouse_click_input(x, y, button, double, pressed):
    """Control-level click with modifier key support."""
    from app.service.actions.mouse_actions import ClickInputAction
    result = _run_action(
        ClickInputAction,
        x=x, y=y, button=button,
        double=double, pressed=pressed.upper() if pressed else ""
    )
    _handle_result(result, f"Control-clicked at ({x}, {y})")


@mouse.command("click-fraction")
@click.option("--frac-x", type=float, required=True, help="Fractional X (0.0-1.0)")
@click.option("--frac-y", type=float, required=True, help="Fractional Y (0.0-1.0)")
@click.option("--button", default="left", help="Mouse button")
@click.option("--double", is_flag=True, help="Perform double-click")
def mouse_click_fraction(frac_x, frac_y, button, double):
    """Click using fractional coordinates (0.0-1.0 relative to screen)."""
    from app.service.actions.mouse_actions import ClickOnCoordinatesAction
    result = _run_action(
        ClickOnCoordinatesAction,
        frac_x=frac_x, frac_y=frac_y,
        button=button, double=double
    )
    _handle_result(result, f"Clicked at fraction ({frac_x:.2f}, {frac_y:.2f})")


@mouse.command("drag-fraction")
@click.option("--start-frac-x", type=float, required=True)
@click.option("--start-frac-y", type=float, required=True)
@click.option("--end-frac-x", type=float, required=True)
@click.option("--end-frac-y", type=float, required=True)
@click.option("--duration", type=float, default=0.5)
@click.option("--key-hold", default="", help="Modifier key to hold during drag")
def mouse_drag_fraction(start_frac_x, start_frac_y, end_frac_x, end_frac_y, duration, key_hold):
    """Drag using fractional coordinates with modifier key support."""
    from app.service.actions.mouse_actions import DragOnCoordinatesAction
    result = _run_action(
        DragOnCoordinatesAction,
        start_frac_x=start_frac_x, start_frac_y=start_frac_y,
        end_frac_x=end_frac_x, end_frac_y=end_frac_y,
        duration=duration, key_hold=key_hold.upper() if key_hold else ""
    )
    _handle_result(result, "Dragged with fractional coordinates")


# ── Keyboard Commands ─────────────────────────────────────────────────────────

@cli.group()
def keyboard():
    """Keyboard control commands (type, press, hotkey)."""
    pass


@keyboard.command("type")
@click.option("--text", required=True, help="Text to type")
@click.option("--interval", type=float, default=0.02, help="Key interval in seconds")
def keyboard_type(text, interval):
    """Type text (supports Unicode via clipboard)."""
    from app.service.actions.keyboard_actions import TypeAction
    preview = text[:30] + "..." if len(text) > 30 else text
    result = _run_action(TypeAction, text=text, interval=interval)
    _handle_result(result, f"Typed: '{preview}'")


@keyboard.command("set-text")
@click.option("--text", required=True, help="Text to input")
@click.option("--clear", is_flag=True, help="Clear current text before typing")
def keyboard_set_text(text, clear):
    """Input text into focused text box (click to focus first)."""
    from app.service.actions.keyboard_actions import SetEditTextAction
    result = _run_action(SetEditTextAction, text=text, clear_current_text=clear)
    _handle_result(result, f"Set text: '{text[:30]}'")


@keyboard.command("press")
@click.option("--keys", required=True, help="Key name (enter, tab, escape, etc.)")
def keyboard_press(keys):
    """Press a single key or key combination."""
    from app.service.actions.keyboard_actions import KeypressAction
    result = _run_action(KeypressAction, keys=keys.lower())
    _handle_result(result, f"Pressed: {keys}")


@keyboard.command("hotkey")
@click.option("--keys", required=True, help="Key combination (e.g., ctrl+c, alt+tab)")
def keyboard_hotkey(keys):
    """Simulate keyboard hotkey combination."""
    from app.service.actions.keyboard_actions import KeyboardInputAction
    result = _run_action(KeyboardInputAction, keys=keys.lower())
    _handle_result(result, f"Hotkey: {keys}")


# ── Scroll Commands ───────────────────────────────────────────────────────────

@cli.group()
def scroll():
    """Mouse wheel / scroll commands."""
    pass


@scroll.command("scroll")
@click.option("--x", type=int, default=0, help="X coordinate for scroll position")
@click.option("--y", type=int, default=0, help="Y coordinate for scroll position")
@click.option("--scroll-x", type=int, default=0, help="Horizontal scroll amount")
@click.option("--scroll-y", type=int, default=-3, help="Vertical scroll amount (negative=down)")
def scroll_at(x, y, scroll_x, scroll_y):
    """Scroll at specified coordinates."""
    from app.service.actions.scroll_actions import ScrollAction
    result = _run_action(
        ScrollAction,
        scroll_x=scroll_x, scroll_y=scroll_y,
        x=x, y=y
    )
    _handle_result(result, f"Scrolled at ({x},{y}): {scroll_x},{scroll_y}")


@scroll.command("wheel")
@click.option("--amount", type=int, required=True, help="Scroll amount (negative=down)")
def scroll_wheel(amount):
    """Scroll mouse wheel at current cursor position."""
    from app.service.actions.scroll_actions import WheelMouseInputAction
    result = _run_action(WheelMouseInputAction, wheel_dist=amount)
    _handle_result(result, f"Wheel scrolled: {amount}")


# ── Window Commands ───────────────────────────────────────────────────────────

@cli.group()
def window():
    """Window management commands (list, activate, open)."""
    pass


@window.command("list")
def window_list():
    """List all visible desktop windows."""
    import io, contextlib
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    try:
        import ctypes

        USER32 = ctypes.windll.user32
        WM_GETTEXT = 0x000D
        WM_GETTEXTLENGTH = 0x000E

        class RECT(ctypes.Structure):
            _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                         ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

        windows = []
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def collect(hwnd, _):
            try:
                if USER32.IsWindowVisible(hwnd):
                    length = USER32.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        USER32.SendMessageW(hwnd, WM_GETTEXT, length + 1, buf)
                        title = buf.value.strip()
                        if title:
                            rect = RECT()
                            USER32.GetWindowRect(hwnd, ctypes.byref(rect))
                            pid = ctypes.c_ulong()
                            USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                            windows.append({
                                "title": title,
                                "pid": pid.value,
                                "left": rect.left,
                                "top": rect.top,
                                "width": rect.right - rect.left,
                                "height": rect.bottom - rect.top,
                            })
            except Exception:
                pass
            return True

        USER32.EnumWindows(WNDENUMPROC(collect), 0)

        if _json_output:
            output({"success": True, "data": {"windows": windows, "count": len(windows)}})
        else:
            click.echo(f"{'TITLE':<45} {'PID':<8} {'W':<6} {'H':<6}")
            click.echo("-" * 75)
            for app in windows[:30]:
                title = (app.get("title", "") or "")[:44]
                pid = str(app.get("pid", ""))
                w = str(app.get("width", ""))
                h = str(app.get("height", ""))
                click.echo(f"{title:<45} {pid:<8} {w:<6} {h:<6}")
            click.echo(f"\nTotal: {len(windows)} windows")
    except Exception as e:
        _handle_result({"success": False, "error": str(e)})
    finally:
        sys.stderr = old_stderr


@window.command("info")
def window_info():
    """Get current foreground window details."""
    from app.service.actions.ui_collect_actions import GetAppWindowInfoAction
    result = _run_action(GetAppWindowInfoAction)
    _handle_result(result, "Foreground window info")


@window.command("open")
@click.option("--name", required=True, help="Application name or process name")
@click.option("--keyword", default="", help="Search keyword for the app")
def window_open(name, keyword):
    """Open or focus an application."""
    from app.service.actions.window_actions import OpenAppAction
    result = _run_action(OpenAppAction, app_name=name, search_keyword=keyword or name)
    _handle_result(result, f"Opened/focused: {name}")


# ── UI Commands ───────────────────────────────────────────────────────────────

@cli.group()
def ui():
    """UI information and capture commands."""
    pass


@ui.command("screenshot")
@click.option("--full", is_flag=True, help="Capture full desktop instead of active window")
def ui_screenshot(full):
    """Capture a screenshot of the active window or full desktop."""
    import base64
    from io import BytesIO
    try:
        import pyautogui
        img = pyautogui.screenshot()
        if img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            if _json_output:
                output({"success": True, "data": {"screenshot_base64": img_b64, "width": img.width, "height": img.height}})
            else:
                click.echo(f"[OK] Screenshot captured: {img.width}x{img.height}")
                click.echo(f"  Base64 size: {len(img_b64)} chars")
        else:
            _handle_result({"success": False, "error": "Screenshot failed"})
    except Exception as e:
        _handle_result({"success": False, "error": str(e)})


@ui.command("tree")
@click.option("--depth", type=int, default=10, help="Maximum traversal depth")
def ui_tree(depth):
    """Get UI control tree of the foreground window (XML format)."""
    from app.service.actions.ui_collect_actions import GetUITreeAction
    result = _run_action(GetUITreeAction, max_depth=depth)
    if result.get("success"):
        if _json_output:
            output(result)
        else:
            tree = result.get("data", {}).get("ui_tree", "")
            click.echo(tree if tree else "(no UI tree available)")
    else:
        _handle_result(result)


@ui.command("controls")
@click.option("--depth", type=int, default=8, help="Maximum traversal depth")
def ui_controls(depth):
    """Get all interactive UI controls in the foreground window."""
    from app.service.actions.ui_collect_actions import GetAppWindowControlsInfoAction
    result = _run_action(GetAppWindowControlsInfoAction, max_depth=depth)
    if result.get("success"):
        controls = result.get("data", {}).get("controls", [])
        if _json_output:
            output(result)
        else:
            click.echo(f"{'NAME':<40} {'TYPE':<25} {'ENABLED':<8} {'AUTOMATION_ID'}")
            click.echo("-" * 110)
            for ctrl in controls[:50]:
                name = (ctrl.get("name", "") or "")[:39]
                ctype = (ctrl.get("control_type", "") or "").replace("ControlType.", "")
                enabled = "Yes" if ctrl.get("is_enabled") else "No"
                aid = ctrl.get("automation_id", "")[:20]
                click.echo(f"{name:<40} {ctype:<25} {enabled:<8} {aid}")
            click.echo(f"\nTotal: {len(controls)} controls")
    else:
        _handle_result(result)


@ui.command("targets")
@click.option("--depth", type=int, default=8, help="Maximum traversal depth")
def ui_targets(depth):
    """Get window controls as TargetInfo format for App Agent selection."""
    from app.service.actions.ui_collect_actions import GetAppWindowControlsTargetInfoAction
    result = _run_action(GetAppWindowControlsTargetInfoAction, max_depth=depth)
    _handle_result(result, "TargetInfo list")


# ── System Commands ────────────────────────────────────────────────────────────

@cli.group()
def system():
    """System operations (process, command, info)."""
    pass


@system.command("info")
def system_info():
    """Get system information (OS, CPU, memory, hostname)."""
    from app.service.actions.shell_actions import GetSystemInfoAction
    result = _run_action(GetSystemInfoAction)
    _handle_result(result, "System info")


@system.command("run")
@click.option("--command", required=True, help="Command to execute")
@click.option("--shell", default="cmd", help="Shell type: cmd or powershell")
def system_run(command, shell):
    """Execute a system command."""
    from app.service.actions.system_actions import RunCommandAction
    result = _run_action(RunCommandAction, command=command, shell=shell)
    if result.get("success"):
        if _json_output:
            output(result)
        else:
            stdout = result.get("data", {}).get("stdout", "")
            stderr = result.get("data", {}).get("stderr", "")
            if stdout:
                click.echo(stdout)
            if stderr:
                click.echo(f"[stderr] {stderr}", err=True)
    else:
        _handle_result(result)


@system.command("process")
@click.option("--name", required=True, help="Process name (supports wildcards)")
def system_process(name):
    """Check if a process is running."""
    from app.service.actions.system_actions import CheckProcessAction
    result = _run_action(CheckProcessAction, process_name=name)
    if result.get("success"):
        info = result.get("data", {}).get("process_info", {})
        running = info.get("running", False)
        count = info.get("match_count", 0)
        if _json_output:
            output(result)
        else:
            if running:
                click.echo(f"[OK] Process '{name}' is running ({count} instance(s))")
                for p in info.get("processes", []):
                    click.echo(f"  PID {p.get('pid')}: {p.get('name')}")
            else:
                click.echo(f"[OK] Process '{name}' is NOT running")
    else:
        _handle_result(result)


@system.command("wait")
@click.option("--seconds", type=float, default=2.0, help="Wait duration in seconds")
def system_wait(seconds):
    """Wait for specified duration."""
    from app.service.actions.system_actions import WaitAction
    result = _run_action(WaitAction, seconds=seconds)
    _handle_result(result, f"Waited {seconds} seconds")


# ── File Commands ─────────────────────────────────────────────────────────────

@cli.group()
def file():
    """File system operations (read, write, list)."""
    pass


@file.command("list")
@click.option("--path", default=".", help="Directory path")
@click.option("--pattern", default="*", help="File pattern (e.g., *.py)")
@click.option("--recursive", is_flag=True, help="Recursive listing")
def file_list(path, pattern, recursive):
    """List files in a directory."""
    from app.service.actions.shell_actions import ListFilesAction
    result = _run_action(ListFilesAction, path=path, pattern=pattern, recursive=recursive)
    if result.get("success"):
        items = result.get("data", {}).get("items", [])
        if _json_output:
            output(result)
        else:
            for item in items[:100]:
                flag = "[D]" if item.get("is_dir") else "[F]"
                size = item.get("size", 0)
                name = item.get("name", "")
                click.echo(f"{flag} {size:>10}  {name}")
            click.echo(f"\nTotal: {len(items)} items")
    else:
        _handle_result(result)


@file.command("read")
@click.option("--path", required=True, help="File path to read")
@click.option("--encoding", default="utf-8", help="Text encoding")
@click.option("--limit", type=int, default=500, help="Maximum lines to read")
def file_read(path, encoding, limit):
    """Read file contents."""
    from app.service.actions.shell_actions import ReadFileAction
    result = _run_action(ReadFileAction, path=path, encoding=encoding, offset=0, limit=limit)
    _handle_result(result, f"Read: {path}")


@file.command("write")
@click.option("--path", required=True, help="File path to write")
@click.option("--content", required=True, help="Content to write")
@click.option("--append", is_flag=True, help="Append instead of overwrite")
def file_write(path, content, append):
    """Write content to a file."""
    from app.service.actions.shell_actions import WriteFileAction
    result = _run_action(WriteFileAction, path=path, content=content, append=append)
    mode = "Appended" if append else "Written"
    _handle_result(result, f"{mode} to: {path}")


@file.command("exists")
@click.option("--path", required=True, help="File or directory path")
def file_exists(path):
    """Check if a file or directory exists."""
    from app.service.actions.shell_actions import CheckFileExistsAction
    result = _run_action(CheckFileExistsAction, path=path)
    if result.get("success"):
        exists = result.get("data", {}).get("exists", False)
        if _json_output:
            output(result)
        else:
            click.echo(f"[OK] {'Exists' if exists else 'Does NOT exist'}: {path}")
    else:
        _handle_result(result)


# ── REPL ───────────────────────────────────────────────────────────────────────

@cli.command()
def repl():
    """Start interactive REPL session."""
    try:
        from cli_anything.windows_control.utils.repl_skin import ReplSkin
    except ImportError:
        # Fallback if repl_skin not available
        click.echo("Starting basic REPL mode...")
        while True:
            try:
                line = input("windows-control> ").strip()
                if line.lower() in ("quit", "exit", "q"):
                    break
                if not line:
                    continue
                click.echo(f"Use: cli-anything-windows-control {line}")
            except (EOFError, KeyboardInterrupt):
                break
        return

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("windows-control", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_help = {
        "mouse click": "click --x <x> --y <y> [--button left|right]",
        "mouse move": "move --x <x> --y <y>",
        "mouse drag": "drag --start-x <x> --start-y <y> --end-x <x> --end-y <y>",
        "keyboard type": "type --text '<text>'",
        "keyboard press": "press --keys <keyname>",
        "keyboard hotkey": "hotkey --keys <ctrl+c>",
        "scroll": "scroll --scroll-y <amount>",
        "window list": "list",
        "window open": "open --name <appname>",
        "ui screenshot": "screenshot [--full]",
        "ui tree": "tree [--depth 10]",
        "ui controls": "controls [--depth 8]",
        "system info": "info",
        "system run": "run --command '<cmd>' [--shell powershell]",
        "system process": "process --name <procname>",
        "system wait": "wait --seconds <n>",
        "file list": "list --path <path> [--pattern *.py]",
        "file read": "read --path <filepath>",
        "file write": "write --path <filepath> --content '<text>'",
        "help": "Show this help",
        "quit": "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, project_name="", modified=False)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() in ("help", "?"):
                skin.help(_repl_help)
                continue

            # Parse command
            parts = line.split()
            if not parts:
                continue

            # Auto-prepend group if needed
            cmd = parts[0].lower()
            if cmd not in ("mouse", "keyboard", "scroll", "window", "ui", "system", "file"):
                skin.warning(f"Unknown command: {cmd}. Type 'help' for available commands.")
                continue

            try:
                cli.main(parts, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
