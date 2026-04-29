# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

hwnd = 18289096
rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

def save_screenshot(name):
    img = ImageGrab.grab(bbox=rect)
    path = rf'E:\workspace\skills\jingmai-product-publish\logs\{name}.png'
    img.save(path)
    print(f"Saved: {path}")

def click(x, y, delay=0.3):
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

def esc():
    win32api.keybd_event(0x1B, 0, 0, 0)  # ESC down
    win32api.keybd_event(0x1B, 0, win32con.KEYEVENTF_KEYUP, 0)  # ESC up
    time.sleep(0.3)

# 方法1: 按ESC多次
print("\nMethod 1: Press ESC multiple times")
for i in range(5):
    esc()
    print(f"  ESC {i+1}")
save_screenshot('esc_try')

time.sleep(1)

# 方法2: 点击弹窗外部区域（黑暗遮罩）关闭
print("\nMethod 2: Click outside popup (dark overlay)")
# 点击左上角黑暗区域
click(100, 100, 0.5)
save_screenshot('click_outside')

time.sleep(1)

# 方法3: 点击X按钮（再次尝试，可能位置有偏差）
print("\nMethod 3: Click X button precisely")
# X按钮可能在 (1870, 148) 稍微偏下的位置
for offset in [(0, 0), (10, 10), (-10, -10), (0, 20), (10, 0)]:
    x = 1870 + offset[0]
    y = 148 + offset[1]
    print(f"  Trying ({x}, {y})")
    click(x, y, 0.5)
    save_screenshot(f'x_offset_{offset}')

time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\multi_close_result.png')

print("\nDone!")
