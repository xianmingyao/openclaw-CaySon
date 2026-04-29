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

# IP23在防护等级下拉框中的位置
# 下拉框展开后，IP23应该在列表中
# 根据截图分析，IP23选项位置大约在 y=xxx
# 让我先计算大概位置

# 防护等级下拉框展开后，选项列表大约在 (814, 800) 到 (1000, 1100) 范围
# IP23应该是列表中的某个选项

# 先尝试直接点击IP23的大概位置
# 假设列表中心在 y=900-1050 之间

print("\nStep 1: 选择 IP23")
# IP23在列表中的位置估算 - 需要根据实际情况调整
# 先点击下拉框展开区域下方的IP23选项位置
ip23_x, ip23_y = 814, 950  # 估算位置

print(f"Clicking IP23 at ({ip23_x}, {ip23_y})")
click(ip23_x, ip23_y, 0.5)
save_screenshot('select_ip23')

# 等待看是否选中
time.sleep(1)

# 如果没选中，尝试其他位置
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\check_ip23.png')

print("\n请查看截图，确认IP23是否被选中")
print("如果没选中，请告诉我IP23在截图中的实际位置，我来重新点击")
