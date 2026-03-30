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
    
    # Take a full screenshot of the browser window
    region = (left, top, width, height)
    dc.screenshot(region=region, filename="full_browser.png")
    print("Full browser screenshot saved")
    
    # Load and analyze the image
    img = Image.open("full_browser.png")
    pixels = np.array(img)
    h, w = pixels.shape[:2]
    print(f"Image size: {w}x{h}")
    
    # Scan for blue pixels in the entire image
    # Youdao's blue is typically RGB(0, 122, 255) or similar
    r_channel = pixels[:,:,0].astype(int)
    g_channel = pixels[:,:,1].astype(int)
    b_channel = pixels[:,:,2].astype(int)
    
    # Find pixels that are blue-ish (high blue, low red, mid green)
    blue_mask = (b_channel > 150) & (r_channel < 100) & (g_channel < 200)
    
    rows, cols = np.where(blue_mask)
    
    if len(rows) > 0:
        print(f"\nFound {len(rows)} blue pixels")
        
        # Group into clusters and find the top-most cluster (likely the button)
        from collections import defaultdict
        clusters = defaultdict(list)
        for r, c in zip(rows, cols):
            cluster_y = (r // 30) * 30  # Group by 30-pixel rows
            clusters[cluster_y].append((r, c))
        
        # Sort clusters by y position (top-most first)
        sorted_clusters = sorted(clusters.items(), key=lambda x: x[0])
        
        print("\nTop blue clusters:")
        for cluster_y, points in sorted_clusters[:10]:
            min_r = min(r for r, c in points)
            max_r = max(r for r, c in points)
            min_c = min(c for r, c in points)
            max_c = max(c for r, c in points)
            print(f"  y={cluster_y}: {len(points)} pixels, bounding box: ({min_c},{min_r})-({max_c},{max_r})")
        
        # Click on the top-most significant blue cluster
        for cluster_y, points in sorted_clusters:
            if len(points) > 50:  # Only significant clusters
                min_r = min(r for r, c in points)
                max_r = max(r for r, c in points)
                min_c = min(c for r, c in points)
                max_c = max(c for r, c in points)
                
                # Click at the center of the cluster
                click_x = left + (min_c + max_c) // 2
                click_y = top + (min_r + max_r) // 2
                
                print(f"\nClicking on blue cluster at ({click_x}, {click_y})...")
                dc.move_mouse(click_x, click_y, duration=0.3)
                time.sleep(0.3)
                dc.click()
                print("Clicked!")
                
                time.sleep(2)
                dc.screenshot(filename="after_cluster_click.png")
                
                # Check if a menu appeared
                dc.screenshot(region=region, filename="check_menu.png")
                
                # Compare the two screenshots
                img_before = Image.open("full_browser.png")
                img_after = Image.open("check_menu.png")
                
                diff = np.array(img_before).astype(float) - np.array(img_after).astype(float)
                diff_sum = np.abs(diff).sum()
                
                print(f"Image difference: {diff_sum}")
                
                if diff_sum > 1000000:  # Significant change
                    print("Menu appeared! Breaking.")
                    break
                else:
                    print("No significant change, trying next cluster...")
    else:
        print("No blue pixels found!")
else:
    print("No Chrome window found!")
