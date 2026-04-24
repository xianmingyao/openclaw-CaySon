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
    time.sleep(0.3)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

# 尝试多个可能的位置关闭弹窗
test_positions = [
    (1275, 325),  # 密集区域中心
    (1300, 350),  # 偏右
    (1250, 350),  # 偏左
    (1280, 300),  # 偏上
]

for i, pos in enumerate(test_positions):
    print(f"\nTrying position {i+1}: {pos}")
    click(pos[0], pos[1], 1)
    save_screenshot(f'popup_x_try{i+1}')

time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\popup_close_result.png')

print("\nDone!")
