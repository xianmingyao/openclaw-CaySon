# -*- coding: utf-8 -*-
"""京麦WebView精确点击"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish\scripts')

import time
import win32api
import win32con
import pyperclip

# 京麦窗口区域
JM_LEFT, JM_TOP, JM_RIGHT, JM_BOTTOM = 0, 0, 2560, 1392

def convert_to_absolute(screen_x, screen_y):
    """转换窗口坐标到屏幕绝对坐标"""
    return screen_x, screen_y

def click_at(screen_x, screen_y):
    """使用绝对坐标点击"""
    # 获取屏幕分辨率
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    
    # 转换坐标 (京麦窗口从0,0开始，所以直接是绝对坐标)
    abs_x = int(screen_x * 65535 / screen_width)
    abs_y = int(screen_y * 65535 / screen_height)
    
    # 移动鼠标
    win32api.SetCursorPos((screen_x, screen_y))
    time.sleep(0.1)
    
    # 点击
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE, abs_x, abs_y, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_LEFTDOWN, abs_x, abs_y, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_LEFTUP, abs_x, abs_y, 0, 0)
    print(f"Clicked at ({screen_x}, {screen_y})")

def paste_text(text):
    """粘贴文本"""
    pyperclip.copy(text)
    time.sleep(0.15)
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0, 0, 0)  # V
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    print(f"Pasted: {text}")

def press_enter():
    """按回车"""
    win32api.keybd_event(0x0D, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
    print("Pressed Enter")

if __name__ == "__main__":
    print("=== 京麦WebView精确点击 ===")
    
    # 等待用户切换到京麦窗口
    print("请确保京麦窗口在前台...")
    time.sleep(1)
    
    # 搜索框坐标 - 根据页面截图分析，搜索框在页面顶部居中
    # 从截图看，搜索框大约在 1100, 165 左右
    search_x = 1100
    search_y = 165
    
    print(f"\n[1/4] 点击搜索框 ({search_x}, {search_y})...")
    click_at(search_x, search_y)
    time.sleep(0.5)
    
    print("\n[2/4] 输入'插座'...")
    paste_text("插座")
    time.sleep(0.3)
    
    print("\n[3/4] 按回车...")
    press_enter()
    time.sleep(2)
    
    print("\n=== 完成 ===")
    print("请检查京麦是否已搜索'插座'")
