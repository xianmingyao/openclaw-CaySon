# -*- coding: utf-8 -*-
"""
测试Edit[0]输入+回车
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Testing Edit[0] input + Enter...")

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
    
    # 获取Edit[0]
    edits = jingmai.descendants(control_type="Edit")
    search_edit = edits[0]
    rect = search_edit.rectangle()
    print(f"Edit[0] at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
    
    # 1. 点击激活
    print("Clicking to activate...")
    pyautogui.click(rect.left + 100, rect.top + 10)
    time.sleep(0.5)
    
    # 2. 全选清除
    print("Clearing...")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    
    # 3. set_edit_text输入
    print("Inputting '插座' via set_edit_text...")
    search_edit.set_edit_text("插座")
    time.sleep(1)
    
    # 4. 按Enter
    print("Pressing Enter...")
    pyautogui.press("enter")
    time.sleep(3)
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
