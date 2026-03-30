import sys
import time
sys.path.insert(0, r"E:\workspace\skills\desktop-control-1-0-0")
from __init__ import DesktopController
import win32gui
import win32con

dc = DesktopController(failsafe=True)

# Get Chrome window info
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

# Find the Youdao Chrome window
print("Finding Chrome windows...")
chrome_windows = get_window_info("有道云笔记")
if not chrome_windows:
    chrome_windows = get_window_info("Chrome")

if chrome_windows:
    title, rect, hwnd = chrome_windows[0]
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    print(f"Window: {title}")
    print(f"  Position: left={left}, top={top}")
    print(f"  Size: {width}x{height}")
    
    # Activate the window
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.5)
    
    # The note list is in the center of the window
    # Based on the layout, the note "今日学习总结 2026-03-28.md" should be around x=350, y=300
    note_x = left + 350
    note_y = top + 300
    print(f"Clicking on note at ({note_x}, {note_y})...")
    dc.click(note_x, note_y)
    time.sleep(2)
    
    dc.screenshot(filename="after_note_click.png")
    print("Screenshot saved")
    
else:
    print("No Chrome window found!")
