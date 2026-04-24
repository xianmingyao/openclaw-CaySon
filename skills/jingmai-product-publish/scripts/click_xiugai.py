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

# 识别坐标 (497, 134)
# 真实坐标 = (994, 233)
xiugai_btn = (994, 233)

print(f"\n识别坐标: (497, 134)")
print(f"真实坐标: {xiugai_btn}")
print(f"\nClicking '修改' at {xiugai_btn}")
click(xiugai_btn[0], xiugai_btn[1], 3)
save_screenshot('click_xiugai')

time.sleep(2)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\after_xiugai.png')

print("\nDone!")
