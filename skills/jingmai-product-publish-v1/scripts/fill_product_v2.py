# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time
import win32clipboard

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
    return path

# 点击函数
def click(x, y, delay=0.3):
    win32api.SetCursorPos((x, y))
    time.sleep(0.2)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(delay)

# 设置剪贴板文本
def set_clipboard(text):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()

# 粘贴函数 (Ctrl+V)
def paste():
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
    win32api.keybd_event(0x56, 0, 0, 0)   # V down
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)

# 商品信息
product = {
    'title': '公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插 【8位】总控1.6米（新国标防过载）B5440',
    'brand': '公牛',
    'model': 'B5440',
    'jd_price': '70',
}

# 元素坐标
title_input = (1408, 445)
brand_select = (814, 545)
model_input = (1607, 545)
jd_price = (1607, 691)
publish = (1216, 1357)

print("\n开始填写商品信息...")

# Step 1: 点击商品标题输入框
print("\nStep 1: 点击商品标题输入框")
click(title_input[0], title_input[1], 0.5)

# 清空现有内容 (Ctrl+A -> Delete)
win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl
win32api.keybd_event(0x41, 0, 0, 0)  # A
win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.2)
win32api.keybd_event(0x2E, 0, 0, 0)  # Delete
time.sleep(0.2)

# 设置标题到剪贴板并粘贴
print("粘贴商品标题...")
set_clipboard(product['title'])
paste()
time.sleep(0.5)
save_screenshot('step1_title')
print("标题已填写")

# Step 2: 选择品牌
print("\nStep 2: 选择品牌")
click(brand_select[0], brand_select[1], 1)
save_screenshot('step2_brand')

# 在品牌搜索框中输入"公牛"
print("输入品牌名称...")
set_clipboard('公牛')
paste()
time.sleep(1)
save_screenshot('step3_brand_search')

print("\n请在品牌下拉框中选择 '公牛' 选项")
print("选择完成后告诉我继续...")
