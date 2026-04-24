# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

hwnd = 18289096

rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

# 第三级类目"电气辅材"位置（需要先悬停）
third_x, third_y = 850, 400  # 需要确认

# 第四级类目"电缆接头盒"坐标
fourth_x, fourth_y = 1357, 231

# 下一步按钮
next_x, next_y = 956, 938

print("Activating window...")
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 先悬停在第三级"电气辅材"上，展开第四级
print(f"Hover on third level at ({third_x}, {third_y})...")
win32api.SetCursorPos((third_x, third_y))
time.sleep(1)  # 等待四级列表展开

# 截图检查
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\hover_check.png')

# 点击第四级
print(f"Click fourth level at ({fourth_x}, {fourth_y})...")
win32api.SetCursorPos((fourth_x, fourth_y))
time.sleep(0.3)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\after_fourth.png')

# 点击下一步
print(f"Click next at ({next_x}, {next_y})...")
win32api.SetCursorPos((next_x, next_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(3)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\\final_result.png')
print("Done!")
