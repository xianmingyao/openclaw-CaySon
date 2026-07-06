# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
from PIL import ImageGrab
import time
import os

# 坐标转换
def norm_to_actual(norm_x, norm_y):
    return (int(norm_x * 2560 / 1000), int(norm_y * 1392 / 1000))

hwnd = 18289096
rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

# 激活窗口
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 商品信息
product = {
    'title': '公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插 【8位】总控1.6米（新国标防过载）B5440',
    'brand': '公牛',
    'model': 'B5440',
    'jd_price': '70',  # 京东挂网价
}

# 元素坐标
elements = {
    'title_input': norm_to_actual(550, 320),      # 商品标题
    'brand_select': norm_to_actual(318, 392),      # 品牌选择
    'model_input': norm_to_actual(628, 392),       # 型号
    'jd_price': norm_to_actual(628, 497),          # 京东价
    'protection_level': norm_to_actual(318, 762),   # 防护等级
    'material': norm_to_actual(473, 762),         # 材质
    'publish': norm_to_actual(475, 975),           # 发布按钮
}

print("\n商品信息:")
for k, v in product.items():
    print(f"  {k}: {v}")

print("\n元素坐标:")
for k, v in elements.items():
    print(f"  {k}: {v}")

# 截图保存函数
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

# 输入文本函数
def input_text(text, delay=0.05):
    for char in text:
        win32api.SendMessage(win32gui.GetForegroundWindow(), win32con.WM_CHAR, ord(char), 0)
        time.sleep(delay)

# Step 1: 点击商品标题输入框并输入
print("\n" + "="*50)
print("Step 1: 填写商品标题")
print("="*50)
x, y = elements['title_input']
click(x, y, 0.5)
print(f"Clicked title input at ({x}, {y})")

# 清空并输入标题
time.sleep(0.3)
# 全选
win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl
win32api.keybd_event(0x41, 0, 0, 0)  # A
win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
time.sleep(0.2)

# 输入标题
input_text(product['title'], 0.03)
print(f"Input title: {product['title'][:30]}...")
save_screenshot('s1_title')

# Step 2: 点击品牌选择
print("\n" + "="*50)
print("Step 2: 选择品牌")
print("="*50)
x, y = elements['brand_select']
click(x, y, 1)
print(f"Clicked brand select at ({x}, {y})")

# 等待品牌下拉框出现
time.sleep(1)
save_screenshot('s2_brand_dropdown')

# 输入品牌名称搜索
input_text(product['brand'], 0.1)
time.sleep(1)
save_screenshot('s3_brand_search')

print("\n请手动选择品牌下拉框中的 '公牛' 选项")
print("选择完成后告诉我，我继续填写其他信息")
