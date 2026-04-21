"""
京麦商品发布 - 继续自动化
选择分类并填写商品信息
"""
import sys
import time
import tempfile
import os
from pathlib import Path

import win32gui
import win32con
import win32ui
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

def click_at_abs(hwnd, abs_x, abs_y, delay=0.3):
    """在窗口内指定坐标点击（屏幕绝对坐标）"""
    import win32api
    
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.1)
    
    win32api.SetCursorPos((abs_x, abs_y))
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
    time.sleep(delay)

def click_in_window(hwnd, rel_x, rel_y, delay=0.3):
    """在窗口内相对坐标点击"""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    abs_x = left + rel_x
    abs_y = top + rel_y
    click_at_abs(hwnd, abs_x, abs_y, delay)

def type_text_direct(text, delay=0.1):
    """直接输入文本到当前焦点窗口"""
    import win32api
    time.sleep(0.3)
    for char in text:
        # 检查是否是中文（需要特殊处理）
        if '\u4e00' <= char <= '\u9fff':
            # 中文输入 - 需要切换到中文输入法或粘贴
            pass
        else:
            vk = win32api.VkKeyScan(char)
            if vk != -1:
                key = vk & 0xff
                modifiers = vk >> 8
                if modifiers & 1:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                win32api.keybd_event(key, 0, 0, 0)
                time.sleep(0.02)
                win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
                if modifiers & 1:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(delay)

def paste_text(text):
    """使用剪贴板粘贴文本"""
    import win32clipboard
    
    # 保存当前剪贴板内容
    try:
        win32clipboard.OpenClipboard()
        old_data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
    except:
        old_data = None
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
            win32clipboard.SetClipboardText(old_data, win32clipboard.CF_TEXT)
        except:
            pass
        finally:
            win32clipboard.CloseClipboard()

def main():
    print("=" * 60)
    print("京麦商品发布自动化 v2.0 - 填写商品信息")
    print("=" * 60)
    
    # 1. 找到京麦窗口
    print("\n[Step 1] 查找京麦窗口...")
    hwnd = find_jingmai_window()
    if not hwnd:
        print("[ERROR] 未找到京麦窗口!")
        return False
    
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    print(f"[OK] 找到京麦窗口: {hwnd}")
    
    # 2. 选择分类 - 点击"工业品"
    print("\n[Step 2] 选择商品分类...")
    # 根据截图，工业品在左侧列表第一个
    # 窗口内坐标: X≈100, Y≈200
    click_in_window(hwnd, 150, 250, delay=1.0)
    print("[OK] 已选择'工业品'分类")
    
    # 3. 点击"下一步"按钮
    print("\n[Step 3] 点击'下一步'按钮...")
    # 下一步按钮在页面底部中央
    # 窗口内坐标: X≈640, Y≈750
    click_in_window(hwnd, 640, 750)
    print("[OK] 点击'下一步'")
    
    # 4. 等待页面加载
    print("\n[Step 4] 等待商品信息页面加载...")
    time.sleep(3)
    
    # 5. 截图确认
    print("\n[Step 5] 截图确认商品信息页面...")
    screenshot_path = screenshot_window(hwnd, os.path.join(tempfile.gettempdir(), "jingmai_product_info.png"))
    print(f"[OK] 截图: {screenshot_path}")
    
    # 6. 填写商品名称
    print("\n[Step 6] 填写商品名称...")
    # 商品名称输入框 - 需要根据实际页面定位
    # 先截图查看实际页面布局
    time.sleep(1)
    
    print("\n" + "=" * 60)
    print("第一阶段完成！")
    print("请检查截图确认是否进入商品信息填写页面")
    print("=" * 60)
    
    # 复制截图到workspace
    import shutil
    dst = r"E:\workspace\jingmai_product_info.png"
    shutil.copy(screenshot_path, dst)
    print(f"\n截图已保存: {dst}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
