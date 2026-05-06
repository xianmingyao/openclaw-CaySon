# -*- coding: utf-8 -*-
# 使用键盘操作下拉框
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
    
    # 按Tab跳转到销售单位下拉框
    # 先按多次Tab到达目标位置
    print("Navigating with Tab...")
    for i in range(15):
        pyautogui.press('tab')
        time.sleep(0.2)
    
    # 现在应该在下拉框附近，用Alt+↓打开
    print("Opening dropdown with Alt+Down...")
    pyautogui.key_down('alt')
    time.sleep(0.1)
    pyautogui.press('down')
    time.sleep(0.1)
    pyautogui.key_up('alt')
    time.sleep(1)
    
    # 用箭头选择第1项
    print("Selecting with arrow keys...")
    pyautogui.press('down')
    time.sleep(0.2)
    pyautogui.press('down')
    time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
