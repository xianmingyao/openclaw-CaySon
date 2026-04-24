"""
京麦截图 - 使用PIL.ImageGrab
"""
import win32gui
from PIL import ImageGrab
import sys

hwnd = 18289096  # 京麦窗口句柄

# 获取窗口信息
rect = win32gui.GetWindowRect(hwnd)
left, top, right, bottom = rect

print(f"Window: {rect}")
print(f"Size: {right-left}x{bottom-top}")

# 使用PIL截图（屏幕坐标）
img = ImageGrab.grab(bbox=rect)

save_path = r'E:\workspace\skills\jingmai-product-publish\logs\jingmai_now.png'
img.save(save_path)
print(f"Saved: {save_path}")
