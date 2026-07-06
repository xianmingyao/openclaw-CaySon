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

# 材质选择框坐标 (归一化473,757 -> 实际1211,1053)
material_x, material_y = 1211, 1053

print(f"\nStep 1: Click Material dropdown at ({material_x}, {material_y})")
click(material_x, material_y, 1.5)
save_screenshot('material_click1')

# 塑料选项 (归一化473,779 -> 实际1211,1084)
plastic_x, plastic_y = 1211, 1084

print(f"\nStep 2: Click '塑料' at ({plastic_x}, {plastic_y})")
click(plastic_x, plastic_y, 1)
save_screenshot('plastic_click2')

print("\nDone!")
