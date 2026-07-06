# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
import win32clipboard
from PIL import ImageGrab
import time

hwnd = 18289096
rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 截图函数
def save_screenshot(name):
    img = ImageGrab.grab(bbox=rect)
    path = rf'E:\workspace\skills\jingmai-product-publish\logs\{name}.png'
    img.save(path)
    print(f"Saved: {path}")

# 点击函数
def click(x, y, delay=0.3):
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

# 设置剪贴板并粘贴
def paste_text(text):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    time.sleep(0.1)
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl
    win32api.keybd_event(0x56, 0, 0, 0)  # V
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

# 品牌选择框坐标
brand_select = (814, 545)

# Step 1: 点击品牌选择框
print("\nStep 1: 点击品牌选择框")
click(brand_select[0], brand_select[1], 1)
save_screenshot('brand_step1')

# Step 2: 输入品牌名称"公牛"
print("\nStep 2: 输入品牌名称'公牛'")
paste_text('公牛')
time.sleep(1)
save_screenshot('brand_step2')

print("\n请查看截图，如果在搜索结果中看到'公牛'选项，请告诉我，我来点击选择")
print("或者如果下拉框已经关闭，请重新点击品牌选择框...")
