# -*- coding: utf-8 -*-
# 直接用键盘输入商品标题
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
    
    # 点击商品标题输入框
    print("Clicking 商品标题...")
    pyautogui.click(750, 425)
    time.sleep(1)
    
    # 直接用键盘输入
    print("Typing title with keyboard...")
    title = "公牛BULL插座B5系列8位总控5米新国标防过载商业专用B5440"
    pyautogui.typewrite(title, interval=0.05)
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
