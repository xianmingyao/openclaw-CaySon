# -*- coding: utf-8 -*-
"""
使用UFO/pywinauto方法查找京麦主窗口
"""
import platform

if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Finding Jingmai main window...")

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    
    # 1. 获取所有窗口
    print("\n1. Getting all windows...")
    desktop = Desktop(backend="win32")
    all_windows = desktop.windows()
    print(f"Found {len(all_windows)} windows")
    
    # 2. 找京麦相关窗口
    print("\n2. Finding Jingmai windows...")
    jingmai_windows = []
    for w in all_windows:
        try:
            title = w.window_text()
            class_name = w.element_info.class_name
            if title and ("jd" in title.lower() or "jdfw" in title.lower() or "wares" in title.lower()):
                rect = w.rectangle()
                print(f"  {title[:50]}")
                print(f"    Class: {class_name}")
                print(f"    Rect: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom}), Size: {rect.width()}x{rect.height()}")
                jingmai_windows.append(w)
        except:
            pass
    
    # 3. 找最大窗口（可能是主窗口）
    print("\n3. Finding largest window (possible main window)...")
    max_area = 0
    main_window = None
    for w in all_windows:
        try:
            rect = w.rectangle()
            area = rect.width() * rect.height()
            if area > max_area and rect.width() > 1000 and rect.height() > 700:
                max_area = area
                main_window = w
        except:
            pass
    
    if main_window:
        print(f"  Largest window: {main_window.window_text()[:50]}")
        rect = main_window.rectangle()
        print(f"  Size: {rect.width()}x{rect.height()}")
        print(f"  Rect: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
    
    # 4. 尝试找2560x1392的窗口
    print("\n4. Finding 2560x1392 window...")
    for w in all_windows:
        try:
            rect = w.rectangle()
            if rect.width() == 2560 and rect.height() == 1392:
                print(f"  Found 2560x1392 window: {w.window_text()[:50]}")
                print(f"    Class: {w.element_info.class_name}")
        except:
            pass
    
    # 5. 使用UIA后端查找
    print("\n5. Using UIA backend to find windows...")
    desktop_uia = Desktop(backend="uia")
    uia_windows = desktop_uia.windows()
    
    # 找最大的UIA窗口
    max_uia_window = None
    max_uia_area = 0
    for w in uia_windows:
        try:
            rect = w.rectangle()
            area = rect.width() * rect.height()
            if area > max_uia_area:
                max_uia_area = area
                max_uia_window = w
        except:
            pass
    
    if max_uia_window:
        print(f"  Largest UIA window: {max_uia_window.window_text()[:50] if max_uia_window.window_text() else '(no title)'}")
        rect = max_uia_window.rectangle()
        print(f"  Size: {rect.width()}x{rect.height()}")
        print(f"  Control Type: {max_uia_window.element_info.control_type}")
        
        # 尝试获取子元素
        try:
            children = max_uia_window.children()
            print(f"  Direct children: {len(children)}")
            for i, child in enumerate(children[:10]):
                try:
                    print(f"    [{i}] {child.element_info.control_type}: {child.element_info.name[:30] if child.element_info.name else '(no name)'}")
                except:
                    pass
        except Exception as e:
            print(f"  Error getting children: {e}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")
