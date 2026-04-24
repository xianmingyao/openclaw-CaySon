# -*- coding: utf-8 -*-
# 展开极数下拉框并分析选项
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
    
    # 向上滚动
    for i in range(3):
        pyautogui.scroll(2, x=1280, y=700)
        time.sleep(0.2)
    
    # 点击极数下拉框
    print("Clicking 极数 at (1036, 641)...")
    pyautogui.click(1036, 641)
    time.sleep(2)
    
    # 分析所有可见元素
    all_elements = jingmai.descendants()
    
    print("\n=== All elements in y=640-760 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            ctype = elem.element_info.control_type
            if 640 <= rect.top <= 760 and name and len(name.strip()) > 0:
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
