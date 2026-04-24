# -*- coding: utf-8 -*-
"""
在类目列表中选择"工业品"一级类目
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Selecting '工业品' in category list...")

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
    
    # 打印y=300-500范围内的所有元素（类目区域）
    print("Elements in category area...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            ctype = elem.element_info.control_type
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            
            # 类目区域：y在300-500范围
            if 300 < rect.top < 500 and name and len(name.strip()) > 1:
                if ctype in ["Hyperlink", "Button", "Text", "Custom"]:
                    print(f"  {ctype}: '{name.strip()}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击"工业品" - 在y=317, x=533附近
    print("\nClicking '工业品' at (533, 317)...")
    pyautogui.click(533, 317)
    time.sleep(2)
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
