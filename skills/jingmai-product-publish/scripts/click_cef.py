# -*- coding: utf-8 -*-
"""直接操作京麦CEF WebView"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish\scripts')

import time
import win32gui
import win32api
import win32con

# 京麦主窗口HWND
JM_HWND = 1250920

def get_cef_hwnd(parent_hwnd):
    """找到CEF浏览器窗口的HWND"""
    cef_hwnd = None
    def enum_child(hwnd, ctx):
        nonlocal cef_hwnd
        cls = win32gui.GetClassName(hwnd)
        if 'CefBrowserWindow' in cls or 'Chrome_RenderWidgetHostHWND' in cls:
            cef_hwnd = hwnd
            print(f"Found CEF window: HWND={hwnd}, Class={cls}")
        return True
    win32gui.EnumChildWindows(parent_hwnd, enum_child, None)
    return cef_hwnd

def click_at(hwnd, x, y):
    """向指定窗口发送点击事件"""
    # 先把鼠标移到目标位置
    win32api.SetCursorPos((x, y))
    time.sleep(0.1)
    
    # 发送鼠标事件到目标窗口
    lparam = (y << 16) | (x & 0xFFFF)
    
    # WM_MOUSEMOVE
    win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
    time.sleep(0.05)
    
    # WM_LBUTTONDOWN
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, lparam)
    time.sleep(0.05)
    
    # WM_LBUTTONUP
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
    print(f"Sent click to HWND {hwnd} at ({x}, {y})")

def send_text_to_cef(hwnd, text):
    """发送文本到CEF窗口"""
    import pyperclip
    pyperclip.copy(text)
    time.sleep(0.1)
    
    # Ctrl+V
    win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl
    win32api.keybd_event(0x56, 0, 0, 0)    # V
    time.sleep(0.05)
    win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    print(f"Sent text to CEF: {text}")

if __name__ == "__main__":
    print("=== 操作京麦CEF WebView ===")
    
    # 找到CEF窗口
    cef_hwnd = get_cef_hwnd(JM_HWND)
    if not cef_hwnd:
        print("未找到CEF窗口!")
        # 使用主窗口
        cef_hwnd = JM_HWND
        print(f"使用主窗口HWND: {cef_hwnd}")
    
    # 获取CEF窗口区域
    rect = win32gui.GetWindowRect(cef_hwnd)
    print(f"CEF窗口区域: {rect}")
    
    # 计算搜索框的坐标（相对于CEF窗口）
    # 根据页面布局，搜索框大约在窗口上方居中位置
    search_x = 1100
    search_y = 165
    
    print(f"\n[1/4] 点击搜索框 ({search_x}, {search_y})...")
    click_at(cef_hwnd, search_x, search_y)
    time.sleep(0.5)
    
    print("\n[2/4] 输入'插座'...")
    send_text_to_cef(cef_hwnd, "插座")
    time.sleep(0.3)
    
    print("\n[3/4] 按回车...")
    win32api.keybd_event(0x0D, 0, 0, 0)  # Enter
    time.sleep(0.05)
    win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(2)
    
    print("\n=== 完成 ===")
