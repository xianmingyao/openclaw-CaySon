# -*- coding: utf-8 -*-
"""测试窗口匹配逻辑"""
import win32gui
import win32process

JINGMAI_WINDOW_KEYWORDS = ["京麦", "muyixing", "Internal-Platform-Frontend"]

def _is_jingmai_window(title: str) -> bool:
    if not title:
        return False
    title_lower = title.lower()
    return any(kw in title_lower for kw in JINGMAI_WINDOW_KEYWORDS)

def callback(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if _is_jingmai_window(title):
                    rect = win32gui.GetWindowRect(hwnd)
                    results.append((hwnd, pid, title, rect))
            except:
                pass

results = []
win32gui.EnumWindows(callback, results)

print("=== 匹配到的京麦窗口 ===")
for hwnd, pid, title, rect in results:
    print(f'hwnd={hwnd}, pid={pid}')
    print(f'  title="{title}"')
    print(f'  rect={rect}')
    print()

if not results:
    print("❌ 没有找到任何京麦窗口!")
