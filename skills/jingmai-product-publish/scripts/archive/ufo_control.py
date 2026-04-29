# -*- coding: utf-8 -*-
"""
使用UFO/pywinauto方法控制京麦
"""
import platform

if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Testing pywinauto to control Jingmai...")

try:
    from pywinauto import Desktop
    from pywinauto.controls.uiawrapper import UIAWrapper
    import pyautogui
    import time
    
    print("Imports successful!")
    
    # 1. 获取所有窗口
    print("\n1. Getting all windows...")
    desktop = Desktop(backend="win32")
    all_windows = desktop.windows()
    print(f"Found {len(all_windows)} windows")
    
    # 2. 找京麦窗口
    jingmai_windows = [w for w in all_windows if "jd" in w.window_text().lower() or "jdfw" in w.window_text().lower()]
    print(f"\n2. Found {len(jingmai_windows)} Jingmai-related windows")
    
    for i, w in enumerate(jingmai_windows):
        print(f"  [{i}] {w.window_text()[:50]}")
        print(f"      Class: {w.element_info.class_name}")
    
    # 3. 尝试找京麦主窗口
    if jingmai_windows:
        window = jingmai_windows[0]
        print(f"\n3. Using window: {window.window_text()[:50]}")
        
        # 4. 激活窗口
        window.set_focus()
        time.sleep(0.5)
        
        # 5. 获取窗口信息
        rect = window.rectangle()
        print(f"\n4. Window rect:")
        print(f"   Left: {rect.left}, Top: {rect.top}")
        print(f"   Right: {rect.right}, Bottom: {rect.bottom}")
        print(f"   Width: {rect.right - rect.left}, Height: {rect.bottom - rect.top}")
        
        # 6. 尝试获取UI树
        print(f"\n5. Getting UI tree...")
        try:
            children = window.children()
            print(f"   Found {len(children)} direct children")
            for j, child in enumerate(children[:10]):
                try:
                    name = child.element_info.name or ""
                    ctype = child.element_info.control_type or ""
                    print(f"   [{j}] {ctype}: {name[:30]}")
                except:
                    pass
        except Exception as e:
            print(f"   Error getting UI tree: {e}")
        
        # 7. 尝试查找Button类型的元素（X按钮通常是Button）
        print(f"\n6. Looking for Button elements...")
        try:
            buttons = window.children(class_name="Button")
            print(f"   Found {len(buttons)} Button elements")
            for btn in buttons[:5]:
                print(f"   - {btn.window_text()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # 8. 尝试用UIA后端
        print(f"\n7. Trying UIA backend...")
        try:
            desktop_uia = Desktop(backend="uia")
            uia_windows = desktop_uia.windows()
            print(f"   Found {len(uia_windows)} windows with UIA")
            
            # 找京麦窗口
            for w in uia_windows:
                if "jd" in w.window_text().lower() or "jdfw" in w.window_text().lower() or "wares" in w.window_text().lower():
                    print(f"   UIA Window: {w.window_text()[:50]}")
                    print(f"   Control Type: {w.element_info.control_type}")
                    
                    # 查找子元素
                    try:
                        for child in w.children()[:5]:
                            print(f"     Child: {child.element_info.control_type} - {child.element_info.name[:30]}")
                    except:
                        pass
                    break
        except Exception as e:
            print(f"   Error: {e}")
        
    else:
        print("No Jingmai windows found")
        
        # 列出所有窗口
        print("\nAll visible windows:")
        for i, w in enumerate(all_windows[:20]):
            print(f"  [{i}] {w.window_text()[:50]} - {w.element_info.class_name}")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Install with: pip install pywinauto pyautogui")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")
