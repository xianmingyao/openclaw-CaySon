# -*- coding: utf-8 -*-
# 拖动SKU表格水平滚动条
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
    
    # 向上滚动到正确位置
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 拖动水平滚动条（y=912行的滚动条）
    # 滚动条通常在表格下方
    print("Dragging horizontal scrollbar...")
    scrollbar_x = 1400  # 滚动条中间位置
    scrollbar_y = 912
    
    # 从中间向右拖动
    pyautogui.mouseDown(scrollbar_x, scrollbar_y)
    time.sleep(0.2)
    pyautogui.moveTo(scrollbar_x + 300, scrollbar_y)
    time.sleep(0.2)
    pyautogui.mouseUp()
    time.sleep(1)
    
    # 截图看结果
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
