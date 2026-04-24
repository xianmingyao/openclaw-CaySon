# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

# 使用正确的窗口 (529674, 300x252)
hwnd = 529674

rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")  # Expected: (1080, 648, 1380, 900)

# 窗口内容尺寸 300x252
# 截图分析用的是 1280x800
# 比例: x = 300/1280 = 0.234375, y = 252/800 = 0.315

# 归一化坐标 (1280x800 窗口中的位置)
# 下一步按钮中心: x=498, y=939
# 第三列中心: x=530, y=232

# 转换到实际窗口坐标
scale_x = 300.0 / 1280.0
scale_y = 252.0 / 800.0

next_x_norm = 498
next_y_norm = 939
cat_x_norm = 530
cat_y_norm = 232

next_x = int(next_x_norm * scale_x)
next_y = int(next_y_norm * scale_y)
cat_x = int(cat_x_norm * scale_x)
cat_y = int(cat_y_norm * scale_y)

# 加上窗口偏移 (1080, 648)
offset_x = 1080
offset_y = 648

next_screen_x = offset_x + next_x
next_screen_y = offset_y + next_y
cat_screen_x = offset_x + cat_x
cat_screen_y = offset_y + cat_y

print(f"Next button: ({next_x_norm},{next_y_norm}) -> screen ({next_screen_x},{next_screen_y})")
print(f"Category: ({cat_x_norm},{cat_y_norm}) -> screen ({cat_screen_x},{cat_screen_y})")

# 激活窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 截图当前状态
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\current_state.png')
print(f"Screenshot: {rect}")

# 点击第三列
print(f"\nStep 1: Click category at ({cat_screen_x}, {cat_screen_y})...")
win32api.SetCursorPos((cat_screen_x, cat_screen_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

# 点击下一步
print(f"Step 2: Click next at ({next_screen_x}, {next_screen_y})...")
win32api.SetCursorPos((next_screen_x, next_screen_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(3)

# 最终截图
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\after_action.png')
print("Done!")
