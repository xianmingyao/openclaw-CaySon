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

# 方法1: 按ESC关闭弹窗
print("\nStep 1: Press ESC to close popup")
win32api.keybd_event(0x1B, 0, 0, 0)  # ESC
win32api.keybd_event(0x1B, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(1)
save_screenshot('after_esc')

# 方法2: 直接点击修改按钮 (归一化168,388 -> 实际430,540)
modify_x, modify_y = 430, 540
print(f"\nStep 2: Click '修改' at ({modify_x}, {modify_y})")
click(modify_x, modify_y, 2)
save_screenshot('modify_click')

time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\final_check.png')

print("\nDone!")
