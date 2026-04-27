# -*- coding: utf-8 -*-
"""直接操作京麦窗口 - 使用SendMessage"""
import time
import win32gui
import win32api
import win32con
import ctypes

# 京麦窗口HWND
JM_HWND = 1250920

def click_at_absolute(screen_x, screen_y):
    """使用绝对坐标点击"""
    # 确保鼠标在正确位置
    win32api.SetCursorPos((screen_x, screen_y))
    time.sleep(0.1)
    
    # 使用绝对坐标的mouse_event
    # MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE | MOUSEEVENTF_LEFTDOWN | MOUSEEVENTF_LEFTUP
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE, 
                        screen_x * 65535 // 2560, 
                        screen_y * 65535 // 1392, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_LEFTDOWN, 
                        screen_x * 65535 // 2560, 
                        screen_y * 65535 // 1392, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_LEFTUP, 
                        screen_x * 65535 // 2560, 
                        screen_y * 65535 // 1392, 0, 0)
    print(f"Clicked at screen({screen_x}, {screen_y})")

def paste_text(text):
    """使用剪贴板粘贴"""
    import pyperclip
    pyperclip.copy(text)
    time.sleep(0.1)
    
    # Ctrl+V
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
    
    # 获取窗口区域
    rect = win32gui.GetWindowRect(JM_HWND)
    print(f"窗口区域: {rect}")
    
    # 搜索框的绝对屏幕坐标 (窗口从0,0开始，所以直接用窗口坐标)
    search_x = 1100
    search_y = 165
    
    print(f"\n[1/4] 点击搜索框 ({search_x}, {search_y})...")
    click_at_absolute(search_x, search_y)
    time.sleep(0.5)
    
    print("\n[2/4] 输入'插座'...")
    paste_text("插座")
    time.sleep(0.3)
    
    print("\n[3/4] 按回车...")
    press_enter()
    time.sleep(2)
    
    print("\n=== 完成 ===")
    print("请检查京麦窗口")
