# -*- coding: utf-8 -*-
# 选择230V额定电压
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
    
    # 查找230V选项
    print("Looking for 230V...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "230V" in name or "230v" in name.lower():
                print(f"Found: '{name}' at ({rect.left}, {rect.top})")
                try:
                    elem.invoke()
                except:
                    pyautogui.click(rect.left + 50, rect.top + 5)
                time.sleep(1)
                print("Selected!")
                break
        except:
            pass

except Exception as e:
    print(f"Error: {e}")
