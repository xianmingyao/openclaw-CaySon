# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

hwnd = 18289096

rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

# "下一步"按钮坐标
next_x, next_y = 1275, 1306

print(f"Clicking '下一步' at ({next_x}, {next_y})")

# 激活窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 点击
win32api.SetCursorPos((next_x, next_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

print("Clicked! Waiting for page to load...")
time.sleep(3)

# 截图
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\product_info_page.png')
print("Saved: product_info_page.png")
