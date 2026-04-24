# -*- coding: utf-8 -*-
# 点击ComboBox然后用键盘选择
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
    for i in range(8):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 1. 选择额定电压 - 点击并按多次下箭头
    print("1. Selecting 额定电压 250V~...")
    # ComboBox[5] at (1036, 881)
    pyautogui.click(1036, 881)
    time.sleep(0.5)
    
    # 按下箭头直到选中250V~
    for i in range(8):
        pyautogui.press('down')
        time.sleep(0.15)
    
    pyautogui.press('enter')
    time.sleep(0.5)
    print("   Done!")
    
    # 2. 选择电缆长度 5米
    print("2. Selecting 电缆长度 5米...")
    # ComboBox[7] at (644, 946)
    pyautogui.click(644, 946)
    time.sleep(0.5)
    
    for i in range(3):
        pyautogui.press('down')
        time.sleep(0.15)
    
    pyautogui.press('enter')
    time.sleep(0.5)
    print("   Done!")
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
