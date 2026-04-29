# -*- coding: utf-8 -*-
"""轻量级京麦操作 - 纯Win32，无pywinauto"""
import win32gui
import win32api
import win32con
import time
import os

# 京麦窗口HWND
JM_HWND = 1250920

def click(x, y):
    """纯Win32点击"""
    # 先把鼠标移到目标位置
    win32api.SetCursorPos((x, y))
    time.sleep(0.1)
    # 按下
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.05)
    # 抬起
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    time.sleep(0.2)

def paste_text(text):
    """使用剪贴板粘贴"""
    import pyperclip
    # 复制到剪贴板
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

def activate_window():
    """激活京麦窗口"""
    if win32gui.IsIconic(JM_HWND):
        win32gui.ShowWindow(JM_HWND, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(JM_HWND)
    time.sleep(0.3)

if __name__ == "__main__":
    print("=== 轻量级京麦操作 ===")
    print(f"窗口HWND: {JM_HWND}")
    
    # 激活窗口
    print("\n[1/4] 激活京麦窗口...")
    activate_window()
    
    # 点击搜索框 (x=1150, y=165 是估算位置)
    print("[2/4] 点击搜索框...")
    click(1150, 165)
    time.sleep(0.5)
    
    # 输入"插座"
    print("[3/4] 输入关键词...")
    paste_text("插座")
    time.sleep(0.3)
    
    # 按回车
    print("[4/4] 搜索...")
    press_enter()
    
    print("\n=== 完成 ===")
    print("请检查京麦窗口中的搜索结果")
