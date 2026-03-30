import sys
import time
sys.path.insert(0, r"E:\workspace\skills\desktop-control-1-0-0")
from __init__ import DesktopController
import win32gui
import win32con

dc = DesktopController(failsafe=True)

# Get Chrome window info
def get_window_rect(title_substring):
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_substring in title and "Chrome" in title:
                rect = win32gui.GetWindowRect(hwnd)
                windows.append((title, rect))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

# Find the Youdao Chrome window
print("Finding Chrome windows...")
chrome_windows = get_window_rect("有道云笔记")
if not chrome_windows:
    chrome_windows = get_window_rect("Chrome")

for title, rect in chrome_windows:
    left, top, right, bottom = rect
    print(f"Window: {title}")
    print(f"  Position: left={left}, top={top}")
    print(f"  Size: width={right-left}, height={bottom-top}")
    
    # Activate the window
    hwnd = win32gui.FindWindow(None, title)
    if hwnd:
        win32gui.SetForegroundWindow(hwnd)
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.5)

# Take a screenshot to see the current state
dc.screenshot(filename="window_pos_1.png")
print("\nScreenshot saved")

# Now try to click on the 新建 button
# Based on the previous screenshot, the 新建 button is in the sidebar at the top
# The sidebar starts at approximately x=0-300 from the left edge of the browser window
# And y=150-200 from the top of the browser window

# If the browser window is at (left, top), we need to add these offsets
if chrome_windows:
    _, rect = chrome_windows[0]
    left, top, right, bottom = rect
    print(f"\nBrowser window offset: ({left}, {top})")
    
    # Try clicking at the approximate position of 新建 button
    # Based on the screenshot analysis, the button is around (60-80, 170-190) from the browser window's top-left
    click_x = left + 75
    click_y = top + 185
    print(f"Clicking at screen position: ({click_x}, {click_y})")
    
    dc.move_mouse(click_x, click_y, duration=0.5)
    time.sleep(0.5)
    dc.click()
    print("Clicked!")
    
    time.sleep(1)
    dc.screenshot(filename="window_pos_2.png")
    print("Screenshot after click saved")
else:
    print("No Chrome window found!")
