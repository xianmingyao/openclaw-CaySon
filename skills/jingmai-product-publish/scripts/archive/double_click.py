# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time

hwnd = 18289096

rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

# 从截图直接测量: y=232, x=515 (归一化转实际)
# 屏幕 2560x1392
x = int(515 * 2560 / 1000)  # 归一化 515 -> 实际
y = int(232 * 1392 / 1000)  # 归一化 232 -> 实际

# 或者直接从像素分析: 515/1280*2560 和 232/800*1392
x2 = int(515 * 2560 / 1280)
y2 = int(232 * 1392 / 800)

print(f"Method 1: ({x}, {y})")
print(f"Method 2: ({x2}, {y2})")

# 尝试两个位置
test_points = [(x2, y2), (1318, 323), (1354, 234)]

for i, (tx, ty) in enumerate(test_points):
    print(f"\nTest {i+1}: Clicking at ({tx}, {ty})")
    
    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    
    # 鼠标移动到目标位置
    win32api.SetCursorPos((tx, ty))
    time.sleep(0.3)
    
    # 双击
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    time.sleep(1)
    
    # 截图
    img = ImageGrab.grab(bbox=rect)
    img.save(rf'E:\workspace\skills\jingmai-product-publish\logs\test{i+1}.png')
    print(f"Saved test{i+1}.png")

print("\nDone!")
