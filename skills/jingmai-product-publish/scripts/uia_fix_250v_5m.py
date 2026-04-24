# -*- coding: utf-8 -*-
# 修改额定电压为250V和电缆长度为5米
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
    
    # ========== 1. 修改额定电压为250V ==========
    print("\n=== 1. 修改额定电压为250V ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 根据分析，额定电压的"请选择"在(1036, 745)
    # 点击它
    print("Clicking 额定电压 at (1036, 745)...")
    pyautogui.click(1036, 745)
    time.sleep(2)
    
    # 查找250V选项 - 通常在y=750-950范围
    print("Looking for 250V option...")
    all_elements = jingmai.descendants()
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "250V" in name:
                print(f"  Found 250V at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 50, rect.top + 5)
                time.sleep(1)
                break
        except:
            pass
    
    # ========== 2. 修改电缆长度为5米 ==========
    print("\n=== 2. 修改电缆长度为5米 ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 电缆长度的"请选择"在(644, 745)
    print("Clicking 电缆长度 at (644, 745)...")
    pyautogui.click(644, 745)
    time.sleep(2)
    
    # 查找5米选项
    print("Looking for 5米 option...")
    all_elements = jingmai.descendants()
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "5米" in name or "5��" in name:
                print(f"  Found at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 50, rect.top + 5)
                time.sleep(1)
                break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
