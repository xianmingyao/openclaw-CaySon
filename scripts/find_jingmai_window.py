# -*- coding: utf-8 -*-
import win32gui
import win32process

def callback(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                results.append((hwnd, pid, title))
            except:
                pass

results = []
win32gui.EnumWindows(callback, results)

print("=== Chrome/京东相关窗口 ===")
for hwnd, pid, title in sorted(results, key=lambda x: x[1]):
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['jd', 'jingmai', 'muyi', 'internal', 'chrome', '京麦']):
        rect = win32gui.GetWindowRect(hwnd)
        print(f'hwnd={hwnd}, pid={pid}')
        print(f'  title="{title}"')
        print(f'  rect={rect}')
        print()
