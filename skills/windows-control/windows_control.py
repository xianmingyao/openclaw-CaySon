#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Windows-Control Action 调用封装

提供简化的 action 调用接口，支持直接通过命令行调用 jingmai-agent 的 actions。

Usage:
    python windows_control.py click --x 100 --y 200
    python windows_control.py type --text "Hello World"
    python windows_control.py open_app --app_name notepad
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

# 添加 jingmai-agent 路径
JM_AGENT_PATH = Path(r"E:\PY\jingmai-agent")
if JM_AGENT_PATH.exists():
    sys.path.insert(0, str(JM_AGENT_PATH))


def run_action(action_class, action_name: str, **kwargs):
    """同步运行 action"""
    try:
        action = action_class()
        action.set_context(1.0, (1920, 1080))
        result = asyncio.run(action.execute(**kwargs))
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def print_result(result: dict):
    """格式化打印结果"""
    if result.get("success"):
        print(f"✅ {result}")
    else:
        print(f"❌ {result}")


# ==================== 鼠标操作 ====================

def cmd_click(args):
    from app.service.actions.mouse_actions import ClickAction
    result = run_action(ClickAction, "click", x=args.x, y=args.y, button=args.button)
    print_result(result)


def cmd_double_click(args):
    from app.service.actions.mouse_actions import DoubleClickAction
    result = run_action(DoubleClickAction, "double_click", x=args.x, y=args.y)
    print_result(result)


def cmd_click_input(args):
    from app.service.actions.mouse_actions import ClickInputAction
    result = run_action(ClickInputAction, "click_input",
                       x=args.x, y=args.y, button=args.button,
                       double=args.double, pressed=args.pressed)
    print_result(result)


def cmd_click_on_coordinates(args):
    from app.service.actions.mouse_actions import ClickOnCoordinatesAction
    result = run_action(ClickOnCoordinatesAction, "click_on_coordinates",
                       frac_x=args.frac_x, frac_y=args.frac_y,
                       button=args.button, double=args.double)
    print_result(result)


def cmd_move(args):
    from app.service.actions.mouse_actions import MoveAction
    result = run_action(MoveAction, "move", x=args.x, y=args.y)
    print_result(result)


def cmd_drag(args):
    from app.service.actions.mouse_actions import DragAction
    result = run_action(DragAction, "drag",
                       start_x=args.start_x, start_y=args.start_y,
                       end_x=args.end_x, end_y=args.end_y,
                       duration=args.duration)
    print_result(result)


def cmd_drag_on_coordinates(args):
    from app.service.actions.mouse_actions import DragOnCoordinatesAction
    result = run_action(DragOnCoordinatesAction, "drag_on_coordinates",
                       start_frac_x=args.start_frac_x, start_frac_y=args.start_frac_y,
                       end_frac_x=args.end_frac_x, end_frac_y=args.end_frac_y,
                       duration=args.duration, button=args.button, key_hold=args.key_hold)
    print_result(result)


# ==================== 键盘操作 ====================

def cmd_type(args):
    from app.service.actions.keyboard_actions import TypeAction
    result = run_action(TypeAction, "type", text=args.text, interval=args.interval)
    print_result(result)


def cmd_set_edit_text(args):
    from app.service.actions.keyboard_actions import SetEditTextAction
    result = run_action(SetEditTextAction, "set_edit_text",
                       text=args.text, clear_current_text=args.clear)
    print_result(result)


def cmd_keyboard_input(args):
    from app.service.actions.keyboard_actions import KeyboardInputAction
    result = run_action(KeyboardInputAction, "keyboard_input", keys=args.keys)
    print_result(result)


def cmd_keypress(args):
    from app.service.actions.keyboard_actions import KeypressAction
    result = run_action(KeypressAction, "keypress", keys=args.keys)
    print_result(result)


# ==================== 滚动操作 ====================

def cmd_scroll(args):
    from app.service.actions.scroll_actions import ScrollAction
    result = run_action(ScrollAction, "scroll",
                       scroll_x=args.scroll_x, scroll_y=args.scroll_y,
                       x=args.x, y=args.y)
    print_result(result)


def cmd_wheel_mouse_input(args):
    from app.service.actions.scroll_actions import WheelMouseInputAction
    result = run_action(WheelMouseInputAction, "wheel_mouse_input", wheel_dist=args.wheel_dist)
    print_result(result)


# ==================== 窗口操作 ====================

def cmd_open_app(args):
    from app.service.actions.window_actions import OpenAppAction
    result = run_action(OpenAppAction, "open_app",
                       app_name=args.app_name, search_keyword=args.search_keyword)
    print_result(result)


# ==================== 系统操作 ====================

def cmd_wait(args):
    from app.service.actions.system_actions import WaitAction
    result = run_action(WaitAction, "wait", seconds=args.seconds)
    print_result(result)


def cmd_run_command(args):
    from app.service.actions.system_actions import RunCommandAction
    result = run_action(RunCommandAction, "run_command",
                       command=args.command, shell=args.shell)
    print_result(result)


def cmd_check_process(args):
    from app.service.actions.system_actions import CheckProcessAction
    result = run_action(CheckProcessAction, "check_process", process_name=args.process_name)
    print_result(result)


def cmd_no_action(args):
    from app.service.actions.system_actions import NoAction
    result = run_action(NoAction, "no_action")
    print_result(result)


# ==================== UI 采集 ====================

def cmd_get_desktop_app_info(args):
    from app.service.actions.ui_collect_actions import GetDesktopAppInfoAction
    result = run_action(GetDesktopAppInfoAction, "get_desktop_app_info")
    print_result(result)


def cmd_capture_window_screenshot(args):
    from app.service.actions.ui_collect_actions import CaptureWindowScreenshotAction
    result = run_action(CaptureWindowScreenshotAction, "capture_window_screenshot")
    if result.get("success"):
        print(f"✅ Screenshot captured: {result['data']['width']}x{result['data']['height']}")
    else:
        print(f"❌ {result}")


def cmd_capture_desktop_screenshot(args):
    from app.service.actions.ui_collect_actions import CaptureDesktopScreenshotAction
    result = run_action(CaptureDesktopScreenshotAction, "capture_desktop_screenshot")
    if result.get("success"):
        print(f"✅ Screenshot captured: {result['data']['width']}x{result['data']['height']}")
    else:
        print(f"❌ {result}")


def cmd_get_app_window_info(args):
    from app.service.actions.ui_collect_actions import GetAppWindowInfoAction
    result = run_action(GetAppWindowInfoAction, "get_app_window_info")
    print_result(result)


def cmd_get_ui_tree(args):
    from app.service.actions.ui_collect_actions import GetUITreeAction
    result = run_action(GetUITreeAction, "get_ui_tree", max_depth=args.max_depth)
    print_result(result)


# ==================== 文件操作 ====================

def cmd_list_files(args):
    from app.service.actions.shell_actions import ListFilesAction
    result = run_action(ListFilesAction, "list_files",
                       path=args.path, pattern=args.pattern, recursive=args.recursive)
    print_result(result)


def cmd_read_file(args):
    from app.service.actions.shell_actions import ReadFileAction
    result = run_action(ReadFileAction, "read_file",
                       path=args.path, encoding=args.encoding,
                       offset=args.offset, limit=args.limit)
    print_result(result)


def cmd_write_file(args):
    from app.service.actions.shell_actions import WriteFileAction
    result = run_action(WriteFileAction, "write_file",
                       path=args.path, content=args.content, append=args.append)
    print_result(result)


def cmd_check_file_exists(args):
    from app.service.actions.shell_actions import CheckFileExistsAction
    result = run_action(CheckFileExistsAction, "check_file_exists", path=args.path)
    print_result(result)


def cmd_get_system_info(args):
    from app.service.actions.shell_actions import GetSystemInfoAction
    result = run_action(GetSystemInfoAction, "get_system_info")
    print_result(result)


# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(description="Windows-Control Action 调用工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 鼠标操作
    p = subparsers.add_parser("click", help="点击指定坐标")
    p.add_argument("--x", type=int, required=True)
    p.add_argument("--y", type=int, required=True)
    p.add_argument("--button", default="left")
    p.set_defaults(func=cmd_click)

    p = subparsers.add_parser("double-click", help="双击指定坐标")
    p.add_argument("--x", type=int, required=True)
    p.add_argument("--y", type=int, required=True)
    p.set_defaults(func=cmd_double_click)

    p = subparsers.add_parser("move", help="移动鼠标")
    p.add_argument("--x", type=int, required=True)
    p.add_argument("--y", type=int, required=True)
    p.set_defaults(func=cmd_move)

    # 键盘操作
    p = subparsers.add_parser("type", help="输入文本")
    p.add_argument("--text", required=True)
    p.add_argument("--interval", type=float, default=0.02)
    p.set_defaults(func=cmd_type)

    p = subparsers.add_parser("keypress", help="按键")
    p.add_argument("--keys", required=True)
    p.set_defaults(func=cmd_keypress)

    p = subparsers.add_parser("keyboard-input", help="键盘组合键")
    p.add_argument("--keys", required=True)
    p.set_defaults(func=cmd_keyboard_input)

    # 窗口操作
    p = subparsers.add_parser("open-app", help="打开应用")
    p.add_argument("--app-name", required=True)
    p.add_argument("--search-keyword", default="")
    p.set_defaults(func=cmd_open_app)

    # 系统操作
    p = subparsers.add_parser("wait", help="等待")
    p.add_argument("--seconds", type=float, default=2.0)
    p.set_defaults(func=cmd_wait)

    p = subparsers.add_parser("run-command", help="执行命令")
    p.add_argument("--command", required=True)
    p.add_argument("--shell", default="cmd")
    p.set_defaults(func=cmd_run_command)

    p = subparsers.add_parser("check-process", help="检查进程")
    p.add_argument("--process-name", required=True)
    p.set_defaults(func=cmd_check_process)

    # UI 采集
    p = subparsers.add_parser("get-desktop-app-info", help="获取桌面窗口信息")
    p.set_defaults(func=cmd_get_desktop_app_info)

    p = subparsers.add_parser("capture-window-screenshot", help="截取活动窗口")
    p.set_defaults(func=cmd_capture_window_screenshot)

    p = subparsers.add_parser("capture-desktop-screenshot", help="截取桌面")
    p.set_defaults(func=cmd_capture_desktop_screenshot)

    p = subparsers.add_parser("get-app-window-info", help="获取活动窗口信息")
    p.set_defaults(func=cmd_get_app_window_info)

    p = subparsers.add_parser("get-ui-tree", help="获取UI控件树")
    p.add_argument("--max-depth", type=int, default=10)
    p.set_defaults(func=cmd_get_ui_tree)

    # 文件操作
    p = subparsers.add_parser("list-files", help="列出文件")
    p.add_argument("--path", default=".")
    p.add_argument("--pattern", default="*")
    p.add_argument("--recursive", action="store_true")
    p.set_defaults(func=cmd_list_files)

    p = subparsers.add_parser("read-file", help="读取文件")
    p.add_argument("--path", required=True)
    p.add_argument("--encoding", default="utf-8")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=500)
    p.set_defaults(func=cmd_read_file)

    p = subparsers.add_parser("write-file", help="写入文件")
    p.add_argument("--path", required=True)
    p.add_argument("--content", required=True)
    p.add_argument("--append", action="store_true")
    p.set_defaults(func=cmd_write_file)

    p = subparsers.add_parser("check-file-exists", help="检查文件存在")
    p.add_argument("--path", required=True)
    p.set_defaults(func=cmd_check_file_exists)

    p = subparsers.add_parser("get-system-info", help="获取系统信息")
    p.set_defaults(func=cmd_get_system_info)

    # 解析参数
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # 执行命令
    args.func(args)


if __name__ == "__main__":
    main()
