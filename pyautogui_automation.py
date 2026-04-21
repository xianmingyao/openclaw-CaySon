"""
京麦商品发布 - PyAutoGUI 直接自动化
使用 PyAutoGUI 直接操作京麦窗口
"""
import sys
import time
import tempfile
import os
import shutil
from pathlib import Path

import pyautogui
import win32gui
import win32con
import win32ui

# 设置 PyAutoGUI 安全区域
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

def find_jingmai_window():
    """找到京麦窗口"""
    hwnd = win32gui.FindWindow(None, 'jd_465d1abd3ee76')
    if not hwnd:
        def enum_handler(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ('jingmai' in title.lower() or 'jd_' in title.lower()):
                    result.append(hwnd)
        result = []
        win32gui.EnumWindows(lambda h, r=result: enum_handler(h, r) or True, result)
        hwnd = result[0] if result else None
    return hwnd

def activate_window(hwnd):
    """激活窗口"""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(hwnd, 0, 0, 0, 2560, 1440, 0)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)

def get_window_rect(hwnd):
    """获取窗口矩形"""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    return left, top, right, bottom

def screenshot_window(hwnd, save_path=None):
    """截取窗口截图"""
    if not save_path:
        save_path = os.path.join(tempfile.gettempdir(), f"jingmai_{int(time.time())}.png")
    
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    
    hwindc = win32gui.GetWindowDC(hwnd)
    mfcdc = win32ui.CreateDCFromHandle(hwindc)
    savedc = mfcdc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfcdc, width, height)
    savedc.SelectObject(bitmap)
    savedc.BitBlt((0, 0), (width, height), mfcdc, (0, 0), win32con.SRCCOPY)
    
    bitmap.SaveBitmapFile(savedc, save_path)
    
    win32gui.DeleteObject(bitmap.GetHandle())
    savedc.DeleteDC()
    mfcdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwindc)
    
    return save_path

def click_absolute(x, y, delay=0.5):
    """使用 PyAutoGUI 点击绝对屏幕坐标"""
    pyautogui.click(x, y)
    time.sleep(delay)

def click_relative(hwnd, rel_x, rel_y, delay=0.5):
    """点击窗口内相对坐标"""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    abs_x = left + rel_x
    abs_y = top + rel_y
    pyautogui.click(abs_x, abs_y)
    time.sleep(delay)

def main():
    print("=" * 60)
    print("京麦商品发布 - PyAutoGUI 自动化")
    print("=" * 60)
    
    # 1. 找到京麦窗口
    print("\n[Step 1] 查找京麦窗口...")
    hwnd = find_jingmai_window()
    if not hwnd:
        print("[ERROR] 未找到京麦窗口!")
        return False
    
    activate_window(hwnd)
    print(f"[OK] 窗口: {hwnd}")
    
    left, top, right, bottom = get_window_rect(hwnd)
    print(f"[OK] 窗口区域: ({left}, {top}, {right}, {bottom})")
    
    # 2. 截图当前状态
    print("\n[Step 2] 截图...")
    screenshot_window(hwnd, os.path.join(tempfile.gettempdir(), "jingmai_init2.png"))
    print("[OK] 已截图")
    
    # 3. 确认已在类目选择页面，点击"下一步"按钮
    # 按钮在页面底部右侧，基于 2560x1392 窗口
    # "下一步" 按钮文本大约在 Y=1340 高度
    print("\n[Step 3] 点击'下一步'按钮...")
    
    # 使用 pyautogui 的文字识别找按钮
    # 如果没有文字识别，手动指定按钮位置
    # 在 2560x1392 窗口中，"下一步"按钮通常在右下方
    # 尝试点击多个可能位置
    
    # 先点击确认区域 - 右侧确认按钮
    # 基于观察，"下一步"按钮在 X=2100-2300, Y=1300-1350
    positions_to_try = [
        (2150, 1310),  # 主要猜测位置
        (2200, 1310),
        (2100, 1310),
        (2250, 1310),
        (2150, 1330),
        (2200, 1330),
    ]
    
    for attempt, (x, y) in enumerate(positions_to_try, 1):
        print(f"\n[Attempt {attempt}/6] 点击坐标: ({x}, {y})")
        click_absolute(x, y, delay=1.0)
        
        # 截图查看是否跳转
        screenshot_window(hwnd, os.path.join(tempfile.gettempdir(), f"jingmai_attempt_{attempt}.png"))
        print(f"       已截图")
    
    # 4. 检查是否成功
    print("\n[Step 4] 检查最终状态...")
    final_screenshot = screenshot_window(hwnd, os.path.join(tempfile.gettempdir(), "jingmai_final.png"))
    
    dst = r"E:\workspace\jingmai_final.png"
    shutil.copy(final_screenshot, dst)
    print(f"[OK] 最终截图: {dst}")
    
    print("\n" + "=" * 60)
    print("请检查截图确认是否进入商品信息页面")
    print("=" * 60)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
