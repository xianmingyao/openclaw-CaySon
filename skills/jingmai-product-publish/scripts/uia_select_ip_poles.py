# -*- coding: utf-8 -*-
# 选择防护等级和极数
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
    time.sleep(1.5)
    
    # 查找IP选项
    all_elements = jingmai.descendants()
    print("Looking for IP options...")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 1000 <= rect.top <= 1200 and ("IP" in name or "55" in name):
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 选择第一个IP选项 (1037, 928)
    print("Selecting IP55...")
    pyautogui.click(1037, 928)
    time.sleep(1)
    
    # ========== 2. 选择极数 ==========
    print("\n=== 2. 选择极数 ===")
    # 极数"请选择"在(644, 1042)
    print("Clicking 极数 at (644, 1042)...")
    pyautogui.click(644, 1042)
    time.sleep(1.5)
    
    # 查找极数选项
    all_elements = jingmai.descendants()
    print("Looking for pole options...")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 1000 <= rect.top <= 1200 and ("极" in name or "位" in name or "3" in name or "2" in name):
                if len(name) < 10:
                    print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 选择第一个选项（通常是3极）
    print("Selecting first option...")
    pyautogui.click(1037, 928)  # 这个位置需要根据实际情况调整
    time.sleep(1)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
