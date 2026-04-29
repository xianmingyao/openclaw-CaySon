# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

hwnd = 18289096

rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

# 第四级类目"电缆接头盒"坐标
cat_x, cat_y = 1357, 231
# 下一步按钮坐标
next_x, next_y = 956, 938

print(f"Step 1: Click '电缆接头盒' at ({cat_x}, {cat_y})...")

# 激活窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 点击第四级类目
win32api.SetCursorPos((cat_x, cat_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\after_4th_select.png')

# 检查按钮状态
print(f"Step 2: Click '下一步' at ({next_x}, {next_y})...")
win32api.SetCursorPos((next_x, next_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(3)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\product_info_final.png')
print("Done!")
