"""
京麦 - 选择类目 + 下一步
"""
import win32api
import win32con
import win32gui
from PIL import ImageGrab
import time

hwnd = 18289096

# 窗口信息
rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")  # (0, 0, 2560, 1392)

win32gui.SetForegroundWindow(hwnd)
time.sleep(0.3)

# Step 1: 点击"金属加工配件" (窗口内 y=233, x=515)
# 全屏模式，窗口坐标=屏幕坐标
target_y = 233
target_x = 515

print(f"Step 1: Click '金属加工配件' at ({target_x}, {target_y})")
win32api.SetCursorPos((target_x, target_y))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(1.5)

# 截图1
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\step1_done.png')
print("Step 1 screenshot saved")

# Step 2: 点击"下一步"按钮 (窗口内 y=938, x=498)
next_y = 938
next_x = 498

print(f"Step 2: Click '下一步' at ({next_x}, {next_y})")
win32api.SetCursorPos((next_x, next_y))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

# 截图2
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\step2_done.png')
print("Step 2 screenshot saved")
print("Done!")
