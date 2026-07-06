import win32gui
import win32con
import win32ui
from PIL import Image
import os

def find_chrome_windows():
    results = []
    def callback(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            cls = win32gui.GetClassName(hwnd)
            if 'chrome' in cls.lower() or 'widget' in cls.lower() or '京麦' in title:
                rect = win32gui.GetWindowRect(hwnd)
                if rect[2] - rect[0] > 100 and rect[3] - rect[1] > 100:
                    results.append({
                        'hwnd': hwnd,
                        'title': title[:80],
                        'class': cls,
                        'rect': rect
                    })
    win32gui.EnumWindows(callback, None)
    return results

windows = find_chrome_windows()
for w in windows:
    print(f"hwnd={w['hwnd']}, title='{w['title']}', class='{w['class']}', rect={w['rect']}")
