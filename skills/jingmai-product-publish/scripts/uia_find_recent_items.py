# -*- coding: utf-8 -*-
# 查找近期使用类目中的所有项并点击
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
    
    # 查找y=640-700范围内的所有文本（近期使用类目区域）
    print("Elements in recent category area (y=640-700):")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 640 <= rect.top <= 700 and name:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 尝试点击"工业品>中低压配电>插座"
    # 它可能在y=654附近，x在500-800之间
    print("\nTrying to find and click the recent category...")
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "工业品" in name and "中低压" in name:
                print(f"FOUND! '{name}' at ({rect.left}, {rect.top})")
                # 点击中间位置
                try:
                    elem.invoke()
                except:
                    pyautogui.click(rect.left + 100, rect.top + 5)
                time.sleep(2)
                print("Clicked!")
                break
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
