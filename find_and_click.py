import sys
import time
sys.path.insert(0, r"E:\workspace\skills\desktop-control-1-0-0")
from __init__ import DesktopController
import win32gui
import win32con
from PIL import Image
import numpy as np

dc = DesktopController(failsafe=True)

# Get Chrome window info
def get_window_rect(title_substring):
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
chrome_windows = get_window_rect("有道云笔记")
if not chrome_windows:
    chrome_windows = get_window_rect("Chrome")

if chrome_windows:
    title, rect, hwnd = chrome_windows[0]
    left, top, right, bottom = rect
    print(f"Window: {title}")
    print(f"  Position: left={left}, top={top}")
    print(f"  Size: width={right-left}, height={bottom-top}")
    
    # Activate the window
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.5)
    
    # Take a screenshot of just the browser window
    region = (left, top, right-left, bottom-top)
    dc.screenshot(region=region, filename="browser_region.png")
    print("Browser region screenshot saved")
    
    # Load and analyze the image
    img = Image.open("browser_region.png")
    pixels = np.array(img)
    
    print(f"Image shape: {pixels.shape}")
    
    # Scan the top-left area for blue pixels
    # Youdao's blue button is typically RGB(0, 122, 255) which is BGR(255, 122, 0)
    sidebar = pixels[0:300, 0:300]
    
    # Look for blue-ish pixels (R low, G mid, B high)
    # In RGB format from PIL: (R, G, B)
    blue_mask = (sidebar[:,:,0] < 100) & (sidebar[:,:,1] < 180) & (sidebar[:,:,2] > 200)
    
    # Find rows and cols with blue pixels
    rows, cols = np.where(blue_mask)
    
    if len(rows) > 0:
        print(f"Found {len(rows)} blue pixels in sidebar")
        
        # Group into regions
        min_y, max_y = rows.min(), rows.max()
        min_x, max_x = cols.min(), cols.max()
        print(f"Blue region bounding box: x={min_x}-{max_x}, y={min_y}-{max_y}")
        
        # Try clicking around the center of the blue region
        center_x = left + (min_x + max_x) // 2
        center_y = top + (min_y + max_y) // 2
        print(f"Trying to click at absolute position: ({center_x}, {center_y})")
        
        dc.move_mouse(center_x, center_y, duration=0.3)
        time.sleep(0.3)
        dc.click()
        print("Clicked!")
        time.sleep(2)
        dc.screenshot(filename="after_blue_click.png")
    else:
        print("No blue pixels found in sidebar")
        
        # Try scanning for any colored pixels that might be the button
        # Look for non-white, non-gray pixels
        gray_mask = (np.abs(sidebar[:,:,0].astype(int) - sidebar[:,:,1].astype(int)) < 30) & \
                    (np.abs(sidebar[:,:,1].astype(int) - sidebar[:,:,2].astype(int)) < 30)
        colored_mask = ~gray_mask & (sidebar[:,:,0] > 50) | (sidebar[:,:,1] > 50) | (sidebar[:,:,2] > 50)
        
        rows, cols = np.where(colored_mask)
        if len(rows) > 0:
            print(f"Found {len(rows)} colored pixels in sidebar")
            
            # Group into clusters
            from collections import defaultdict
            clusters = defaultdict(list)
            for r, c in zip(rows, cols):
                # Group by approximate y position (in chunks of 20 pixels)
                cluster_y = (r // 20) * 20
                clusters[cluster_y].append((r, c))
            
            # Find the cluster with most pixels (likely the button area)
            largest_cluster = max(clusters.keys(), key=lambda k: len(clusters[k]))
            cluster_rows, cluster_cols = zip(*clusters[largest_cluster])
            
            center_x = left + (min(cluster_cols) + max(cluster_cols)) // 2
            center_y = top + (min(cluster_rows) + max(cluster_rows)) // 2
            print(f"Colored region center: ({center_x}, {center_y})")
            
            dc.move_mouse(center_x, center_y, duration=0.3)
            time.sleep(0.3)
            dc.click()
            print("Clicked!")
            time.sleep(2)
            dc.screenshot(filename="after_colored_click.png")
else:
    print("No Chrome window found!")
