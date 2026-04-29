# -*- coding: utf-8 -*-
"""测试jingmai_locator的窗口匹配"""
import win32gui
import win32process

WINDOW_TITLES = [
    'muyixing',
    'Internal-Platform-Frontend',
    '京麦',
    '京东商家',
]

def callback(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                for keyword in WINDOW_TITLES:
                    if keyword.lower() in title.lower():
                        rect = win32gui.GetWindowRect(hwnd)
                        results.append((hwnd, pid, title, rect))
                        break
            except:
                pass

results = []
win32gui.EnumWindows(callback, results)

print("=== jingmai_locator 匹配结果 ===")
for hwnd, pid, title, rect in results:
    print(f'hwnd={hwnd}, pid={pid}')
    print(f'  title="{title}"')
    print(f'  rect={rect}')
    print()

if not results:
    print("❌ 没有找到任何京麦相关窗口!")
