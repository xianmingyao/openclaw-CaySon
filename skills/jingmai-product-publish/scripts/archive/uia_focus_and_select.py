# -*- coding: utf-8 -*-
# 聚焦京麦窗口并选择防护等级和极数
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
    
    # 先按Esc关闭任何弹窗
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # ========== 1. 选择防护等级 ==========
    print("=== 1. 选择防护等级 ===")
    # 防护等级"请选择"在(1036, 1042)
    print("Clicking 防护等级 at (1036, 1042)...")
    pyautogui.click(1036, 1042)
    time.sleep(2)
    
    # 查找IP选项
    all_elements = jingmai.descendants()
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 1000 <= rect.top <= 1200 and "IP" in name:
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                # 点击第一个IP选项
                pyautogui.click(rect.left + 50, rect.top + 5)
                time.sleep(1)
                break
        except:
            pass
    
    # ========== 2. 选择极数 ==========
    print("\n=== 2. 选择极数 ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 极数"请选择"在(644, 1042)
    print("Clicking 极数 at (644, 1042)...")
    pyautogui.click(644, 1042)
    time.sleep(2)
    
    # 查找极数选项 - 极数通常是2、3等
    all_elements = jingmai.descendants()
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 选项通常在1040-1200范围
            if 1040 <= rect.top <= 1200:
                if name in ["2", "3", "4", "5", "6", "8"]:
                    print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                    pyautogui.click(rect.left + 30, rect.top + 5)
                    time.sleep(1)
                    break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
