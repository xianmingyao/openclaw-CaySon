# -*- coding: utf-8 -*-
# 使用Tab导航填写表单
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
    
    # 向上滚动到顶部
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 从商品标题开始，用Tab导航
    print("Starting from title...")
    
    # 第1次Tab到商品标题输入框
    for _ in range(2):
        pyautogui.press('tab')
        time.sleep(0.2)
    
    # 输入商品标题
    print("Typing title...")
    pyautogui.typewrite("公牛BULL插座B5系列8位总控5米新国标防过载商业专用B5440", interval=0.05)
    time.sleep(0.5)
    
    # Tab到下一个字段
    pyautogui.press('tab')
    time.sleep(0.3)
    
    # 输入型号
    print("Typing model...")
    pyautogui.typewrite("B5440", interval=0.05)
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
