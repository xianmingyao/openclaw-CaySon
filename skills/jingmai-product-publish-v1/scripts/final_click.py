"""
京麦 - 精确定位点击
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

# 获取实际截图比对视图
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\before_action.png')

# 用精确坐标点击"金属加工配件"
target_x = 527
target_y = 232

print(f"Click '金属加工配件' at ({target_x}, {target_y})")
win32api.SetCursorPos((target_x, target_y))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(2)

# 截图检查
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\after_category_click.png')

# 再点下一步
print(f"Click '下一步' at (540, 938)")
win32api.SetCursorPos((540, 938))
time.sleep(0.2)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
time.sleep(0.1)
win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
time.sleep(3)

# 最终截图
img = ImageGrab.grab(bbox=rect)
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\result.png')
print("Done! Check result.png")
