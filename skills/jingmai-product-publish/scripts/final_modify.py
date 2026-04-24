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

# 修改按钮坐标 (归一化388,167 -> 实际993,232)
modify_x, modify_y = 993, 232

print(f"\nClick '修改' at ({modify_x}, {modify_y})")
click(modify_x, modify_y, 2)
save_screenshot('modify_final')

time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\check_modify.png')

print("\nDone!")
