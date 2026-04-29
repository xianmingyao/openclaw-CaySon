# -*- coding: utf-8 -*-
# 关闭下拉框并点击孔型配置
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
    
    # 按Esc关闭当前下拉框
    print("Pressing Escape to close...")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 点击孔型配置下拉框 - ComboBox[7] at (644, 1026)
    print("Clicking 孔型配置 at (644, 1026)...")
    pyautogui.click(644, 1026)
    time.sleep(1.5)
    
    # 查找选项
    print("Looking for 孔型配置 options...")
    all_elements = jingmai.descendants()
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 选项通常在y=1000-1200范围
            if 1000 <= rect.top <= 1200 and name and len(name) > 1:
                ctype = elem.element_info.control_type
                if "孔" in name or "五孔" in name or "三孔" in name or "二孔" in name:
                    print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 也打印所有y=1000-1100的文本
    print("\nAll texts in y=1000-1100:")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 1000 <= rect.top <= 1100 and name and len(name.strip()) > 1:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
