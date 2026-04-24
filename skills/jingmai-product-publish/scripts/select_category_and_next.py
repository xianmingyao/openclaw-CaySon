"""
京麦 - 选择完整类目 + 点击下一步
"""
import win32api
import win32con
import win32gui
from PIL import ImageGrab
import time

hwnd = 18289096

print("Step 1: Click '金属加工配件' in third column")
# 第三列"金属加工配件"坐标 - 从截图分析大约在 y=400, x=492
# 基于全屏窗口(0,0,2560,1392)
click_x_3rd = 540  # 第三列x中心
click_y_3rd = 420  # 第三列y位置

win32gui.SetForegroundWindow(hwnd)
time.sleep(0.3)

win32api.SetCursorPos((click_x_3rd, click_y_3rd))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
print(f"Clicked at ({click_x_3rd}, {click_y_3rd})")
time.sleep(1)

# 截图确认
rect = win32gui.GetWindowRect(hwnd)
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\after_select_category.png')
print("Screenshot saved")

print("\nStep 2: Click Next button")
# 下一步按钮坐标
click_x_next = 498
click_y_next = 938

win32api.SetCursorPos((click_x_next, click_y_next))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
print(f"Clicked Next at ({click_x_next}, {click_y_next})")
time.sleep(2)

# 最终截图
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\final_result.png')
print("Final screenshot saved")
