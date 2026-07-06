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

# 截图函数
def save_screenshot(name):
    img = ImageGrab.grab(bbox=rect)
    path = rf'E:\workspace\skills\jingmai-product-publish\logs\{name}.png'
    img.save(path)
    print(f"Saved: {path}")
    return path

# 点击函数
def click(x, y, delay=0.3):
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

# 坐标转换 (归一化0-1000 -> 实际2560x1392)
def to_actual(norm_x, norm_y):
    return (int(norm_x * 2560 / 1000), int(norm_y * 1392 / 1000))

# 元素坐标
coords = {
    '防护等级': to_actual(318, 755),   # [755, 318]
    '材质': to_actual(470, 755),      # [755, 470]
    '商品图片': to_actual(275, 115),   # [115, 275]
    '商品描述': to_actual(312, 115),  # [115, 312]
    '发布按钮': to_actual(475, 973),   # [973, 475]
}

print("\n元素坐标:")
for k, v in coords.items():
    print(f"  {k}: {v}")

# Step 1: 点击"防护等级"选择框
print("\n" + "="*50)
print("Step 1: 点击'防护等级'选择框")
print("="*50)
click(coords['防护等级'][0], coords['防护等级'][1], 1.5)
save_screenshot('attr_protection')

# 截图看选项
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\protection_options.png')
print("查看防护等级选项...")

print("\n请查看截图，选择合适的防护等级选项")
print("选择完成后告诉我继续...")
