# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

hwnd = 18289096

rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

# 正确坐标（归一化1000转实际2560x1392）
# 第三级"电气辅材": (568, 233) -> (1454, 324)
third_x = int(568 * 2560 / 1000)
third_y = int(233 * 1392 / 1000)

# 第四级"电缆接头盒": (713, 233) -> (1825, 324)
fourth_x = int(713 * 2560 / 1000)
fourth_y = int(233 * 1392 / 1000)

# 下一步按钮: (499, 939) -> (1277, 1307)
next_x = int(499 * 2560 / 1000)
next_y = int(939 * 1392 / 1000)

print(f"Third level: ({third_x}, {third_y})")
print(f"Fourth level: ({fourth_x}, {fourth_y})")
print(f"Next button: ({next_x}, {next_y})")

# 激活窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# Step 1: 悬停在第三级"电气辅材"上，展开第四级
print(f"\nStep 1: Hover on '电气辅材' at ({third_x}, {third_y})...")
win32api.SetCursorPos((third_x, third_y))
time.sleep(1)

# 截图检查
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\step1.png')

# Step 2: 点击第四级"电缆接头盒"
print(f"Step 2: Click '电缆接头盒' at ({fourth_x}, {fourth_y})...")
win32api.SetCursorPos((fourth_x, fourth_y))
time.sleep(0.3)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\step2.png')

# Step 3: 点击"下一步"按钮
print(f"Step 3: Click '下一步' at ({next_x}, {next_y})...")
win32api.SetCursorPos((next_x, next_y))
time.sleep(0.3)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(3)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\step3.png')
print("\nDone!")
