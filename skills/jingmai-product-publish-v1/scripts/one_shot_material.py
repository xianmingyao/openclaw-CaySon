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

def click(x, y, delay=0.2):
    win32api.SetCursorPos((x, y))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

# 先展开材质下拉框
material_x, material_y = 1208, 1055
print(f"Step 1: Expand material dropdown at ({material_x}, {material_y})")
click(material_x, material_y, 2)
save_screenshot('step1_expand')

# 截图看展开后的位置
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\step1_state.png')

# 塑料在列表底部，从之前分析大约是 y=997
plastic_x, plastic_y = 1214, 997
print(f"Step 2: Select '塑料' at ({plastic_x}, {plastic_y})")
click(plastic_x, plastic_y, 1)
save_screenshot('step2_plastic')

# 最终截图
time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\final_material_state.png')

print("\nDone!")
