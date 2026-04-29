# -*- coding: utf-8 -*-
# 正确操作ComboBox - 选择销售单位
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
    
    # ComboBox位置：
    # [9] 销售单位 at (1028, 881)
    # [11] 商品包装 at (628, 964)
    # [12] 特殊发货时效标记 at (1028, 964)
    
    # 1. 选择销售单位 - 点击"请选择"旁边的箭头
    print("1. Selecting 销售单位...")
    # 点击ComboBox右侧的箭头区域
    pyautogui.click(1828, 881)  # 这是展开的下拉箭头
    time.sleep(1)
    
    # 用键盘选择第1项
    pyautogui.press('down')
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # 2. 选择商品包装
    print("2. Selecting 商品包装...")
    pyautogui.click(1828, 964)  # 展开箭头
    time.sleep(1)
    pyautogui.press('down')
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # 3. 选择特殊发货时效标记
    print("3. Selecting 特殊发货时效标记...")
    pyautogui.click(1828, 964)  # 可能是同一个位置
    time.sleep(1)
    pyautogui.press('down')
    time.sleep(0.3)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
