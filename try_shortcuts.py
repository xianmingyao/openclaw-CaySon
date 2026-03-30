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
    print(f"Window: {title}")
    print(f"  Position: left={left}, top={top}")
    
    # Activate the window
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.5)
    
    # Take screenshot before
    dc.screenshot(filename="before_ctrl_n.png")
    
    # Try Ctrl+N to create new note
    print("Pressing Ctrl+N...")
    dc.hotkey("ctrl", "n")
    print("Pressed!")
    
    time.sleep(2)
    
    # Take screenshot after
    dc.screenshot(filename="after_ctrl_n.png")
    print("Screenshot saved")
    
    # Also try F7 or other shortcuts
    print("\nTrying more shortcuts...")
    
    # Try Ctrl+Shift+N (new incognito window in Chrome, but might do something else in Youdao)
    # Try Alt+F then N (File menu)
    print("Trying Alt+F...")
    dc.press("alt")
    time.sleep(0.5)
    dc.press("f")
    time.sleep(1)
    dc.press("n")  # New Note in Youdao
    time.sleep(2)
    dc.press("escape")  # Release Alt
    dc.screenshot(filename="after_alt_f.png")
    print("Alt+F screenshot saved")
    
else:
    print("No Chrome window found!")
