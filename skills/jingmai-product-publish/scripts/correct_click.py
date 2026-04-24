"""
京麦 - 正确坐标点击
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
time.sleep(0.3)

# Step 1: 点击"金属加工配件" (正确屏幕坐标)
target_x = 1787
target_y = 234

print(f"Step 1: Click '金属加工配件' at screen ({target_x}, {target_y})")
win32api.SetCursorPos((target_x, target_y))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(1.5)

# 截图
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\category_selected.png')
print("Screenshot saved")

# Step 2: 点击"下一步"
next_x = 498
next_y = 938

print(f"Step 2: Click '下一步' at screen ({next_x}, {next_y})")
win32api.SetCursorPos((next_x, next_y))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

# 最终截图
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\product_info_page.png')
print("Final screenshot saved")
print("Done!")
