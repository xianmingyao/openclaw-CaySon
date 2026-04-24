"""
京麦 - 基于实际像素坐标操作
"""
import win32api
import win32con
import win32gui
from PIL import ImageGrab
import time

hwnd = 18289096
rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# Step 1: 点击"金属加工配件" (530, 232)
print("Step 1: Click category at (530, 232)...")
win32api.SetCursorPos((530, 232))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\s1.png')

# Step 2: 点击"下一步" (1275, 938)
print("Step 2: Click next at (1275, 938)...")
win32api.SetCursorPos((1275, 938))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(3)

img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\s2.png')
print("Done!")
