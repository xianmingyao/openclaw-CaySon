# -*- coding: utf-8 -*-
# 向右拖动并填写价格
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
    print("Scrolling up...")
    for i in range(12):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 向右拖动滚动条
    print("Dragging scrollbar...")
    pyautogui.mouseDown(1500, 915)
    time.sleep(0.3)
    pyautogui.moveTo(1500 + 500, 915)
    time.sleep(0.3)
    pyautogui.mouseUp()
    time.sleep(1)
    
    # 截图看结果
    print("Taking screenshot...")
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
