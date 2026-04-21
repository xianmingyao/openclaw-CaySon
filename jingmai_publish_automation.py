"""
京麦商品发布 - 直接 UFO 自动化
不依赖 LLM，直接坐标点击完成商品上架
"""
import sys
import time
import tempfile
import os
from pathlib import Path

# 添加 desktop-control 到路径
sys.path.insert(0, str(Path(__file__).parent / "skills" / "desktop-control-cli" / "desktop-control"))

import win32gui
import win32con
import win32ui
from PIL import Image

def find_jingmai_window():
    """找到京麦窗口"""
    hwnd = win32gui.FindWindow(None, 'jd_465d1abd3ee76')
    if not hwnd:
        # 尝试查找其他标题
        def enum_handler(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and ('jingmai' in title.lower() or 'jd_' in title.lower()):
                    result.append(hwnd)
        result = []
        win32gui.EnumWindows(lambda h, r=result: enum_handler(h, r) or True, result)
        hwnd = result[0] if result else None
    return hwnd

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

def click_at(hwnd, x, y, delay=0.3):
    """在窗口内指定坐标点击"""
    # 转换为屏幕坐标
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    screen_x = left + x
    screen_y = top + y
    
    # 使用 SetForegroundWindow 确保窗口激活
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.1)
    
    # 发送鼠标点击 (使用屏幕坐标)
    import win32api
    win32api.SetCursorPos((screen_x, screen_y))
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    time.sleep(delay)
    return True

def type_text(text, delay=0.1):
    """输入文本"""
    import win32api
    time.sleep(0.2)
    for char in text:
        win32api.SendMessage(win32gui.GetForegroundWindow(), win32con.WM_CHAR, ord(char), 0)
        time.sleep(delay)

def press_key(key, delay=0.1):
    """按键"""
    import win32api
    win32api.keybd_event(key, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(delay)

def main():
    print("=" * 60)
    print("京麦商品发布自动化 v1.0")
    print("=" * 60)
    
    # 1. 找到京麦窗口
    print("\n[Step 1] 查找京麦窗口...")
    hwnd = find_jingmai_window()
    if not hwnd:
        print("[ERROR] 未找到京麦窗口!")
        return False
    print(f"[OK] 找到京麦窗口: {hwnd}")
    
    # 恢复并激活窗口
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetWindowPos(hwnd, 0, 100, 100, 1280, 800, 0)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    
    rect = win32gui.GetWindowRect(hwnd)
    win_width = rect[2] - rect[0]
    win_height = rect[3] - rect[1]
    print(f"[OK] 窗口大小: {win_width}x{win_height}")
    
    # 2. 截图确认初始状态
    print("\n[Step 2] 截图确认初始状态...")
    screenshot_path = screenshot_window(hwnd)
    print(f"[OK] 截图保存: {screenshot_path}")
    
    # 3. 点击左侧"商品"菜单
    print("\n[Step 3] 点击左侧菜单'商品'...")
    # 左侧菜单区域: X=0-68, 商品菜单位置 Y≈145
    click_x, click_y = 34, 145
    print(f"[INFO] 点击坐标: ({click_x}, {click_y})")
    click_at(hwnd, click_x, click_y)
    
    # 截图确认
    screenshot_window(hwnd, os.path.join(tempfile.gettempdir(), "jingmai_after_menu_click.png"))
    print("[OK] 菜单点击完成")
    
    # 4. 点击"发布商品"子菜单
    print("\n[Step 4] 点击'发布商品'子菜单...")
    # 发布商品在商品菜单下方，Y≈190
    click_x, click_y = 34, 195
    print(f"[INFO] 点击坐标: ({click_x}, {click_y})")
    click_at(hwnd, click_x, click_y, delay=1.0)
    
    # 截图确认
    screenshot_window(hwnd, os.path.join(tempfile.gettempdir(), "jingmai_after_publish_click.png"))
    print("[OK] 发布商品点击完成")
    
    # 5. 等待页面加载
    print("\n[Step 5] 等待页面加载...")
    time.sleep(2)
    
    # 6. 截图查看当前页面
    print("\n[Step 6] 截图查看发布页面...")
    final_screenshot = screenshot_window(hwnd, os.path.join(tempfile.gettempdir(), "jingmai_publish_page.png"))
    print(f"[OK] 截图保存: {final_screenshot}")
    
    print("\n" + "=" * 60)
    print("自动化流程执行完成!")
    print("请检查截图确认是否进入发布商品页面")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
