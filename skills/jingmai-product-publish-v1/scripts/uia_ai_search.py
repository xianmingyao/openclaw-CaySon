# -*- coding: utf-8 -*-
"""
在AI搜索框输入完整路径并搜索
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("AI searching for '工业品 中低压配电 插座'...")

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
    
    # 找AI搜索框 (Edit at 269, 58)
    print("Finding AI search Edit...")
    edits = jingmai.descendants(control_type="Edit")
    
    ai_search = None
    for edit in edits:
        rect = edit.rectangle()
        if rect.width() > 1700:
            ai_search = edit
            print(f"Found AI search box at ({rect.left}, {rect.top})")
            break
    
    if ai_search:
        # 清除并输入新内容
        print("Clearing and inputting new search...")
        try:
            # 全选
            ai_search.set_edit_text("")
            time.sleep(0.5)
            
            # 输入搜索词
            ai_search.set_edit_text("工业品 中低压配电 插座")
            print("Input success!")
        except Exception as e:
            print(f"Error: {e}")
            # 备选：用pyautogui
            rect = ai_search.rectangle()
            pyautogui.click(rect.left + 100, rect.top + 10)
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('delete')
            time.sleep(0.3)
            pyautogui.typewrite("工业品 中低压配电 插座", interval=0.1)
        
        time.sleep(2)
        
        # 按回车触发搜索
        print("Pressing Enter...")
        pyautogui.press("enter")
        time.sleep(3)
        
        print("Done!")
    else:
        print("AI search box not found")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
