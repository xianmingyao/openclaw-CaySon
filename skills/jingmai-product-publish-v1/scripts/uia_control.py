# -*- coding: utf-8 -*-
"""
使用UIA后端控制京麦
"""
import platform

if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Using UIA backend to control Jingmai...")

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    
    # 1. 使用UIA后端获取窗口
    print("\n1. Getting windows with UIA backend...")
    desktop = Desktop(backend="uia")
    all_windows = desktop.windows()
    
    # 2. 找京麦窗口
    jingmai = None
    for w in all_windows:
        try:
            title = w.window_text()
            if "jd_465d1abd3ee76" in title or "wares-jdm" in title.lower():
                jingmai = w
                print(f"  Found: {title}")
                break
        except:
            pass
    
    if not jingmai:
        # 尝试通过class_name找
        for w in all_windows:
            try:
                if "wares" in w.window_text().lower():
                    jingmai = w
                    print(f"  Found by class: {w.window_text()}")
                    break
            except:
                pass
    
    if not jingmai:
        print("  Jingmai window not found!")
        print("  Available windows with 'jd':")
        for w in all_windows:
            try:
                if "jd" in w.window_text().lower():
                    print(f"    {w.window_text()[:50]}")
            except:
                pass
        exit(1)
    
    # 3. 获取窗口信息
    rect = jingmai.rectangle()
    print(f"\n2. Window info:")
    print(f"   Title: {jingmai.window_text()[:50]}")
    print(f"   Rect: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
    print(f"   Size: {rect.width()}x{rect.height()}")
    print(f"   Control Type: {jingmai.element_info.control_type}")
    
    # 4. 激活窗口
    print(f"\n3. Activating window...")
    jingmai.set_focus()
    time.sleep(0.5)
    
    # 5. 遍历UI树（深度优先）
    print(f"\n4. Building UI tree...")
    
    def print_tree(element, level=0, max_level=5):
        if level > max_level:
            return
        try:
            name = element.element_info.name or ""
            ctype = element.element_info.control_type or ""
            rect = element.rectangle()
            
            indent = "  " * level
            if name:
                print(f"{indent}{ctype}: {name[:40]}")
            else:
                print(f"{indent}{ctype}")
            
            # 递归打印子元素
            try:
                for child in element.children():
                    print_tree(child, level + 1, max_level)
            except:
                pass
        except Exception as e:
            pass
    
    try:
        children = jingmai.children()
        print(f"   Found {len(children)} direct children")
        for i, child in enumerate(children[:20]):
            try:
                name = child.element_info.name or ""
                ctype = child.element_info.control_type or ""
                rect = child.rectangle()
                print(f"   [{i}] {ctype}: {name[:40] if name else '(no name)'}")
                print(f"       Rect: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
            except Exception as e:
                print(f"   [{i}] Error: {e}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 6. 尝试查找Button
    print(f"\n5. Looking for Button elements...")
    try:
        buttons = jingmai.descendants(control_type="Button")
        print(f"   Found {len(buttons)} Button elements")
        for i, btn in enumerate(buttons[:20]):
            try:
                name = btn.element_info.name or ""
                rect = btn.rectangle()
                print(f"   [{i}] '{name[:30]}' at ({rect.left}, {rect.top})")
            except:
                pass
    except Exception as e:
        print(f"   Error: {e}")
    
    # 7. 尝试查找X按钮
    print(f"\n6. Looking for X close button...")
    try:
        # 尝试各种可能的X按钮名称
        for title in ["X", "Close", "关闭", "×"]:
            try:
                x_btn = jingmai.child_window(title=title, control_type="Button")
                if x_btn.exists():
                    rect = x_btn.rectangle()
                    print(f"   Found '{title}' button at ({rect.left}, {rect.top})")
                    # 点击
                    x_btn.click()
                    print(f"   Clicked '{title}' button!")
                    time.sleep(1)
                    break
            except Exception as e:
                pass
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\nDone!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
