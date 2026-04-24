# -*- coding: utf-8 -*-
# 选择极数
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
    
    # 点击极数下拉框
    print("Clicking 极数 at (1036, 641)...")
    pyautogui.click(1036, 641)
    time.sleep(2)
    
    # 查找极数选项 - 极数通常是2、3、4等
    all_elements = jingmai.descendants()
    print("Looking for pole options...")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 选项应该在y=650-750范围
            if 650 <= rect.top <= 750:
                # 极数选项可能是纯数字
                if name.isdigit() and int(name) <= 12:
                    print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                    try:
                        elem.invoke()
                    except:
                        pyautogui.click(rect.left + 20, rect.top + 5)
                    time.sleep(1)
                    print(f"  Selected {name}!")
                    break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
