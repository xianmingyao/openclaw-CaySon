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

# 商品信息
product = {
    'title': '公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插【8位】总控5米（新国标防过载）B5440',
    'brand': '公牛',
    'model': 'B5440',
    'jd_price': '70',
}

# 元素坐标
coords = {
    'brand_select': (814, 545),      # 品牌选择
    'model_input': (1607, 545),     # 型号
    'jd_price': (1607, 691),        # 京东价
    'market_price': (814, 691),     # 市场价
    'publish': (1216, 1357),        # 发布按钮
}

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

# 清空输入框
def clear_input():
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl
    win32api.keybd_event(0x41, 0, 0, 0)  # A
    win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    win32api.keybd_event(0x2E, 0, 0, 0)  # Delete
    time.sleep(0.2)

# Step 1: 填写型号
print("\n" + "="*50)
print("Step 1: 填写型号")
print("="*50)
click(coords['model_input'][0], coords['model_input'][1], 0.5)
clear_input()
paste_text(product['model'])
save_screenshot('01_model')
print(f"Model filled: {product['model']}")

# Step 2: 填写京东价
print("\n" + "="*50)
print("Step 2: 填写京东价")
print("="*50)
click(coords['jd_price'][0], coords['jd_price'][1], 0.5)
clear_input()
paste_text(product['jd_price'])
save_screenshot('02_jd_price')
print(f"JD Price filled: {product['jd_price']}")

# Step 3: 填写市场价 (高于京东价20%)
print("\n" + "="*50)
print("Step 3: 填写市场价")
print("="*50)
market_price = str(int(float(product['jd_price']) * 1.2))  # 20% higher
click(coords['market_price'][0], coords['market_price'][1], 0.5)
clear_input()
paste_text(market_price)
save_screenshot('03_market_price')
print(f"Market Price filled: {market_price}")

print("\n" + "="*50)
print("当前填写状态:")
print("="*50)
print(f"  商品标题: {len(product['title'])}字符 ✓")
print(f"  品牌: 需要手动选择 '公牛'")
print(f"  型号: {product['model']} ✓")
print(f"  京东价: {product['jd_price']} ✓")
print(f"  市场价: {market_price} ✓")

print("\n请手动选择品牌 '公牛'，然后告诉我继续...")
