# -*- coding: utf-8 -*-
# 填写重要属性：防护等级和极数
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    import pyperclip
    
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
    
    # ========== 1. 选择防护等级（重要属性）==========
    print("\n=== 1. 选择防护等级 ===")
    
    # 根据之前分析，防护等级"请选择"在(1036, 745)附近
    # 点击展开
    pyautogui.click(1036, 745)
    time.sleep(1.5)
    
    # 查找IP选项并选择第一个
    all_elements = jingmai.descendants()
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 700 <= rect.top <= 1000 and "IP" in name:
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 50, rect.top + 5)
                time.sleep(1)
                print("  Selected!")
                break
        except:
            pass
    
    # ========== 2. 选择极数 ==========
    print("\n=== 2. 选择极数 ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 极数"请选择"可能在(644, 745)
    pyautogui.click(644, 745)
    time.sleep(1.5)
    
    # 选择第一个选项（通常是3极）
    all_elements = jingmai.descendants()
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 700 <= rect.top <= 1000 and len(name) <= 3:
                if name.isdigit() or "极" in name:
                    print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                    pyautogui.click(rect.left + 30, rect.top + 5)
                    time.sleep(1)
                    print("  Selected!")
                    break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
