# -*- coding: utf-8 -*-
"""直接操作京麦窗口"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish\scripts')

import time
import win32gui
import win32api
import win32con
from pywinauto import Application

# 京麦窗口HWND
JM_HWND = 1250920

def click_at(hwnd, x, y):
    """在窗口内指定坐标点击"""
    # 确保窗口在前台
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    
    # 将窗口坐标转换为屏幕坐标
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    screen_x = left + x
    screen_y = top + y
    
    # 点击
    win32api.SetCursorPos((screen_x, screen_y))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print(f"Clicked at window({x}, {y}) = screen({screen_x}, {screen_y})")

def type_text(text):
    """输入文本"""
    import pyperclip
    pyperclip.copy(text)
    time.sleep(0.1)
    
    # Ctrl+V 粘贴
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl
    win32api.keybd_event(0x56, 0, 0, 0)  # V
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)

def press_enter():
    """按回车"""
    win32api.keybd_event(0x0D, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.2)

if __name__ == "__main__":
    print("=== 直接操作京麦 ===")
    print(f"窗口HWND: {JM_HWND}")
    
    # 获取窗口信息
    left, top, right, bottom = win32gui.GetWindowRect(JM_HWND)
    print(f"窗口区域: ({left}, {top}) - ({right}, {bottom})")
    width = right - left
    height = bottom - top
    print(f"窗口大小: {width}x{height}")
    
    # 1. 点击搜索框 (根据页面布局，搜索框大约在窗口中部偏上)
    # 窗口2560x1392，搜索框大约在 (1280, 165) 左右
    search_x = 1100
    search_y = 165
    
    print(f"\n[1/4] 点击搜索框 ({search_x}, {search_y})...")
    click_at(JM_HWND, search_x, search_y)
    time.sleep(0.5)
    
    # 2. 输入"插座"
    print("\n[2/4] 输入'插座'...")
    type_text("插座")
    time.sleep(0.3)
    
    # 3. 按回车
    print("\n[3/4] 按回车...")
    press_enter()
    time.sleep(2)
    
    # 4. 点击"工业品"类目 (大约在左侧中间位置)
    print("\n[4/4] 点击'工业品'...")
    click_at(JM_HWND, 300, 400)
    
    print("\n=== 完成 ===")
