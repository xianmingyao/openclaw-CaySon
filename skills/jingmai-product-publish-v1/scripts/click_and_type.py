# -*- coding: utf-8 -*-
"""京麦商品发布自动化"""
import win32gui
import win32api
import win32con
import time
import sys

# 京麦窗口HWND
hwnd = 1250920

def click_at(x, y):
    """在指定坐标点击"""
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.3)

def type_text(text):
    """输入文本"""
    for char in text:
        win32api.SendMessage(hwnd, win32con.WM_CHAR, ord(char), 0)
        time.sleep(0.05)

def press_key(key):
    """按键"""
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(0.1)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, key, 0)
    time.sleep(0.1)

# 设置焦点
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

print("=== 步骤1: 点击搜索框 ===")
# 搜索框位置 (根据页面布局分析)
search_x, search_y = 1100, 165
click_at(search_x, search_y)
time.sleep(0.5)

print("=== 步骤2: 输入关键词 ===")
type_text("插座")
time.sleep(0.5)

print("=== 步骤3: 按回车搜索 ===")
press_key(win32con.VK_RETURN)
time.sleep(1)

print("=== 完成 ===")
