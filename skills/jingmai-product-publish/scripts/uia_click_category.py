# -*- coding: utf-8 -*-
"""
点击"工业品"开始选择正确类目
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Clicking '工业品' category...")

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
    
    # 查找所有Text元素找"工业品"
    print("Looking for '工业品' text...")
    texts = jingmai.descendants(control_type="Text")
    
    gongyepin = None
    for txt in texts:
        try:
            name = txt.element_info.name or ""
            if "工业品" in name and ">" not in name:
                rect = txt.rectangle()
                print(f"Found '工业品' at ({rect.left}, {rect.top})")
                gongyepin = txt
                break
        except:
            pass
    
    if gongyepin:
        print("Clicking '工业品'...")
        try:
            gongyepin.invoke()
        except:
            try:
                gongyepin.click_input()
            except:
                rect = gongyepin.rectangle()
                pyautogui.click(rect.left + 50, rect.top + 5)
        time.sleep(2)
        print("Clicked!")
    else:
        print("'工业品' not found")
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
