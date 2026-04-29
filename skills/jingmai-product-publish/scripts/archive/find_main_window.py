# -*- coding: utf-8 -*-
"""
查找京麦主窗口
"""
import platform

if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Finding Jingmai main window with correct backend...")

try:
    from pywinauto import Desktop
    import time
    
    # 1. 使用win32后端找2560x1392的窗口
    print("\n1. Looking for 2560x1392 windows with win32 backend...")
    desktop = Desktop(backend="win32")
    all_windows = desktop.windows()
    
    big_windows = []
    for w in all_windows:
        try:
            rect = w.rectangle()
            if rect.width() == 2560 and rect.height() == 1392:
                title = w.window_text()
                class_name = w.element_info.class_name
                big_windows.append(w)
                print(f"  2560x1392: {title[:50]} - Class: {class_name}")
        except:
            pass
    
    print(f"\n2. Found {len(big_windows)} windows with size 2560x1392")
    
    # 3. 尝试UIA后端找京麦
    print("\n3. Trying UIA backend for Jingmai...")
    desktop_uia = Desktop(backend="uia")
    uia_windows = desktop_uia.windows()
    
    # 找包含"商品"或"发布"的窗口
    for w in uia_windows:
        try:
            title = w.window_text()
            if title and ("商品" in title or "发布" in title or "工业品" in title):
                print(f"  Found: {title[:50]}")
                rect = w.rectangle()
                print(f"    Size: {rect.width()}x{rect.height()}")
        except:
            pass
    
    # 4. 列出所有顶层UIA窗口
    print("\n4. Top-level UIA windows...")
    for w in uia_windows[:30]:
        try:
            title = w.window_text()
            if title:
                rect = w.rectangle()
                print(f"  {title[:40]} - {rect.width()}x{rect.height()}")
        except:
            pass
    
    # 5. 尝试直接连接到京麦
    print("\n5. Trying direct connection...")
    try:
        from pywinauto.application import Application
        
        # 尝试连接jd_465d1abd3ee76进程
        # 先用win32枚举进程找jd进程
        import psutil
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'jd' in proc.info['name'].lower() or 'jingmai' in proc.info['name'].lower():
                    print(f"  Process: {proc.info['name']} (PID: {proc.info['pid']})")
            except:
                pass
    except Exception as e:
        print(f"  Error: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")
