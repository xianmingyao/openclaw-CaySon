"""
京麦商品发布 - pywinauto 自动化
使用 pywinauto 直接操作 Qt 窗口
"""
import sys
import time
import os
import shutil
import tempfile
from pathlib import Path

from pywinauto import Application

def main():
    print("=" * 60)
    print("京麦商品发布 - pywinauto 自动化")
    print("=" * 60)
    
    # 1. 连接到京麦窗口
    print("\n[Step 1] 连接到京麦窗口...")
    try:
        app = Application(backend="win32").connect(title="jd_465d1abd3ee76", timeout=5)
        window = app.window(title="jd_465d1abd3ee76")
        print(f"[OK] 连接到窗口: {window}")
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        # 尝试使用 Qt 后端
        try:
            app = Application(backend="qt").connect(title="jd_465d1abd3ee76", timeout=5)
            window = app.window(title="jd_465d1abd3ee76")
            print(f"[OK] Qt 后端连接成功")
        except Exception as e2:
            print(f"[ERROR] Qt 后端也失败: {e2}")
            return False
    
    # 2. 激活窗口
    print("\n[Step 2] 激活窗口...")
    window.set_focus()
    time.sleep(0.5)
    print("[OK] 窗口已激活")
    
    # 3. 列出窗口中的控件
    print("\n[Step 3] 列出窗口控件...")
    try:
        children = window.children()
        print(f"[OK] 找到 {len(children)} 个子控件")
        for i, child in enumerate(children[:20]):  # 只显示前20个
            try:
                print(f"  [{i}] {child.class_name()} - {child.window_text()[:50] if child.window_text() else '(empty)'}")
            except:
                print(f"  [{i}] {child.class_name()}")
    except Exception as e:
        print(f"[WARN] 枚举控件失败: {e}")
    
    # 4. 尝试找到并点击"下一步"按钮
    print("\n[Step 4] 查找并点击'下一步'按钮...")
    
    # 方法1: 通过文本查找按钮
    try:
        # 尝试不同的按钮文本
        button_texts = [
            "下一步",
            "下一步，完善商品信息",
            "下一步，填写商品信息",
            "下一步，完善商品基本信息",
        ]
        
        for text in button_texts:
            try:
                # 使用窗口的 child_window 方法查找
                btn = window.child_window(title=text, class_name="Button")
                if btn.exists():
                    print(f"[INFO] 找到按钮: '{text}'")
                    btn.click()
                    print(f"[OK] 已点击按钮: '{text}'")
                    time.sleep(3)
                    break
            except Exception as e:
                print(f"[WARN] 查找按钮 '{text}' 失败: {e}")
    except Exception as e:
        print(f"[WARN] 方法1失败: {e}")
    
    # 方法2: 通过 class_name 查找所有按钮
    try:
        all_buttons = window.children(class_name="Button")
        print(f"[INFO] 找到 {len(all_buttons)} 个 Button 控件")
        for btn in all_buttons:
            try:
                text = btn.window_text()
                print(f"  Button: '{text}' at {btn.rectangle()}")
            except:
                pass
    except Exception as e:
        print(f"[WARN] 方法2失败: {e}")
    
    # 5. 截图确认
    print("\n[Step 5] 截图确认...")
    
    # 使用 pywinauto 截图
    try:
        # 获取窗口区域
        rect = window.rectangle()
        print(f"[INFO] 窗口区域: {rect}")
        
        # 保存截图
        dst = r"E:\workspace\jingmai_pywinauto.png"
        
        # 使用 win32api 截图
        import win32gui
        import win32con
        import win32ui
        
        hwnd = win32gui.FindWindow(None, "jd_465d1abd3ee76")
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
        
        path = os.path.join(tempfile.gettempdir(), "jingmai_pywinauto.png")
        bitmap.SaveBitmapFile(savedc, path)
        
        win32gui.DeleteObject(bitmap.GetHandle())
        savedc.DeleteDC()
        mfcdc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwindc)
        
        shutil.copy(path, dst)
        print(f"[OK] 截图保存: {dst}")
    except Exception as e:
        print(f"[ERROR] 截图失败: {e}")
    
    print("\n" + "=" * 60)
    print("请检查截图确认是否成功")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
