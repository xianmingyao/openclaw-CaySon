# -*- coding: utf-8 -*-
"""
点击京麦按钮[2] (2137, 18)
"""
import platform

if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Clicking button at (2137, 18)...")

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
                    print(f"  Found: {rect.width()}x{rect.height()}")
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
    
    # 3. 获取按钮[2]
    print("\n3. Getting button[2] at (2137, 18)...")
    buttons = jingmai.descendants(control_type="Button")
    btn = buttons[2]
    rect = btn.rectangle()
    print(f"  Button rect: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
    
    # 4. 点击按钮
    print("\n4. Clicking button[2]...")
    try:
        btn.click()
        print("  pywinauto click() called")
        time.sleep(3)
    except Exception as e:
        print(f"  Error with click(): {e}")
        
        # 备选：使用pyautogui
        print("\n5. Trying pyautogui click...")
        pyautogui.click(rect.left, rect.top)
        time.sleep(3)
    
    print("\nDone!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
