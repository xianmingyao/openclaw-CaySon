import sys
import time
import pyperclip
sys.path.insert(0, r"E:\workspace\skills\desktop-control-1-0-0")
from __init__ import DesktopController
import win32gui
import win32con

dc = DesktopController(failsafe=True)

def get_window_info(title_substring):
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_substring in title and "Chrome" in title:
                rect = win32gui.GetWindowRect(hwnd)
                windows.append((title, rect, hwnd))
        return True
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

print("Finding Chrome windows...")
chrome_windows = get_window_info("有道云笔记")
if not chrome_windows:
    chrome_windows = get_window_info("Chrome")

if chrome_windows:
    title, rect, hwnd = chrome_windows[0]
    left, top, right, bottom = rect
    
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.5)
    
    # Click on the title field to rename
    title_x = left + 600
    title_y = top + 150
    print(f"Clicking title at ({title_x}, {title_y})...")
    dc.click(title_x, title_y)
    time.sleep(0.5)
    
    # Select all and type new name
    dc.hotkey("ctrl", "a")
    time.sleep(0.3)
    dc.type_text("skill-vetter 使用指南", interval=0.05)
    time.sleep(0.5)
    
    # Press Enter to confirm
    dc.press("enter")
    time.sleep(1)
    
    dc.screenshot(filename="renamed_note.png")
    print("Done!")
else:
    print("No Chrome window found!")
