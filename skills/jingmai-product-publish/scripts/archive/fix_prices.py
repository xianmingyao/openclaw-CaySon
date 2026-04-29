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

# 价格计算（京东价=70）
jd_price = 70
purchase_price = round(jd_price * 0.95, 2)  # 66.5
market_price = round(jd_price / 0.85, 2)  # 82.35

print(f"\n价格计算（京东价={jd_price}）：")
print(f"  采购价 = {jd_price} × 0.95 = {purchase_price}")
print(f"  市场价 = {jd_price} ÷ 0.85 = {market_price}")

# 元素坐标
coords = {
    'market_price': (814, 691),     # 市场价
    'purchase_price': (1999, 691),  # 采购价（新增）
    'jd_price': (1597, 691),       # 京东价
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

# Step 1: 修正市场价
print("\n" + "="*50)
print(f"Step 1: 修正市场价 (当前84 -> 应该是{market_price})")
print("="*50)
click(coords['market_price'][0], coords['market_price'][1], 0.5)
clear_input()
paste_text(str(market_price))
save_screenshot('fix_market_price')
print(f"Market price set to: {market_price}")

# Step 2: 填写采购价
print("\n" + "="*50)
print(f"Step 2: 填写采购价 ({purchase_price})")
print("="*50)
click(coords['purchase_price'][0], coords['purchase_price'][1], 0.5)
clear_input()
paste_text(str(purchase_price))
save_screenshot('fix_purchase_price')
print(f"Purchase price set to: {purchase_price}")

print("\n" + "="*50)
print("价格填写完成:")
print("="*50)
print(f"  京东价: {jd_price} (固定)")
print(f"  采购价: {purchase_price} = {jd_price} × 0.95")
print(f"  市场价: {market_price} = {jd_price} ÷ 0.85")
