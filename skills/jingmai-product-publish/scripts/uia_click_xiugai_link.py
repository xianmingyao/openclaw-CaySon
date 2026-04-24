# -*- coding: utf-8 -*-
"""
点击"修改"按钮重新选择类目
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Clicking '修改' button...")

try:
    from pywinauto import Desktop
    import pyautogui
    import time
    
    desktop = Desktop(backend="uia")
    all_windows = desktop.windows()
    
    jingmai = None
    for w in all_windows:
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
        print("Main window not found!")
        exit(1)
    
    print("Found main window")
    jingmai.set_focus()
    time.sleep(0.5)
    
    # 找"修改"链接
    print("Looking for '修改' hyperlink...")
    links = jingmai.descendants(control_type="Hyperlink")
    
    xiugai = None
    for link in links:
        try:
            name = link.element_info.name or ""
            if "修改" in name:
                rect = link.rectangle()
                print(f"Found '修改' at ({rect.left}, {rect.top})")
                xiugai = link
                break
        except:
            pass
    
    if xiugai:
        print("Clicking '修改'...")
        try:
            xiugai.invoke()
        except:
            try:
                xiugai.click_input()
            except:
                rect = xiugai.rectangle()
                pyautogui.click(rect.left + 30, rect.top + 5)
        time.sleep(2)
        print("Clicked!")
    else:
        print("'修改' not found!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
