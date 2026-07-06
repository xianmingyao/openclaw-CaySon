# -*- coding: utf-8 -*-
"""枚举所有窗口"""
from pywinauto import Desktop

print("=== 枚举所有窗口 (UIA backend) ===")
desktop = Desktop(backend="uia")
for w in desktop.windows():
    try:
        title = w.window_text()
        if title:
            rect = w.rectangle()
            print(f"'{title}' -> {rect.width()}x{rect.height()}")
    except:
        pass

print("\n=== 使用 win32gui 枚举 ===")
import win32gui
import win32process

def callback(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title and len(title) > 2:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                results.append((hwnd, pid, title, rect))
            except:
                pass

results = []
win32gui.EnumWindows(callback, results)

for hwnd, pid, title, rect in sorted(results, key=lambda x: x[1]):
    if any(kw in title.lower() for kw in ['chrome', 'muying', 'internal', 'jd', 'jingmai', '京麦']):
        print(f"[{pid}] hwnd={hwnd}: '{title}'")
