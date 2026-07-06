"""
京麦 - 点击变蓝的下一步按钮
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

# 点击"下一步" (按钮中心 498, 938)
next_x = 498
next_y = 938

print(f"Click '下一步' at ({next_x}, {next_y})")
win32api.SetCursorPos((next_x, next_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
print("Clicked!")
time.sleep(3)

# 截图
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\product_info_final.png')
print("Saved: product_info_final.png")
