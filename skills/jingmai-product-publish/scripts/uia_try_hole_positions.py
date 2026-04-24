# -*- coding: utf-8 -*-
# 尝试点击孔型配置下拉框
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
    
    # 先按Esc关闭当前下拉框
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 尝试多个位置
    positions = [
        (660, 1028),  # 稍微右移
        (670, 1028),  
        (680, 1028),
        (650, 1028),
        (640, 1028),
    ]
    
    for x, y in positions:
        print(f"Trying ({x}, {y})...")
        pyautogui.click(x, y)
        time.sleep(1.5)
        
        # 检查是否打开了孔型配置
        all_elements = jingmai.descendants()
        for elem in all_elements:
            try:
                name = elem.element_info.name or ""
                if "五孔" in name or "三孔" in name or "四孔" in name:
                    print(f"  Found option: {name}")
                    # 点击这个选项
                    rect = elem.rectangle()
                    pyautogui.click(rect.left + 50, rect.top + 5)
                    time.sleep(1)
                    print(f"  Selected!")
                    break
            except:
                pass
        
        # 检查是否有孔型配置相关的选项出现
        found_hole = False
        for elem in all_elements:
            try:
                name = elem.element_info.name or ""
                rect = elem.rectangle()
                if rect.top > 1000 and ("孔" in name or "五孔" in name):
                    print(f"  Found: {name} at ({rect.left}, {rect.top})")
                    found_hole = True
            except:
                pass
        
        if found_hole:
            break
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
