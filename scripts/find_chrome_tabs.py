# -*- coding: utf-8 -*-
"""查找Chrome中的京麦商家中心标签页"""
import win32gui
import win32process

chrome_pids = {29396}  # Chrome进程PID

def callback(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid in chrome_pids:
                    rect = win32gui.GetWindowRect(hwnd)
                    results.append((hwnd, pid, title, rect))
            except:
                pass

results = []
win32gui.EnumWindows(callback, results)

print("=== Chrome 窗口 (PID 29396) ===")
for hwnd, pid, title, rect in sorted(results, key=lambda x: x[0]):
    print(f"hwnd={hwnd}: '{title}'")
    print(f"  rect={rect}")
    print()
