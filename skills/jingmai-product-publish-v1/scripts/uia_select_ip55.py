# -*- coding: utf-8 -*-
# 选择防护等级
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
    
    # ========== 1. 选择防护等级 ==========
    print("\n=== 1. 选择防护等级 ===")
    
    # 点击防护等级下拉框 (644, 638)
    print("Clicking 防护等级 at (644, 638)...")
    pyautogui.click(644, 638)
    time.sleep(2)
    
    # 查找IP选项
    all_elements = jingmai.descendants()
    print("Looking for IP options...")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "IP" in name and rect.top > 600:
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                # 点击第一个IP选项
                pyautogui.click(rect.left + 50, rect.top + 5)
                time.sleep(1)
                print("  Selected IP55!")
                break
        except:
            pass
    
    # ========== 2. 选择极数 ==========
    print("\n=== 2. 选择极数 ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 点击极数下拉框 (1036, 638)
    print("Clicking 极数 at (1036, 638)...")
    pyautogui.click(1036, 638)
    time.sleep(2)
    
    # 选择第一个选项
    all_elements = jingmai.descendants()
    print("Looking for pole options...")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if rect.top > 600 and (name.isdigit() or "极" in name):
                if len(name) <= 3:
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
