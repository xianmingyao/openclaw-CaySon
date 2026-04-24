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

# 尝试多个位置关闭"参数"弹窗
positions = [
    (1486, 516),  # 之前分析的位置
    (1500, 500),  # 稍微调整
    (1520, 520),  # 偏右
    (1470, 530),  # 偏左
    (1450, 550),  # 偏下
    (1550, 550),  # 右下
]

for i, pos in enumerate(positions):
    print(f"\nTrying position {i+1}: {pos}")
    click(pos[0], pos[1], 1)
    save_screenshot(f'try_param_{i+1}')
    
    # 检查是否关闭
    time.sleep(0.5)
    img = ImageGrab.grab(bbox=rect)
    img_array = np.array(img)
    
    # 检查是否还有"参数"文字（简单判断）
    # 如果弹窗关闭了，屏幕中央不应该有大面积白色区域

time.sleep(1)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\param_close_results.png')

print("\nDone!")
