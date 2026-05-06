# -*- coding: utf-8 -*-
"""
找到正确的输入框并输入"中低压配电"
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Finding correct input box and input '中低压配电'...")

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
    
    # 列出所有Edit元素
    edits = jingmai.descendants(control_type="Edit")
    print(f"Found {len(edits)} Edit elements:")
    
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            print(f"[{i}] '{name}' at ({rect.left}, {rect.top}) size {rect.width()}x{rect.height()}")
        except:
            pass
    
    # 尝试每个Edit
    search_term = "中低压配电"
    print(f"\nTrying to input '{search_term}' in each Edit...")
    
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            print(f"\nTrying Edit[{i}] at ({rect.left}, {rect.top})...")
            
            # 点击激活
            pyautogui.click(rect.left + rect.width()//2, rect.top + rect.height()//2)
            time.sleep(0.5)
            
            # 清除
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)
            
            # 输入
            pyautogui.typewrite(search_term, interval=0.1)
            time.sleep(0.5)
            
            # 按回车
            pyautogui.press('enter')
            time.sleep(2)
            
            print(f"  Input sent!")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nDone!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
