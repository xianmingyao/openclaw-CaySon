# -*- coding: utf-8 -*-
"""使用pywinauto枚举京麦所有元素"""
from pywinauto import Application, timings
from pywinauto.findwindows import find_window
import win32gui
import time

hwnd = 1250920

print(f"连接京麦窗口: {hwnd}")

# 尝试使用win32 backend
try:
    app = Application(backend='win32').connect(handle=hwnd)
    print("Win32连接成功")
    
    dlg = app.window(handle=hwnd)
    print(f"窗口: {dlg.window_text()}")
    
    # 枚举所有子窗口
    print("\n=== 所有子窗口 ===")
    
    def print_window(hwnd, indent=0):
        try:
            text = win32gui.GetWindowText(hwnd)
            cls = win32gui.GetClassName(hwnd)
            if text or 'Edit' in cls or 'Button' in cls or 'Static' in cls:
                print("  " * indent + f"[{hwnd}] {cls}: {text[:50] if text else '(empty)'}")
        except:
            pass
    
    # 只打印直接子窗口
    def enum_child_proc(hwnd, ctx):
        print_window(hwnd, 1)
        return True
    
    win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
