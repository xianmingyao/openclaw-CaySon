# -*- coding: utf-8 -*-
import win32gui
import win32con
import win32api
import win32clipboard
from PIL import ImageGrab
import time
import json

# 坐标转换
def norm_to_actual(norm_x, norm_y):
    return (int(norm_x * 2560 / 1000), int(norm_y * 1392 / 1000))

hwnd = 18289096
rect = win32gui.GetWindowRect(hwnd)
print(f"Window: {rect}")

win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 商品数据
product = {
    'title': '公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插 【8位】总控5米（新国标防过载）B5440',
    'brand': '公牛',
    'model': 'B5440',
    'jd_price': '70',
}

# 加载京东数据
try:
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_product_data.json', 'r', encoding='utf-8') as f:
        jd_data = json.load(f)
    print(f"JD Data loaded: {jd_data.get('title', 'N/A')[:30]}...")
except Exception as e:
    print(f"JD Data load error: {e}")
    jd_data = {}

# 合并数据
if jd_data.get('title'):
    product['title'] = jd_data['title'].split(' ')[0] + ' B5440'  # 使用更简短的标题

# 元素坐标 (实际像素)
coords = {
    'title_input': (1408, 445),      # 商品标题
    'brand_select': (814, 545),      # 品牌选择
    'model_input': (1607, 545),       # 型号
    'jd_price': (1607, 691),         # 京东价
    'publish': (1216, 1357),         # 发布按钮
}

print("\n商品信息:")
for k, v in product.items():
    print(f"  {k}: {v}")

print("\n元素坐标:")
for k, v in coords.items():
    print(f"  {k}: {v}")

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

# Step 1: 填写商品标题
print("\n" + "="*50)
print("Step 1: 填写商品标题")
print("="*50)
click(coords['title_input'][0], coords['title_input'][1], 0.5)
clear_input()
paste_text(product['title'])
save_screenshot('01_title')
print(f"Title filled: {product['title'][:30]}...")

# Step 2: 选择品牌
print("\n" + "="*50)
print("Step 2: 选择品牌")
print("="*50)
click(coords['brand_select'][0], coords['brand_select'][1], 1)
save_screenshot('02_brand_click')

# 输入品牌名称搜索
paste_text(product['brand'])
time.sleep(1)
save_screenshot('03_brand_search')

print("\n请手动选择品牌下拉框中的 '公牛' 选项")
print("选择完成后告诉我继续填写其他信息...")

# 保存当前数据状态
with open(r'E:\workspace\skills\jingmai-product-publish\logs\fill_status.json', 'w', encoding='utf-8') as f:
    json.dump({
        'product': product,
        'coords': coords,
        'status': 'waiting_for_brand_selection'
    }, f, ensure_ascii=False, indent=2)
