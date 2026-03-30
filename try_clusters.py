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
    
    # Take a full screenshot
    region = (left, top, width, height)
    dc.screenshot(region=region, filename="browser_full.png")
    
    # Load and analyze
    img = Image.open("browser_full.png")
    pixels = np.array(img)
    
    # Find blue pixels
    r_channel = pixels[:,:,0].astype(int)
    g_channel = pixels[:,:,1].astype(int)
    b_channel = pixels[:,:,2].astype(int)
    
    blue_mask = (b_channel > 150) & (r_channel < 100) & (g_channel < 200)
    rows, cols = np.where(blue_mask)
    
    print(f"Found {len(rows)} blue pixels")
    
    # Group into clusters
    from collections import defaultdict
    clusters = defaultdict(list)
    for r, c in zip(rows, cols):
        cluster_y = (r // 20) * 20
        clusters[cluster_y].append((r, c))
    
    # Sort by size
    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
    
    print("\nTop clusters by size:")
    for cluster_y, points in sorted_clusters[:5]:
        min_r = min(r for r, c in points)
        max_r = max(r for r, c in points)
        min_c = min(c for r, c in points)
        max_c = max(c for r, c in points)
        print(f"  y={cluster_y}: {len(points)} pixels, box: ({min_c},{min_r})-({max_c},{max_r})")
    
    # Try the 3rd largest cluster (likely the sidebar header)
    # Skip the first two which are browser UI
    for cluster_y, points in sorted_clusters[2:7]:
        min_r = min(r for r, c in points)
        max_r = max(r for r, c in points)
        min_c = min(c for r, c in points)
        max_c = max(c for r, c in points)
        
        # Center of the cluster
        center_x = left + (min_c + max_c) // 2
        center_y = top + (min_r + max_r) // 2
        
        print(f"\nTrying cluster at ({center_x}, {center_y})...")
        dc.move_mouse(center_x, center_y, duration=0.3)
        time.sleep(0.3)
        dc.click()
        print("Clicked!")
        time.sleep(2)
        
        dc.screenshot(filename=f"click_cluster.png")
        
        # Check for menu
        dc.screenshot(region=region, filename="check.png")
        img1 = np.array(Image.open("browser_full.png"))
        img2 = np.array(Image.open("check.png"))
        diff = np.abs(img1.astype(float) - img2.astype(float)).sum()
        print(f"  Difference: {diff}")
        
        if diff > 5000000:
            print("  Menu appeared!")
            break
else:
    print("No Chrome window found!")
