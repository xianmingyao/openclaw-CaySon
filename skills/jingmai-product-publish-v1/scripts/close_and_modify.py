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

# X关闭按钮坐标 (归一化137,974 -> 实际351,1356)
close_x, close_y = 351, 1356

# 修改按钮坐标 (归一化168,387 -> 实际430,539)
modify_x, modify_y = 430, 539

print(f"\nStep 1: Click X to close popup at ({close_x}, {close_y})")
click(close_x, close_y, 1)
save_screenshot('step1_close')

time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\step1_state.png')

print(f"\nStep 2: Click '修改' at ({modify_x}, {modify_y})")
click(modify_x, modify_y, 2)
save_screenshot('step2_modify')

time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\step2_state.png')

print("\nDone!")
