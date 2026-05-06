# -*- coding: utf-8 -*-
# 重新聚焦京麦并选择防护等级和极数
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
    
    print("Found window, setting focus...")
    jingmai.set_focus()
    time.sleep(0.5)
    
    # ========== 1. 选择防护等级 ==========
    print("=== 1. 选择防护等级 ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 防护等级在"重要属性"区域
    # 先查找所有"请选择"
    all_elements = jingmai.descendants()
    
    print("All '请选择' elements:")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if name == "请选择" and rect.top > 1000:
                print(f"  at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击防护等级"请选择"
    print("Clicking 防护等级...")
    pyautogui.click(1036, 1042)
    time.sleep(2)
    
    # 选择第一个IP选项
    print("Selecting first IP...")
    pyautogui.click(1037, 928)
    time.sleep(1)
    
    # ========== 2. 选择极数 ==========
    print("\n=== 2. 选择极数 ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    print("Clicking 极数...")
    pyautogui.click(644, 1042)
    time.sleep(2)
    
    # 选择第一个选项
    print("Selecting first option...")
    pyautogui.click(1037, 928)
    time.sleep(1)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
