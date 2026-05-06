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
    
    # 1. 选择销售单位 - 用键盘操作
    print("1. Selecting 销售单位 with keyboard...")
    pyautogui.click(1028, 890)
    time.sleep(0.5)
    pyautogui.press('f4')  # 打开下拉框
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.3)
    pyautogui.press('down')
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # 2. 选择商品包装
    print("2. Selecting 商品包装 with keyboard...")
    pyautogui.click(628, 987)
    time.sleep(0.5)
    pyautogui.press('f4')
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # 3. 选择特殊发货时效标记
    print("3. Selecting 特殊发货时效标记 with keyboard...")
    pyautogui.click(1028, 987)
    time.sleep(0.5)
    pyautogui.press('f4')
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
