# -*- coding: utf-8 -*-
# 点击"近期使用类目"中的"工业品>中低压配电>插座"
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
    
    # 搜索所有包含"工业品"的元素
    print("Looking for '工业品' text...")
    all_elements = jingmai.descendants()
    
    targets = []
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            if "工业品" in name and ">" in name:
                rect = elem.rectangle()
                ctype = elem.element_info.control_type
                print(f"  Found: {ctype} '{name}' at ({rect.left}, {rect.top})")
                targets.append((elem, name, rect))
        except:
            pass
    
    # 点击第一个
    if targets:
        elem, name, rect = targets[0]
        print(f"Clicking at ({rect.left}, {rect.top})...")
        try:
            elem.invoke()
        except:
            pyautogui.click(rect.left + 50, rect.top + 5)
        time.sleep(2)
        print("Done!")
    else:
        print("Target not found")

except Exception as e:
    print(f"Error: {e}")
