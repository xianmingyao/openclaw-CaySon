# -*- coding: utf-8 -*-
"""
使用UIA直接操作搜索框
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Using UIA to operate search box...")

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
    time.sleep(0.5)
    
    # 找所有Edit元素
    print("Finding all Edit elements...")
    edits = jingmai.descendants(control_type="Edit")
    
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            print(f"[{i}] '{name}' at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
            
            # 点击这个Edit
            print(f"  Clicking...")
            try:
                edit.invoke()
            except:
                try:
                    edit.click_input()
                except:
                    pyautogui.click(rect.left + 5, rect.top + 5)
            
            time.sleep(1)
            
            # 输入测试文字
            print(f"  Typing test...")
            pyautogui.typewrite("test", interval=0.1)
            time.sleep(1)
            
            # 截图看看
            print(f"  Checking...")
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
