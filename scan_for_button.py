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
    
    # The 新建 button is at the top-left of the sidebar
    # Based on the screenshot, the sidebar is on the left side
    # The button should be around x=60-100, y=160-200 from window top-left
    
    # Let's scan a grid of positions
    print("\nScanning for 新建 button...")
    
    # Try a range of positions
    for y in range(150, 220, 10):
        for x in range(40, 140, 20):
            abs_x = left + x
            abs_y = top + y
            print(f"Trying ({abs_x}, {abs_y})...", end=" ")
            
            dc.move_mouse(abs_x, abs_y, duration=0.1)
            time.sleep(0.1)
            
            # Check pixel color at this position
            color = dc.get_pixel_color(abs_x, abs_y)
            
            # Check if it's blue-ish (the button is blue)
            r, g, b = color
            if b > 150 and r < 100 and g < 180:
                print(f"BLUE! RGB({r},{g},{b}) - clicking!")
                dc.click(abs_x, abs_y)
                time.sleep(1)
                dc.screenshot(filename="found_button.png")
                print("  Screenshot saved")
                break
            else:
                print(f"RGB({r},{g},{b})")
        
        # Check if we found it
        try:
            from PIL import Image
            img = Image.open("found_button.png")
            print("  Found button, breaking")
            break
        except:
            pass
else:
    print("No Chrome window found!")
