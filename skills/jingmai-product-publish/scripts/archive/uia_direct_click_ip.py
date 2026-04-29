# -*- coding: utf-8 -*-
# 直接点击IP55选项
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
    
    # ========== 1. 展开防护等级下拉框 ==========
    print("\n=== 1. Click 防护等级 dropdown ===")
    pyautogui.click(644, 641)
    time.sleep(2)
    
    # 根据之前的分析，IP选项列表文本"IP55 IP66 IP50..."在(632, 668)
    # 让我查找下拉选项的准确位置
    all_elements = jingmai.descendants()
    ip_options = []
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 防护等级选项应该在y=660-750范围
            if 660 <= rect.top <= 750 and "IP" in name:
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                ip_options.append((elem, name, rect))
        except:
            pass
    
    # 点击第一个IP选项 (IP55)
    if ip_options:
        elem, name, rect = ip_options[0]
        print(f"\nClicking IP55 at ({rect.left}, {rect.top})...")
        try:
            elem.invoke()
        except:
            pyautogui.click(rect.left + 30, rect.top + 5)
        time.sleep(1)
        print("Selected!")
    
    # ========== 2. 选择极数 ==========
    print("\n=== 2. Click 极数 dropdown ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    pyautogui.click(1036, 641)
    time.sleep(2)
    
    # 查找极数选项
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 660 <= rect.top <= 750 and (name.isdigit() or "极" in name):
                if len(name) <= 3:
                    print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
                    try:
                        elem.invoke()
                    except:
                        pyautogui.click(rect.left + 20, rect.top + 5)
                    time.sleep(1)
                    print("Selected!")
                    break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
