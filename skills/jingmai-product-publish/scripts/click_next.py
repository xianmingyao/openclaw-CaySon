"""
Jingmai Product Publish - Click Next Button Test
"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish\scripts')

from jingmai_logger import init_logger
from jingmai_locator import JingmaiLocator
from jingmai_monitor import JingmaiMonitor
import time

log = init_logger("click_next")
locator = JingmaiLocator(log)
monitor = JingmaiMonitor(locator, log)

log.header("Click Next Button Test")

# 1. Find window
log.step("[1/4] Finding Jingmai window...")
window = locator.find_window()
if not window:
    log.error("Window not found")
    sys.exit(1)
log.ok(f"Window found: {window.title}")
log.info(f"Window rect: {window.rect}")

# 2. Activate window
log.step("[2/4] Activating window...")
locator.activate_window()
time.sleep(0.5)

# Get updated window rect
if locator.window_rect:
    log.info(f"Window position after activate: {locator.window_rect}")

# 3. Screenshot before click
log.step("[3/4] Screenshot before click...")
screenshot_before = monitor.take_screenshot("before_click")
log.info(f"Before: {screenshot_before}")

# Next button coordinates (from image analysis)
# Screen coordinates need to be calculated based on window position
# The screenshot showed button at window-relative position around x=498, y=939

# First get current window position
if locator.window_rect:
    left, top, right, bottom = locator.window_rect
    log.info(f"Window offset: left={left}, top={top}")
    
    # Button center (from screenshot analysis): window coords ~498, 939
    # Convert to screen coords
    screen_x = left + 498
    screen_y = top + 939
    
    log.info(f"Screen click position: ({screen_x}, {screen_y})")
    
    # Execute click
    log.step("[4/4] Clicking Next button...")
    import win32api
    import win32con
    win32api.SetCursorPos((screen_x, screen_y))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    log.ok("Click executed")
else:
    log.error("Window rect not available")

# Wait and screenshot after
time.sleep(2)
log.info("Taking after-click screenshot...")
screenshot_after = monitor.take_screenshot("after_click")
log.info(f"After: {screenshot_after}")

log.info("")
log.info("=" * 50)
log.info("Please check screenshots for results")
log.info("=" * 50)
