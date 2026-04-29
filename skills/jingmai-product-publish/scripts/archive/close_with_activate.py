# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

hwnd = 18289096
rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

# 确保窗口在最前面
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 最大化窗口（如果可以）
# win32gui.ShowWindow(hwnd, 3)  # SW_MAXIMIZE

def save_screenshot(name):
    img = ImageGrab.grab(bbox=rect)
    path = rf'E:\workspace\skills\jingmai-product-publish\logs\{name}.png'
    img.save(path)
    print(f"Saved: {path}")

def click(x, y, delay=0.5):
    win32api.SetCursorPos((x, y))
    time.sleep(0.5)  # 增加等待时间
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

# X按钮坐标 - 宁兄亲自指导
x_btn = (973, 134)

print(f"\nStep 1: Click X at {x_btn}")
click(x_btn[0], x_btn[1], 3)
save_screenshot('x_clicked')

time.sleep(2)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\after_x_click.png')

print("\nDone!")
