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

def click(x, y, delay=0.5):
    win32api.SetCursorPos((x, y))
    time.sleep(0.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE, 0, 0, 0, 0)
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

# 尝试多个Y值
base_x = 2496
test_ys = [186, 190, 195, 200, 205]

for y in test_ys:
    print(f"\nTrying ({base_x}, {y})")
    click(base_x, y, 1)
    save_screenshot(f'try_y_{y}')

time.sleep(2)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\multi_y_result.png')

print("\nDone!")
