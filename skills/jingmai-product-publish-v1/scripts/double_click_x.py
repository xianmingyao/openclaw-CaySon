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
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.15)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

def double_click(x, y):
    click(x, y, 0.3)
    click(x, y, 0.5)

# 尝试多种点击方式
x_btn = (1872, 140)

print(f"\nMethod 1: Single click at {x_btn}")
click(x_btn[0], x_btn[1], 1)
save_screenshot('single_click')

print(f"\nMethod 2: Double click at {x_btn}")
double_click(x_btn[0], x_btn[1])
save_screenshot('double_click')

time.sleep(2)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\multi_click_result.png')

print("\nDone!")
