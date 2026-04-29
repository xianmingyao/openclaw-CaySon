# -*- coding: utf-8 -*-
# 直接点击ComboBox展开并选择
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
    
    # 向上滚动一点
    print("Scrolling...")
    for i in range(3):
        pyautogui.scroll(2, x=1280, y=700)
        time.sleep(0.2)
    
    # ========== 1. 选择防护等级 ==========
    print("\n=== 1. 选择防护等级 ===")
    
    # ComboBox[7] at (644, 636)
    combos = jingmai.descendants(control_type="ComboBox")
    if len(combos) > 7:
        combo = combos[7]
        rect = combo.rectangle()
        print(f"ComboBox[7] at ({rect.left}, {rect.top})")
        
        # 直接使用combo的选择方法
        try:
            print("Trying combo.select()...")
            # 获取选项
            items = combo.items()
            for item in items:
                item_text = str(item)
                if "IP" in item_text:
                    print(f"  Selecting: {item_text}")
                    item.select()
                    time.sleep(1)
                    print("  Done!")
                    break
        except Exception as e:
            print(f"  Error: {e}")
            # 回退到点击
            print("  Falling back to click...")
            pyautogui.click(rect.left + 100, rect.top + 10)
            time.sleep(1)
    
    # ========== 2. 选择极数 ==========
    print("\n=== 2. 选择极数 ===")
    
    if len(combos) > 8:
        combo = combos[8]
        rect = combo.rectangle()
        print(f"ComboBox[8] at ({rect.left}, {rect.top})")
        
        try:
            items = combo.items()
            for item in items:
                item_text = str(item)
                print(f"  Option: {item_text}")
                if item_text.isdigit() or "3" in item_text:
                    print(f"  Selecting: {item_text}")
                    item.select()
                    time.sleep(1)
                    break
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
