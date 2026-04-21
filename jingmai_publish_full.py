"""
京麦商品发布 - 完整自动化流程
1. 选择三级分类
2. 点击下一步
3. 填写商品信息
"""
import sys
import time
import tempfile
import os
import shutil
from pathlib import Path

import win32gui
import win32con
import win32ui
import win32clipboard
from PIL import Image

def find_jingmai_window():
    """找到京麦窗口"""
    hwnd = win32gui.FindWindow(None, 'jd_465d1abd3ee76')
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

def click_in_window(hwnd, rel_x, rel_y, delay=0.5):
    """在窗口内相对坐标点击"""
    import win32api
    
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    abs_x = left + rel_x
    abs_y = top + rel_y
    
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.1)
    
    win32api.SetCursorPos((abs_x, abs_y))
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    time.sleep(delay)

def paste_text(text):
    """使用剪贴板粘贴文本"""
    # 保存当前剪贴板内容
    old_data = None
    try:
        win32clipboard.OpenClipboard()
        old_data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except:
        pass
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
    
    # 设置新文本到剪贴板
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    
    # 粘贴
    import win32api
    time.sleep(0.2)
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord('V'), 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    time.sleep(0.3)
    
    # 恢复旧剪贴板内容
    if old_data:
        time.sleep(0.2)
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        try:
            win32clipboard.SetClipboardText(old_data, win32clipboard.CF_UNICODETEXT)
        except:
            pass
        finally:
            win32clipboard.CloseClipboard()

def main():
    print("=" * 60)
    print("京麦商品发布自动化 v3.0 - 完整流程")
    print("=" * 60)
    
    # 1. 找到京麦窗口
    print("\n[Step 1] 查找京麦窗口...")
    hwnd = find_jingmai_window()
    if not hwnd:
        print("[ERROR] 未找到京麦窗口!")
        return False
    
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    print(f"[OK] 窗口: {hwnd}")
    
    # 2. 截图确认初始状态
    print("\n[Step 2] 截图确认初始状态...")
    screenshot_window(hwnd, os.path.join(tempfile.gettempdir(), "jingmai_init.png"))
    print("[OK] 已截图")
    
    # 3. 选择一级分类: 工业品
    print("\n[Step 3] 选择一级分类 '工业品'...")
    # 工业品在左侧列表，窗口坐标约 X=100, Y=200
    click_in_window(hwnd, 100, 220, delay=1.0)
    print("[OK] 已点击'工业品'")
    
    # 4. 选择二级分类: 传感器
    print("\n[Step 4] 选择二级分类 '传感器'...")
    # 传感器在展开后的列表
    click_in_window(hwnd, 100, 280, delay=1.0)
    print("[OK] 已点击'传感器'")
    
    # 5. 选择三级分类: 气体传感器
    print("\n[Step 5] 选择三级分类 '气体传感器'...")
    # 气体传感器
    click_in_window(hwnd, 100, 340, delay=1.0)
    print("[OK] 已点击'气体传感器'")
    
    # 6. 点击"下一步"按钮
    print("\n[Step 6] 点击'下一步，完善商品信息'...")
    # 按钮在页面底部
    click_in_window(hwnd, 640, 750, delay=2.0)
    print("[OK] 已点击'下一步'")
    
    # 7. 等待商品信息页面加载
    print("\n[Step 7] 等待商品信息页面...")
    time.sleep(3)
    
    # 8. 截图确认
    print("\n[Step 8] 截图确认商品信息页面...")
    screenshot_path = screenshot_window(hwnd, os.path.join(tempfile.gettempdir(), "jingmai_product_form.png"))
    
    dst = r"E:\workspace\jingmai_product_form.png"
    shutil.copy(screenshot_path, dst)
    print(f"[OK] 截图: {dst}")
    
    print("\n" + "=" * 60)
    print("分类选择完成！")
    print("请检查截图确认是否进入商品信息填写页面")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
