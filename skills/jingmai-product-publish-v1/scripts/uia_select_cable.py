# -*- coding: utf-8 -*-
# 选择电缆长度
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    
    desktop = Desktop(backend="uia")
    
    jingmai = None
    for w in desktop.windows():
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
        print("Window not found!")
        exit(1)
    
    print("Found window")
    jingmai.set_focus()
    time.sleep(0.5)
    
    # 点击"电缆长度"的"请选择" - (1428, 883)
    print("Clicking 电缆长度 at (1428, 883)...")
    pyautogui.click(1428, 883)
    time.sleep(1.5)
    
    # 查找电缆长度选项
    print("Looking for cable length options...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if rect.top > 800 and ("米" in name or "cm" in name.lower() or "m" in name.lower() or "长度" in name):
                if len(name) < 15:
                    print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 也打印y=850-1100的选项
    print("\nOptions in y=850-1100:")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 900 <= rect.top <= 1100 and len(name) > 1 and len(name) < 15:
                ctype = elem.element_info.control_type
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
