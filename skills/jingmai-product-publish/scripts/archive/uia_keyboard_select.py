# -*- coding: utf-8 -*-
# 用键盘选择ComboBox值
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
    
    # 向上滚动
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 1. 选择额定电压 250V~
    # ComboBox at (1036, 881)
    print("1. Selecting 额定电压 250V~...")
    pyautogui.click(1036, 881)
    time.sleep(0.5)
    
    # 按多次下箭头
    for _ in range(8):
        pyautogui.press('down')
        time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)
    print("   Done!")
    
    # 2. 选择电缆长度 5米
    # ComboBox at (644, 1026)
    print("2. Selecting 电缆长度 5米...")
    pyautogui.click(644, 1026)
    time.sleep(0.5)
    
    for _ in range(4):
        pyautogui.press('down')
        time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)
    print("   Done!")
    
    # 3. 选择极数
    # ComboBox at (1036, 1026)
    print("3. Selecting 极数...")
    pyautogui.click(1036, 1026)
    time.sleep(0.5)
    
    for _ in range(2):
        pyautogui.press('down')
        time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)
    print("   Done!")
    
    # 4. 选择防护等级 IP55
    # 需要向上滚动找
    print("4. Selecting 防护等级 IP55...")
    # 向上滚动一点
    for i in range(5):
        pyautogui.scroll(2, x=1280, y=700)
        time.sleep(0.2)
    
    # 找防护等级ComboBox
    combos = jingmai.descendants(control_type="ComboBox")
    for combo in combos:
        try:
            name = combo.element_info.name or ""
            if "防护" in name:
                rect = combo.rectangle()
                print(f"   Found 防护等级 at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 50, rect.top + 10)
                time.sleep(0.5)
                for _ in range(3):
                    pyautogui.press('down')
                    time.sleep(0.2)
                pyautogui.press('enter')
                print("   Done!")
                break
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
