# -*- coding: utf-8 -*-
# 输入孔型配置
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
    
    # 孔型配置在"必填属性"下，label在y=848
    # 输入框可能在label下方，约y=870-880
    # 尝试点击
    print("Trying to click 孔型配置 input...")
    
    # 尝试几个可能的位置
    positions = [
        (700, 880),  # 可能在label下方
        (750, 880),
        (700, 870),
        (750, 870),
        (700, 885),
        (750, 885),
    ]
    
    for x, y in positions:
        print(f"  Trying ({x}, {y})...")
        pyautogui.click(x, y)
        time.sleep(0.5)
        
        # 检查是否激活了某个输入框
        # 尝试输入文本
        pyautogui.typewrite("五孔", interval=0.1)
        time.sleep(0.5)
        
        # 按Tab继续
        pyautogui.press("tab")
        time.sleep(0.5)
        
        # 截图看结果
        # 如果输入成功，"孔型配置"应该不再是"请输入"
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
