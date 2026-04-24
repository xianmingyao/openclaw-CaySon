# -*- coding: utf-8 -*-
# 填写电压250V
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
    
    # 根据分析，电压在"规格描述"表格中
    # 找电压输入框
    all_elements = jingmai.descendants()
    
    print("Looking for voltage input...")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "电压" in name or "电压" in name:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 电压输入框位置 - 根据之前分析在 Header: '*电压' at (947, 1144)
    # Edit可能在附近
    print("Clicking voltage input at (980, 1213)...")
    pyautogui.click(980, 1213)
    time.sleep(0.5)
    
    # 填写250V
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    
    pyperclip.copy("250")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    pyautogui.press("tab")
    time.sleep(0.5)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
