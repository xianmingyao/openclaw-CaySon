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

def click(x, y, delay=0.5):
    win32api.SetCursorPos((x, y))
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

# X关闭按钮 (AI识别结果)
x_btn = (1870, 148)

print(f"\nClicking X close button at {x_btn}")
click(x_btn[0], x_btn[1], 2)
save_screenshot('popup_closed')

time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\final_popup_state.png')

print("\nDone!")
