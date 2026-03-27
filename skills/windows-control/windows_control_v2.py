#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Windows-Control V2 - 基于 UFO 架构改进

核心改进：
1. 使用 pywinauto 进行窗口管理
2. 使用 application.set_focus() 正确激活窗口
3. 支持 UI 控件树遍历
4. 支持绝对坐标和相对坐标转换
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

# 添加 jingmai-agent 路径
JM_AGENT_PATH = Path(r"E:\PY\jingmai-agent")
if JM_AGENT_PATH.exists():
    sys.path.insert(0, str(JM_AGENT_PATH))

# 导入 pywinauto
from pywinauto import Application, Desktop
from pywinauto.timings import wait_until_passes, TimeoutError as PywinautoTimeoutError
import pyautogui

# 导入 jingmai-agent 的 screenshot
try:
    from app.service.utils.screenshot import capture_screenshot, compute_image_hash
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False


class WindowsController:
    """改进的 Windows 控制器 - 基于 UFO 架构"""
    
    def __init__(self):
        self.app = None
        self.window = None
        self.process_name = None
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"[Init] Screen size: {self.screen_width}x{self.screen_height}")
    
    def find_window(self, title_keyword: str = None, process_name: str = None):
        """查找窗口"""
        desktop = Desktop(backend="win32")
        windows = desktop.windows()
        
        for w in windows:
            try:
                title = w.window_text()
                if title_keyword and title_keyword.lower() in title.lower():
                    return w
            except:
                continue
        return None
    
    def connect_app(self, process_name: str):
        """连接到应用程序"""
        try:
            self.app = Application(backend="win32").connect(process=process_name)
            self.process_name = process_name
            print(f"[OK] Connected to process: {process_name}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to connect to {process_name}: {e}")
            return False
    
    def connect_window(self, title_keyword: str):
        """通过窗口标题连接"""
        try:
            self.app = Application(backend="win32").connect(title_re=title_keyword)
            self.window = self.app.window(title=title_keyword)
            self.window.set_focus()  # 关键！激活窗口
            print(f"[OK] Connected to window: {title_keyword}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to connect to window '{title_keyword}': {e}")
            return False
    
    def activate_window(self, title_keyword: str = None):
        """激活窗口（带重试机制）"""
        try:
            # 查找窗口
            if title_keyword:
                self.window = self.find_window(title_keyword)
                if self.window:
                    # UFO 风格：使用 set_focus() + wait_enabled()
                    self.window.set_focus()
                    time.sleep(0.2)
                    # 等待窗口变为可用
                    wait_until_passes(3, 0.1, lambda: self.window.is_visible())
                    print(f"[OK] Activated window: {title_keyword}")
                    return True
            
            # 如果没有指定，尝试激活桌面上的所有 Chrome 窗口
            self.window = self.find_window("chrome")
            if self.window:
                self.window.set_focus()
                time.sleep(0.3)
                print(f"[OK] Activated Chrome window")
                return True
                
            print("[FAIL] Window not found")
            return False
        except Exception as e:
            print(f"[FAIL] Activation error: {e}")
            return False
    
    def click(self, x: int, y: int, button: str = "left"):
        """点击指定坐标 - 先激活窗口再点击"""
        try:
            # 确保窗口在前台
            if self.window:
                self.window.set_focus()
                time.sleep(0.1)
            
            # 执行点击
            pyautogui.click(x, y, button=button)
            print(f"[OK] Clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"[FAIL] Click error: {e}")
            return False
    
    def double_click(self, x: int, y: int):
        """双击"""
        try:
            if self.window:
                self.window.set_focus()
                time.sleep(0.1)
            pyautogui.doubleClick(x, y)
            print(f"[OK] Double-clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"[FAIL] Double-click error: {e}")
            return False
    
    def move_mouse(self, x: int, y: int):
        """移动鼠标"""
        try:
            pyautogui.moveTo(x, y, duration=0.2)
            print(f"[OK] Moved mouse to ({x}, {y})")
            return True
        except Exception as e:
            print(f"[FAIL] Move error: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.02):
        """输入文本"""
        try:
            # 确保窗口激活
            if self.window:
                self.window.set_focus()
                time.sleep(0.1)
            
            pyautogui.write(text, interval=interval)
            print(f"[OK] Typed text: {text[:50]}...")
            return True
        except Exception as e:
            print(f"[FAIL] Type error: {e}")
            return False
    
    def press_key(self, key: str):
        """按按键"""
        try:
            if self.window:
                self.window.set_focus()
                time.sleep(0.1)
            pyautogui.press(key)
            print(f"[OK] Pressed key: {key}")
            return True
        except Exception as e:
            print(f"[FAIL] Press key error: {e}")
            return False
    
    def hotkey(self, *keys):
        """组合键"""
        try:
            if self.window:
                self.window.set_focus()
                time.sleep(0.1)
            pyautogui.hotkey(*keys)
            print(f"[OK] Hotkey: {'+'.join(keys)}")
            return True
        except Exception as e:
            print(f"[FAIL] Hotkey error: {e}")
            return False
    
    def screenshot(self, filename: str = None) -> dict:
        """截图"""
        try:
            if SCREENSHOT_AVAILABLE:
                img, width, height = capture_screenshot()
                if img and filename:
                    img.save(filename)
                print(f"[OK] Screenshot: {width}x{height}")
                return {"success": True, "width": width, "height": height, "filename": filename}
            else:
                # 降级使用 pyautogui
                img = pyautogui.screenshot()
                if filename:
                    img.save(filename)
                print(f"[OK] Screenshot saved")
                return {"success": True, "filename": filename}
        except Exception as e:
            print(f"[FAIL] Screenshot error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_ui_tree(self, max_depth: int = 5) -> list:
        """获取 UI 控件树"""
        if not self.window:
            print("[FAIL] No window connected")
            return []
        
        try:
            tree = []
            
            def traverse(element, depth=0, max_d=max_depth):
                if depth > max_d:
                    return
                try:
                    # 尝试获取子元素
                    children = element.children()
                    for child in children[:20]:  # 限制数量
                        try:
                            info = {
                                "depth": depth,
                                "name": child.window_text()[:50] if child.window_text() else "",
                                "class": child.class_name(),
                                "type": child.control_type(),
                            }
                            tree.append(info)
                            # 递归遍历
                            if depth < max_d:
                                traverse(child, depth + 1, max_d)
                        except:
                            continue
                except:
                    pass
            
            traverse(self.window)
            print(f"[OK] UI tree: {len(tree)} elements")
            return tree
        except Exception as e:
            print(f"[FAIL] UI tree error: {e}")
            return []


# 全局控制器实例
_controller = WindowsController()


def cmd_activate_window(args):
    """激活窗口"""
    result = _controller.activate_window(args.title)
    return {"success": result}


def cmd_connect_window(args):
    """连接窗口"""
    result = _controller.connect_window(args.title)
    return {"success": result}


def cmd_click(args):
    """点击"""
    result = _controller.click(args.x, args.y, args.button)
    return {"success": result}


def cmd_double_click(args):
    """双击"""
    result = _controller.double_click(args.x, args.y)
    return {"success": result}


def cmd_move(args):
    """移动鼠标"""
    result = _controller.move_mouse(args.x, args.y)
    return {"success": result}


def cmd_type(args):
    """输入文本"""
    result = _controller.type_text(args.text, args.interval)
    return {"success": result}


def cmd_press_key(args):
    """按键"""
    result = _controller.press_key(args.keys)
    return {"success": result}


def cmd_hotkey(args):
    """组合键"""
    keys = args.keys.split("+")
    result = _controller.hotkey(*keys)
    return {"success": result}


def cmd_screenshot(args):
    """截图"""
    result = _controller.screenshot(args.filename)
    return result


def cmd_get_ui_tree(args):
    """获取 UI 树"""
    tree = _controller.get_ui_tree(args.max_depth)
    return {"success": True, "elements": len(tree), "tree": tree}


def cmd_wait(args):
    """等待"""
    time.sleep(args.seconds)
    print(f"[OK] Waited {args.seconds}s")
    return {"success": True, "waited": args.seconds}


def main():
    parser = argparse.ArgumentParser(description="Windows-Control V2 (基于 UFO 架构)")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 窗口操作
    p = subparsers.add_parser("activate-window", help="激活窗口")
    p.add_argument("--title", default="", help="窗口标题关键词")
    p.set_defaults(func=cmd_activate_window)

    p = subparsers.add_parser("connect-window", help="连接窗口")
    p.add_argument("--title", required=True, help="窗口标题关键词")
    p.set_defaults(func=cmd_connect_window)

    # 鼠标操作
    p = subparsers.add_parser("click", help="点击")
    p.add_argument("--x", type=int, required=True)
    p.add_argument("--y", type=int, required=True)
    p.add_argument("--button", default="left")
    p.set_defaults(func=cmd_click)

    p = subparsers.add_parser("double-click", help="双击")
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

    p = subparsers.add_parser("press-key", help="按键")
    p.add_argument("--keys", required=True)
    p.set_defaults(func=cmd_press_key)

    p = subparsers.add_parser("hotkey", help="组合键")
    p.add_argument("--keys", required=True, help="例如: ctrl+shift+n")
    p.set_defaults(func=cmd_hotkey)

    # 截图
    p = subparsers.add_parser("screenshot", help="截图")
    p.add_argument("--filename", default="screenshot.png")
    p.set_defaults(func=cmd_screenshot)

    # UI 树
    p = subparsers.add_parser("get-ui-tree", help="获取UI控件树")
    p.add_argument("--max-depth", type=int, default=5)
    p.set_defaults(func=cmd_get_ui_tree)

    # 等待
    p = subparsers.add_parser("wait", help="等待")
    p.add_argument("--seconds", type=float, default=2.0)
    p.set_defaults(func=cmd_wait)

    # 解析参数
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # 执行命令
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
