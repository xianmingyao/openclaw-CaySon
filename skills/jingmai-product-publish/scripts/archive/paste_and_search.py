# -*- coding: utf-8 -*-
"""京麦商品发布 - 使用剪贴板输入"""
import win32gui
import win32api
import win32con
import time
import pyperclip

# 京麦窗口HWND
hwnd = 1250920

def click_at(x, y):
    """在指定坐标点击"""
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.3)

def paste_text(text):
    """使用Ctrl+V粘贴文本"""
    # 复制文本到剪贴板
    pyperclip.copy(text)
    time.sleep(0.2)
    
    # Ctrl+V 粘贴
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
    win32api.keybd_event(0x56, 0, 0, 0)  # V down
    time.sleep(0.1)
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)  # V up
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up
    time.sleep(0.3)

def press_enter():
    """按回车键"""
    win32api.keybd_event(0x0D, 0, 0, 0)  # Enter down
    time.sleep(0.1)
    win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)  # Enter up
    time.sleep(0.3)

# 设置焦点
win32gui.SetForegroundWindow(hwnd)
time.sleep(0.5)

print("=== 步骤1: 点击搜索框 ===")
# 搜索框位置 
search_x, search_y = 1100, 165
click_at(search_x, search_y)
time.sleep(0.5)

print("=== 步骤2: 粘贴'插座' ===")
paste_text("插座")
time.sleep(0.5)

print("=== 步骤3: 按回车 ===")
press_enter()
time.sleep(1)

print("=== 完成 ===")
