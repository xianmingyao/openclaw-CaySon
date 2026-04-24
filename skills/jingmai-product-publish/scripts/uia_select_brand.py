# -*- coding: utf-8 -*-
# 选择品牌 - 点击"品牌"下拉框
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
    
    # 查找所有可点击元素
    buttons = jingmai.descendants(control_type="Button")
    combos = jingmai.descendants(control_type="ComboBox")
    
    print(f"Buttons: {len(buttons)}, Combos: {len(combos)}")
    
    # 查找"品牌"相关元素
    print("Looking for '品牌'...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "品牌" in name and rect.width > 0:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击品牌下拉框 - 根据之前观察，Edit[2]是"型号 *"，品牌可能在附近
    # 尝试点击品牌区域
    print("\nTrying to click brand dropdown...")
    # 品牌选择框应该在y=500-600范围
    pyautogui.click(750, 550)  # 尝试点击品牌下拉框
    time.sleep(2)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
