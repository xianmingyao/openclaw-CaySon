# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32ui
from PIL import Image
import sys

# Find ALL windows with jd_ prefix
result = []
def enum_cb(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title and 'jd_' in title.lower():
            rect = win32gui.GetWindowRect(hwnd)
            results.append((hwnd, title, rect))
win32gui.EnumWindows(enum_cb, result)

print(f"Found {len(result)} windows with 'jd_' in title:")
for hwnd, title, rect in result:
    left, top, right, bottom = rect
    print(f"  HWND={hwnd}, Title='{title}', Rect=({left},{top},{right},{bottom}), Size={right-left}x{bottom-top}")
