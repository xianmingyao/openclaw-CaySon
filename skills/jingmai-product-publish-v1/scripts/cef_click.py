# -*- coding: utf-8 -*-
"""CEF渲染窗口直接操作"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish\scripts')

import time
import win32gui
import win32api
import win32con
import pyperclip

JM_HWND = 1250920
CEF_HWND = 194251988  # Chrome_RenderWidgetHostHWND

def send_mouse_click(hwnd, x, y):
    """向CEF窗口发送鼠标点击"""
    # 将坐标打包成lParam
    lparam = (y << 16) | (x & 0xFFFF)
    
    # 发送鼠标消息
    win32gui.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)
    time.sleep(0.1)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    time.sleep(0.1)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)
    print(f"Sent click to CEF at ({x}, {y})")

def send_keyboard(hwnd, key, down=True):
    """发送键盘事件"""
    if down:
        win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    else:
        win32gui.SendMessage(hwnd, win32con.WM_KEYUP, key, 0)

def send_ctrl_v(hwnd):
    """发送Ctrl+V"""
    VK_CONTROL = 0x11
    VK_V = 0x56
    
    # Ctrl down
    win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, VK_CONTROL, 0)
    time.sleep(0.05)
    # V down
    win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, VK_V, 0)
    time.sleep(0.05)
    # V up
    win32gui.SendMessage(hwnd, win32con.WM_KEYUP, VK_V, 0)
    time.sleep(0.05)
    # Ctrl up
    win32gui.SendMessage(hwnd, win32con.WM_KEYUP, VK_CONTROL, 0)
    print("Sent Ctrl+V")

if __name__ == "__main__":
    print("=== CEF渲染窗口直接操作 ===")
    
    # 检查CEF窗口
    if win32gui.IsWindow(CEF_HWND):
        print(f"CEF窗口存在: {CEF_HWND}")
        rect = win32gui.GetWindowRect(CEF_HWND)
        print(f"CEF窗口区域: {rect}")
    else:
        print(f"CEF窗口不存在: {CEF_HWND}")
        CEF_HWND = JM_HWND
    
    # 搜索框坐标（根据页面分析）
    search_x = 1100
    search_y = 165
    
    print(f"\n[1/4] 点击搜索框...")
    send_mouse_click(CEF_HWND, search_x, search_y)
    time.sleep(0.5)
    
    print("\n[2/4] 输入'插座'...")
    pyperclip.copy("插座")
    time.sleep(0.1)
    send_ctrl_v(CEF_HWND)
    time.sleep(0.3)
    
    print("\n[3/4] 按回车...")
    send_keyboard(CEF_HWND, win32con.VK_RETURN)
    time.sleep(2)
    
    print("\n=== 完成 ===")
