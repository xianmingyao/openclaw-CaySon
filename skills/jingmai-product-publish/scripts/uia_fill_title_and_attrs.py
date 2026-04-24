# -*- coding: utf-8 -*-
# 继续填写标题和其他属性
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
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 1. 填写商品标题
    print("1. Filling 商品标题...")
    pyautogui.click(750, 302)
    time.sleep(0.5)
    title = "公牛BULL插座B5系列8位总控5米新国标防过载商业专用B5440"
    pyperclip.copy(title)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # 2. 修正额定电压 250V~
    print("2. Fixing 额定电压 250V~...")
    pyautogui.click(1036, 758)
    time.sleep(0.5)
    # 多按几次下箭头找到250V~
    for _ in range(5):
        pyautogui.press('down')
        time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # 3. 填写孔型配置 8位
    print("3. Filling 孔型配置 8位...")
    pyautogui.click(844, 1165)
    time.sleep(0.5)
    pyperclip.copy("8位（五孔×4+二孔×4）")
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
