# -*- coding: utf-8 -*-
"""
在搜索框输入"插座"并选择正确类目
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Inputting '插座' in search box...")

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
    
    # 找Edit元素（搜索框）
    print("Finding search Edit box...")
    edits = jingmai.descendants(control_type="Edit")
    print(f"Found {len(edits)} Edit elements")
    
    search_box = None
    for edit in edits:
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            print(f"  Edit: '{name}' at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
            # 搜索框通常比较大
            if rect.width() > 300:
                search_box = edit
                print(f"  -> Search box candidate!")
        except:
            pass
    
    if search_box:
        print("Clicking search box...")
        try:
            search_box.invoke()
        except:
            search_box.click_input()
        time.sleep(1)
        
        print("Typing '插座'...")
        pyautogui.typewrite("插座", interval=0.1)
        time.sleep(2)
        
        print("Done typing!")
    else:
        print("Search box not found, trying coordinates...")
        # 搜索框大致位置 (500, 300)左右
        pyautogui.click(500, 300)
        time.sleep(0.5)
        pyautogui.typewrite("插座", interval=0.1)
        time.sleep(2)
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
