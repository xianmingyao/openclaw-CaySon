"""
京麦 - 点击下一步按钮
"""
import win32api
import win32con
import win32gui
from PIL import ImageGrab
import time

hwnd = 18289096

print("Current window rect:", win32gui.GetWindowRect(hwnd))

# 下一步按钮坐标 (窗口内: y=938, x=498)
# 全屏模式(0,0,2560,1392), 所以屏幕坐标也是 (498, 938)
click_x = 498
click_y = 938

print(f"Clicking at screen ({click_x}, {click_y})")

# 确保窗口在前台
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.3)

# 点击
win32api.SetCursorPos((click_x, click_y))
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.05)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
print("Click done!")

# 等待页面跳转
time.sleep(2)

# 截图
rect = win32gui.GetWindowRect(hwnd)
img = ImageGrab.grab(bbox=rect)
save_path = r'E:\workspace\skills\jingmai-product-publish\logs\after_next_click.png'
img.save(save_path)
print(f"Screenshot saved: {save_path}")
