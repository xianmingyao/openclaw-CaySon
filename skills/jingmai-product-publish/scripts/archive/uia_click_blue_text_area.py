# -*- coding: utf-8 -*-
# 直接点击蓝色近期使用类目文字
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
    
    # 尝试点击近期使用类目区域 - 蓝色链接应该在y=654行
    # 根据观察，"工业品>中低压配电>插座"是第一个条目
    # 蓝色文字可能比周围的灰色文字更靠右一点
    print("Clicking various positions in recent category area...")
    
    # 尝试多个位置
    positions = [
        (580, 654),   # "工业品"文字上
        (650, 654),   # 中间
        (720, 654),   # "中低压配电"附近
        (600, 660),   # 稍微偏移
        (680, 660),   # 
        (750, 660),
    ]
    
    for x, y in positions:
        print(f"  Trying ({x}, {y})...")
        pyautogui.click(x, y)
        time.sleep(1.5)
        
        # 截图看结果
        # 如果没效果，继续下一个位置
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
