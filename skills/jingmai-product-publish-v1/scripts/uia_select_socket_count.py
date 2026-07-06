# -*- coding: utf-8 -*-
# 选择插位数
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
    
    # 点击"插位数"的"请选择" - (644, 1028)
    print("Clicking 插位数 at (644, 1028)...")
    pyautogui.click(644, 1028)
    time.sleep(1.5)
    
    # 查找插位数选项
    print("Looking for socket count options...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 找插座/插位相关的选项
            if rect.top > 1000 and ("插" in name or "位" in name or "孔" in name):
                if len(name) < 10:  # 过滤掉长文本
                    print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
