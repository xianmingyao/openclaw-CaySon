# -*- coding: utf-8 -*-
# 直接点击230V
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
    
    # 直接点击230V的位置 (根据之前的列表，230V应该在弹出列表中)
    # 点击"额定电压"下拉框
    print("Clicking 额定电压 dropdown...")
    pyautogui.click(1036, 883)
    time.sleep(1.5)
    
    # 点击230V选项 - 根据列表位置调整
    # 列表是415V, 250V, 440V, 230V, 500V, 36V, 110V, 400V, 5V, 200V
    # 230V是第4个，每个选项大约20-25px高
    # 起始y约913
    print("Clicking 230V...")
    pyautogui.click(1100, 920)  # 230V大概位置
    time.sleep(1)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
