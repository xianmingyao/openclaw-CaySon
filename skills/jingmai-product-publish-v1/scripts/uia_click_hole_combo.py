# -*- coding: utf-8 -*-
# 点击孔型配置下拉框
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
    
    # ComboBox[7] at (644, 1026) = 孔型配置
    print("Clicking ComboBox[7] at (644, 1026)...")
    pyautogui.click(644, 1026)
    time.sleep(1.5)
    
    # 查找下拉选项
    print("Looking for options...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 选项通常在y=1026-1200范围
            if 1026 <= rect.top <= 1200:
                if name and len(name) > 1:
                    ctype = elem.element_info.control_type
                    print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
