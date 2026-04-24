# -*- coding: utf-8 -*-
"""
解决UIA set_edit_text输入后按回车触发搜索
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Testing set_edit_text + Enter search...")

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
    
    # 找搜索Edit框
    print("Finding search Edit...")
    edits = jingmai.descendants(control_type="Edit")
    
    search_edit = None
    for edit in edits:
        rect = edit.rectangle()
        if rect.width() > 1700:  # 顶部大搜索框
            search_edit = edit
            print(f"Found search Edit at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
            break
    
    if search_edit:
        # 1. set_edit_text输入
        print("Inputting '插座' via set_edit_text...")
        search_edit.set_edit_text("插座")
        time.sleep(1)
        
        # 2. 按Enter触发搜索
        print("Pressing Enter...")
        pyautogui.press("enter")
        time.sleep(3)
        
        print("Done!")
    else:
        print("Search Edit not found")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
