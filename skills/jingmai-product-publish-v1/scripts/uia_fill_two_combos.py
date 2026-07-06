# -*- coding: utf-8 -*-
# 继续填写额定电压和电缆长度
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
    
    # 向上滚动，让商品属性区域可见
    for i in range(8):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 重新获取控件位置
    edits = jingmai.descendants(control_type="Edit")
    combos = jingmai.descendants(control_type="ComboBox")
    
    print(f"Found {len(edits)} Edits, {len(combos)} Combos")
    
    # 打印ComboBox位置
    print("\n=== ComboBox positions ===")
    for i, combo in enumerate(combos):
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            if rect.width() > 0:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 选择额定电压 (第5个ComboBox)
    print("\n1. Selecting 额定电压...")
    if len(combos) > 5:
        combo = combos[5]
        rect = combo.rectangle()
        print(f"   Combo[5] at ({rect.left}, {rect.top})")
        pyautogui.click(rect.left + 80, rect.top + 10)
        time.sleep(1)
        
        # 用键盘选择
        for _ in range(5):
            pyautogui.press('down')
            time.sleep(0.1)
        pyautogui.press('enter')
        print("   Done!")
    
    time.sleep(0.5)
    
    # 选择电缆长度 (第7个ComboBox)
    print("\n2. Selecting 电缆长度...")
    if len(combos) > 7:
        combo = combos[7]
        rect = combo.rectangle()
        print(f"   Combo[7] at ({rect.left}, {rect.top})")
        pyautogui.click(rect.left + 80, rect.top + 10)
        time.sleep(1)
        
        for _ in range(3):
            pyautogui.press('down')
            time.sleep(0.1)
        pyautogui.press('enter')
        print("   Done!")
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
