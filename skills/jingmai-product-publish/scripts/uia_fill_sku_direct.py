# -*- coding: utf-8 -*-
# 直接点击SKU数据行填写
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    import pyperclip
    
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
    for i in range(15):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # TabItem表头在y=1269，数据行应该在y=1269+35=1304左右
    # 根据列位置，直接点击数据区域
    data_y = 1304
    
    # 1. 货期 - x=912 (表头中心)，数据区域偏移
    print("Clicking 货期 data area...")
    pyautogui.click(920, data_y)
    time.sleep(0.5)
    
    # 检查是否有输入框激活
    edits = jingmai.descendants(control_type="Edit")
    print(f"  Found {len(edits)} Edit elements after click")
    
    # 直接用键盘输入
    print("Typing 7...")
    pyautogui.press('7')
    time.sleep(0.3)
    
    # Tab到下一个字段
    pyautogui.press('tab')
    time.sleep(0.3)
    
    # 2. 市场价 82.35
    print("Typing 82.35...")
    pyautogui.press('backspace')
    time.sleep(0.1)
    for c in "82.35":
        pyautogui.press(c)
        time.sleep(0.05)
    time.sleep(0.3)
    
    # Tab到下一个字段
    pyautogui.press('tab')
    time.sleep(0.3)
    
    # 3. 采购价 66.5
    print("Typing 66.5...")
    pyautogui.press('backspace')
    time.sleep(0.1)
    for c in "66.5":
        pyautogui.press(c)
        time.sleep(0.05)
    time.sleep(0.3)
    
    # Tab到下一个字段
    pyautogui.press('tab')
    time.sleep(0.3)
    
    # 4. 京东价 70
    print("Typing 70...")
    pyautogui.press('backspace')
    time.sleep(0.1)
    for c in "70":
        pyautogui.press(c)
        time.sleep(0.05)
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
