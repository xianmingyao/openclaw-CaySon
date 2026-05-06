# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

hwnd = 18289096

rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

# 已知正确坐标
third_x, third_y = 1454, 324   # 第三级"电气辅材"
fourth_x, fourth_y = 1825, 324 # 第四级"电缆接头盒"
next_x, next_y = 1277, 1307    # 下一步按钮

win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# Step 1: 点击第三级"电气辅材"展开第四级
print(f"Step 1: Click '电气辅材' at ({third_x}, {third_y})...")
win32api.SetCursorPos((third_x, third_y))
time.sleep(0.3)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(1.5)

# Step 2: 点击第四级"电缆接头盒"
print(f"Step 2: Click '电缆接头盒' at ({fourth_x}, {fourth_y})...")
win32api.SetCursorPos((fourth_x, fourth_y))
time.sleep(0.3)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\after_4th.png')

# Step 3: 点击"下一步"
print(f"Step 3: Click '下一步' at ({next_x}, {next_y})...")
win32api.SetCursorPos((next_x, next_y))
time.sleep(0.3)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(3)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\product_page.png')
print("Done!")
