# -*- coding: utf-8 -*-
"""
使用UIA set_edit_text方法输入搜索框
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Using UIA set_edit_text to input search...")

try:
    from pywinauto import Desktop
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
    
    # 找顶部搜索框 (269, 58)
    print("Finding search Edit box...")
    edits = jingmai.descendants(control_type="Edit")
    
    search_edit = None
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            print(f"[{i}] '{name}' at ({rect.left}, {rect.top})")
            
            # 顶部大搜索框
            if rect.width() > 1700:
                search_edit = edit
                print(f"  -> Top search box found!")
        except:
            pass
    
    if search_edit:
        print("Setting focus and input text...")
        try:
            # 方法1: set_edit_text
            search_edit.set_edit_text("插座")
            print("set_edit_text success!")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(2)
    else:
        print("Search box not found")
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
