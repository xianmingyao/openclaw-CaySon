# -*- coding: utf-8 -*-
"""
使用UIA直接操作京麦主窗口
"""
import platform

if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Using UIA to directly control Jingmai main window...")

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    
    # 1. 获取UIA后端的京麦窗口
    print("\n1. Getting UIA Jingmai window...")
    desktop = Desktop(backend="uia")
    all_windows = desktop.windows()
    
    jingmai = None
    for w in all_windows:
        try:
            title = w.window_text()
            if title == "jd_465d1abd3ee76":
                rect = w.rectangle()
                if rect.width() == 2560 and rect.height() == 1392:
                    jingmai = w
                    print(f"  Found main window: {rect.width()}x{rect.height()}")
                    break
        except:
            pass
    
    if not jingmai:
        print("  Main window not found!")
        exit(1)
    
    # 2. 激活窗口
    print("\n2. Activating window...")
    jingmai.set_focus()
    time.sleep(1)
    
    # 3. 查找Button
    print("\n3. Finding Button elements...")
    try:
        buttons = jingmai.descendants(control_type="Button")
        print(f"  Found {len(buttons)} buttons")
        
        # 打印所有按钮
        for i, btn in enumerate(buttons[:30]):
            try:
                name = btn.element_info.name or ""
                rect = btn.rectangle()
                enabled = btn.is_enabled()
                visible = btn.is_visible()
                print(f"  [{i}] '{name[:30]}' at ({rect.left}, {rect.top}) E:{enabled} V:{visible}")
            except Exception as e:
                print(f"  [{i}] Error: {e}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # 4. 查找X按钮
    print("\n4. Looking for X button...")
    x_candidates = []
    try:
        for btn in buttons:
            try:
                name = btn.element_info.name or ""
                if name in ["X", "×", "✕", "close", "Close"]:
                    rect = btn.rectangle()
                    x_candidates.append((btn, name, rect))
                    print(f"  Found X candidate: '{name}' at ({rect.left}, {rect.top})")
            except:
                pass
    except Exception as e:
        print(f"  Error: {e}")
    
    # 5. 尝试点击X按钮
    if x_candidates:
        print("\n5. Clicking X button...")
        btn, name, rect = x_candidates[0]
        try:
            # 方法1: 使用pywinauto的click
            print(f"  Trying pywinauto click on ({rect.left}, {rect.top})...")
            btn.click()
            time.sleep(2)
            print("  Clicked!")
            
            # 检查是否关闭
            jingmai2 = None
            for w in all_windows:
                try:
                    title = w.window_text()
                    if title == "jd_465d1abd3ee76":
                        rect2 = w.rectangle()
                        if rect2.width() == 2560 and rect2.height() == 1392:
                            jingmai2 = w
                            break
                except:
                    pass
            
            if jingmai2:
                print("  Window still exists")
            else:
                print("  Window closed!")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("  No X button found")
    
    # 6. 尝试用pyautogui点击（基于坐标）
    print("\n6. Trying pyautogui click...")
    # 使用之前学到的坐标
    # 识别坐标(1266, 105) -> 真实坐标(2532, 183)
    # 但这是基于窗口坐标系的，需要转换
    rect = jingmai.rectangle()
    print(f"  Window rect: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
    
    # 如果窗口不在(0,0)，需要调整
    # 实际点击位置 = 窗口左上角 + 相对位置
    click_x = rect.left + 2532
    click_y = rect.top + 183
    print(f"  Clicking at absolute ({click_x}, {click_y})")
    
    pyautogui.click(click_x, click_y)
    time.sleep(2)
    print("  Clicked!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")
