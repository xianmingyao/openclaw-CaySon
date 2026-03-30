import sys
import os

# Add the skill directory to the path
skill_dir = r"E:\workspace\skills\desktop-control-1-0-0"
sys.path.insert(0, skill_dir)

from __init__ import DesktopController
import time

dc = DesktopController(failsafe=True)

# First, activate the Chrome window
print("Activating Chrome window...")
windows = dc.get_all_windows()
for w in windows:
    if "Chrome" in w or "有道云笔记" in w:
        print(f"Found window: {w}")

# Activate Chrome
dc.activate_window("Chrome")
time.sleep(1)

# Get screen size
width, height = dc.get_screen_size()
print(f"Screen size: {width}x{height}")

# Get current mouse position
pos = dc.get_mouse_position()
print(f"Current mouse position: {pos}")

# Take a screenshot to see the current state
dc.screenshot(filename="desktop_control_1.png")
print("Screenshot saved: desktop_control_1.png")

# Try clicking on the 新建 button at different positions
print("Trying to click 新建 button...")

# The button is at the top left of the sidebar
# Try multiple positions
positions = [
    (75, 185),
    (70, 180),
    (80, 190),
    (65, 175),
]

for x, y in positions:
    print(f"Trying position ({x}, {y})...")
    dc.move_mouse(x, y, duration=0.3)
    time.sleep(0.3)
    dc.click()
    time.sleep(1)
    dc.screenshot(filename=f"desktop_control_{x}_{y}.png")
    print(f"  Clicked and screenshot saved")

# Check current position
pos = dc.get_mouse_position()
print(f"Final mouse position: {pos}")
