"""
京麦商品发布 - CEF 自动化
京麦使用 CEF (Chromium Embedded Framework)，需要用 Chrome DevTools Protocol
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
    print("京麦商品发布 - CEF/Chrome 自动化")
    print("=" * 60)
    
    # 1. 连接到京麦的 CEF 窗口
    print("\n[Step 1] 连接到京麦 CEF 窗口...")
    try:
        app = Application(backend="win32").connect(title="jd_465d1abd3ee76", timeout=5)
        window = app.window(title="jd_465d1abd3ee76")
        print(f"[OK] 连接到窗口")
        
        # 列出所有子窗口
        children = window.children()
        print(f"[OK] 找到 {len(children)} 个子控件")
        
        # 查找 CefBrowserWindow
        cef_window = None
        for child in children:
            try:
                class_name = child.class_name()
                if 'Cef' in class_name or 'Chrome' in class_name:
                    print(f"[INFO] Found CEF/Chrome control: {class_name}")
                    cef_window = child
                    break
            except:
                pass
        
    except Exception as e:
        print(f"[ERROR] 连接失败: {e}")
        return False
    
    # 2. 使用 CDP (Chrome DevTools Protocol) 直接操作
    print("\n[Step 2] 使用 CDP 操作页面...")
    
    # 京麦的 CEF 窗口可以通过 CDP 连接
    # 通常京麦在本地运行一个 CDP 端口
    import subprocess
    import json
    
    # 尝试连接到京麦的 CDP 端口
    # 京麦通常使用端口 9222 或类似端口
    cdp_ports = [9222, 9223, 9333, 9433]
    
    for port in cdp_ports:
        try:
            # 获取 CDP 端点
            result = subprocess.run(
                ['curl', '-s', f'http://localhost:{port}/json'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                print(f"[OK] Found CDP at port {port}")
                try:
                    tabs = json.loads(result.stdout)
                    if tabs:
                        print(f"[INFO] Found {len(tabs)} browser tab(s)")
                        for tab in tabs:
                            print(f"  - {tab.get('title', 'Unknown')}: {tab.get('url', 'Unknown')}")
                        break
                except:
                    pass
        except:
            pass
    
    # 3. 直接使用 JavaScript 执行点击
    # 通过 pywinauto 的 CEF 控件执行 JavaScript
    print("\n[Step 3] 尝试在页面中执行 JavaScript...")
    
    # 查找 Chrome_WidgetWin 控件
    try:
        chrome_widget = window.child_window(class_name="Chrome_WidgetWin_0")
        if chrome_widget.exists():
            print("[INFO] Found Chrome_WidgetWin_0")
            
            # 尝试获取焦点并发送键盘事件
            chrome_widget.set_focus()
            time.sleep(0.5)
            
            # 发送 End 键跳到页面底部（按钮位置）
            from pywinauto import keyboard
            keyboard.send_keys('{END}')
            time.sleep(0.5)
            
            # 发送几次 Tab 确保在按钮上
            for i in range(5):
                keyboard.send_keys('{TAB}')
                time.sleep(0.2)
            
            # 发送空格或回车
            keyboard.send_keys(' ')
            time.sleep(0.5)
            keyboard.send_keys('{ENTER}')
            
            print("[OK] 发送了键盘事件")
    except Exception as e:
        print(f"[WARN] Chrome_WidgetWin 操作失败: {e}")
    
    # 4. 截图确认
    print("\n[Step 4] 截图确认...")
    
    try:
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
        
        path = os.path.join(tempfile.gettempdir(), "jingmai_cef.png")
        bitmap.SaveBitmapFile(savedc, path)
        
        win32gui.DeleteObject(bitmap.GetHandle())
        savedc.DeleteDC()
        mfcdc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwindc)
        
        dst = r"E:\workspace\jingmai_cef.png"
        shutil.copy(path, dst)
        print(f"[OK] 截图保存: {dst}")
    except Exception as e:
        print(f"[ERROR] 截图失败: {e}")
    
    print("\n" + "=" * 60)
    print("CEF 自动化流程执行完成")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
