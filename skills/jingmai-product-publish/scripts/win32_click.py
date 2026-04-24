# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time
import ctypes

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

# 方法1: 直接发送WM_COMMAND消息
print("\nMethod 1: Sending WM_LBUTTONDOWN/UP messages")

# 先移动鼠标
win32api.SetCursorPos((1872, 144))
time.sleep(0.3)

# 发送鼠标按下和抬起消息
win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, win32api.MAKELONG(1872, 144))
time.sleep(0.1)
win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(1872, 144))
time.sleep(2)
save_screenshot('sendmessage_click')

# 方法2: 用PostMessage
print("\nMethod 2: Using PostMessage")
win32api.SetCursorPos((1872, 144))
time.sleep(0.3)
win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 1, win32api.MAKELONG(1872, 144))
time.sleep(0.1)
win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(1872, 144))
time.sleep(2)
save_screenshot('postmessage_click')

# 方法3: 直接用mouse_event
print("\nMethod 3: Using mouse_event directly")
win32api.SetCursorPos((1872, 144))
time.sleep(0.5)
win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE, 0, 0, 0, 0)
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.15)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)
save_screenshot('mouseevent_click')

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\all_methods_result.png')

print("\nDone!")
