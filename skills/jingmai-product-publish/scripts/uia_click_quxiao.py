# -*- coding: utf-8 -*-
"""
点击"取消"按钮重新选择类目
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Clicking '取消' button...")

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
    
    # Find "取消" button
    print("Finding '取消' button...")
    buttons = jingmai.descendants(control_type="Button")
    
    quxiao_btn = None
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            if "取消" in name:
                rect = btn.rectangle()
                print(f"Found '取消' at ({rect.left}, {rect.top})")
                quxiao_btn = btn
                break
        except:
            pass
    
    if quxiao_btn:
        print("Clicking '取消'...")
        try:
            quxiao_btn.invoke()
            print("invoke() called!")
        except Exception as e:
            print(f"Error: {e}")
            try:
                quxiao_btn.click_input()
                print("click_input() called!")
            except Exception as e2:
                print(f"Error2: {e2}")
                rect = quxiao_btn.rectangle()
                pyautogui.click(rect.left, rect.top)
                print("pyautogui fallback!")
        time.sleep(3)
    else:
        print("'取消' not found")
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
