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

def click(x, y, delay=0.3):
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

# 材质选择框 (1920x1032的907,786 -> 2560x1392的1209,1059)
material_x, material_y = 1209, 1059
print(f"Material dropdown: ({material_x}, {material_y})")

# 塑料选项 (1920x1032的907,818 -> 2560x1392的1209,1102)
plastic_x, plastic_y = 1209, 1102
print(f"Plastic option: ({plastic_x}, {plastic_y})")

print("\nStep 1: Click material dropdown")
click(material_x, material_y, 2)
save_screenshot('m1')

print("Step 2: Click plastic")
click(plastic_x, plastic_y, 1)
save_screenshot('m2')

time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\m_final.png')

print("\nDone!")
