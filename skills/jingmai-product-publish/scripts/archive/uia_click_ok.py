# -*- coding: utf-8 -*-
"""
点击确认弹窗的"确定"按钮
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Clicking '确定' button...")

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    
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
                    break
        except:
            pass
    
    if not jingmai:
        print("Main window not found!")
        exit(1)
    
    print("Found main window")
    jingmai.set_focus()
    time.sleep(1)
    
    # Find all Button elements
    print("Finding all buttons...")
    buttons = jingmai.descendants(control_type="Button")
    print(f"Found {len(buttons)} buttons")
    
    # Find "确定" button
    ok_btn = None
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            rect = btn.rectangle()
            print(f"  Button: '{name}' at ({rect.left}, {rect.top})")
            if "确定" in name:
                ok_btn = btn
                print(f"  -> Found '确定' button!")
        except:
            pass
    
    if ok_btn:
        print("Clicking '确定'...")
        try:
            ok_btn.invoke()
            print("invoke() called!")
        except Exception as e:
            print(f"Error: {e}")
            try:
                ok_btn.click_input()
                print("click_input() called!")
            except Exception as e2:
                print(f"Error2: {e2}")
                # Fallback to pyautogui
                rect = ok_btn.rectangle()
                pyautogui.click(rect.left, rect.top)
                print("pyautogui fallback!")
        time.sleep(3)
    else:
        print("'确定' not found")
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
