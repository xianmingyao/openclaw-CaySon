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

def press_key(key_code):
    win32api.keybd_event(key_code, 0, 0, 0)
    time.sleep(0.1)
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

# 方法1: ALT+F4 关闭当前窗口
print("\nMethod 1: ALT+F4")
win32api.keybd_event(0x12, 0, 0, 0)  # ALT down
win32api.keybd_event(0x73, 0, 0, 0)  # F4 down
win32api.keybd_event(0x73, 0, win32con.KEYEVENTF_KEYUP, 0)  # F4 up
win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)  # ALT up
time.sleep(1)
save_screenshot('alt_f4')

# 方法2: ESC
print("Method 2: ESC")
win32api.keybd_event(0x1B, 0, 0, 0)  # ESC down
win32api.keybd_event(0x1B, 0, win32con.KEYEVENTF_KEYUP, 0)  # ESC up
time.sleep(1)
save_screenshot('esc')

# 方法3: Ctrl+W (关闭标签页)
print("Method 3: Ctrl+W")
win32api.keybd_event(0x11, 0, 0, 0)  # CTRL down
win32api.keybd_event(0x57, 0, 0, 0)  # W down
win32api.keybd_event(0x57, 0, win32con.KEYEVENTF_KEYUP, 0)  # W up
win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # CTRL up
time.sleep(1)
save_screenshot('ctrl_w')

# 方法4: Ctrl+F4 (关闭子窗口)
print("Method 4: Ctrl+F4")
win32api.keybd_event(0x11, 0, 0, 0)  # CTRL down
win32api.keybd_event(0x73, 0, 0, 0)  # F4 down
win32api.keybd_event(0x73, 0, win32con.KEYEVENTF_KEYUP, 0)  # F4 up
win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # CTRL up
time.sleep(1)
save_screenshot('ctrl_f4')

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\keyboard_results.png')

print("\nDone! Check results.")
