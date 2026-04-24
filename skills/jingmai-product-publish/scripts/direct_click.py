# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

# 使用大窗口 (18289096)
hwnd = 18289096

rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

# 实际坐标 (从截图分析得出)
cat_x, cat_y = 1354, 234
next_x, next_y = 1275, 1301

print(f"Category: ({cat_x}, {cat_y})")
print(f"Next button: ({next_x}, {next_y})")

# 激活窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# Step 1: 点击第三列"金属加工配件"
print(f"\nStep 1: Click category at ({cat_x}, {cat_y})...")
win32api.SetCursorPos((cat_x, cat_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\s1.png')

# Step 2: 点击"下一步"按钮
print(f"Step 2: Click next at ({next_x}, {next_y})...")
win32api.SetCursorPos((next_x, next_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(3)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\s2.png')
print("\nDone! Check s1.png and s2.png")
