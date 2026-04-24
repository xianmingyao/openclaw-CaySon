# -*- coding: utf-8 -*-
"""
输入"插座"后按回车触发搜索
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Inputting '插座' and pressing Enter...")

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
    
    # 找顶部搜索框
    print("Finding search box...")
    edits = jingmai.descendants(control_type="Edit")
    
    search_edit = None
    for edit in edits:
        rect = edit.rectangle()
        if rect.width() > 1700:
            search_edit = edit
            break
    
    if search_edit:
        # 输入"插座"
        print("Inputting '插座'...")
        try:
            search_edit.set_edit_text("插座")
        except Exception as e:
            print(f"Error: {e}")
            # 点击后用pyautogui输入
            rect = search_edit.rectangle()
            pyautogui.click(rect.left + 100, rect.top + 10)
            time.sleep(0.5)
            pyautogui.typewrite("插座", interval=0.1)
        
        time.sleep(1)
        
        # 按回车
        print("Pressing Enter...")
        pyautogui.press("enter")
        time.sleep(2)
        
        print("Done!")
    else:
        print("Search box not found")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
