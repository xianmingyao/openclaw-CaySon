# -*- coding: utf-8 -*-
# 根据京东数据修正商品属性
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
    
    # 点击额定电压下拉框
    print("Clicking 额定电压...")
    pyautogui.click(1036, 883)
    time.sleep(1.5)
    
    # 选择250V - 在列表中找
    print("Selecting 250V...")
    pyautogui.click(1037, 928)  # 第一个选项415V
    time.sleep(0.3)
    pyautogui.click(1037, 960)  # 第二个选项250V
    time.sleep(1)
    
    # ========== 2. 修改电缆长度为5米 ==========
    print("\n=== 2. 修改电缆长度为5米 ===")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 点击电缆长度下拉框 - 根据之前分析在(1036, 1042)
    print("Clicking 电缆长度...")
    pyautogui.click(1036, 1042)
    time.sleep(1.5)
    
    # 选择5米选项
    print("Selecting 5米...")
    pyautogui.click(1037, 928)  # 第一个选项
    time.sleep(0.3)
    pyautogui.click(1037, 960)  # 第二个选项
    time.sleep(0.3)
    pyautogui.click(1037, 992)  # 第三个选项 (1.8米)
    time.sleep(0.3)
    pyautogui.click(1037, 1024)  # 第四个选项 (4米)
    time.sleep(1)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
