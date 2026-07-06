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

# 完整商品标题
full_title = '公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插 【8位】总控5米（新国标防过载）B5440'

# 元素坐标
title_input = (1408, 445)

print(f"\n完整标题 ({len(full_title)}字符):")
print(full_title)

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

# Step 1: 点击标题输入框
print("\n" + "="*50)
print("Step 1: 点击标题输入框")
print("="*50)
click(title_input[0], title_input[1], 0.5)

# Step 2: 清空现有内容
print("\nStep 2: 清空现有内容")
clear_input()

# Step 3: 粘贴完整标题
print("\nStep 3: 粘贴完整标题")
paste_text(full_title)

# 截图确认
save_screenshot('full_title_filled')

print(f"\n完整标题已填写: {len(full_title)}字符")
