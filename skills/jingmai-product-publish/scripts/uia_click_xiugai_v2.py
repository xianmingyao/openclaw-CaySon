# -*- coding: utf-8 -*-
"""
使用UIA点击修改按钮
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Using UIA to click 'xiugai'...")

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
    time.sleep(1)
    
    # Find all Hyperlinks
    print("Finding Hyperlinks...")
    links = jingmai.descendants(control_type="Hyperlink")
    xiugai_link = None
    for link in links:
        try:
            name = link.element_info.name or ""
            if "修改" in name:
                rect = link.rectangle()
                print(f"Found '修改' at ({rect.left}, {rect.top})")
                xiugai_link = link
                break
        except:
            pass
    
    if xiugai_link:
        print("Clicking...")
        try:
            xiugai_link.click()
            print("Clicked!")
        except Exception as e:
            print(f"Error: {e}")
            # Fallback to pyautogui
            rect = xiugai_link.rectangle()
            print(f"Fallback: pyautogui.click({rect.left}, {rect.top})")
            pyautogui.click(rect.left, rect.top)
        time.sleep(2)
    else:
        print("'修改' not found")
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
