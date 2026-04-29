# -*- coding: utf-8 -*-
# 选择额定电压
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
    
    # 按Esc关闭当前下拉框
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 点击"额定电压"的"请选择" - (1036, 883)
    print("Clicking 额定电压 at (1036, 883)...")
    pyautogui.click(1036, 883)
    time.sleep(1.5)
    
    # 查找电压选项
    print("Looking for voltage options...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if rect.top > 800 and ("230V" in name or "250V" in name or "电压" in name):
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 也打印y=800-1000范围的下拉选项
    print("\nAll dropdown options (y=800-1000):")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 850 <= rect.top <= 1000 and len(name) > 1 and len(name) < 15:
                print(f"  '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
