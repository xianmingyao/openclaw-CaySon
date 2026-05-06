# -*- coding: utf-8 -*-
"""
使用UIA点击修改按钮
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Using UIA to find and click 'xiugai' button...")

try:
    from pywinauto import Desktop
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
    
    # Search all elements for xiugai
    print("Searching for 'xiugai'...")
    all_elements = jingmai.descendants()
    for i, elem in enumerate(all_elements):
        try:
            name = elem.element_info.name or ""
            if "xiugai" in name.lower() or "修改" in name:
                ctype = elem.element_info.control_type
                rect = elem.rectangle()
                print(f"[{i}] {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # Try to click using child_window
    print("Trying child_window...")
    try:
        xiugai = jingmai.child_window(title="修改")
        if xiugai.exists():
            rect = xiugai.rectangle()
            print(f"Found at ({rect.left}, {rect.top})")
            xiugai.click()
            print("Clicked!")
        else:
            print("Not found")
    except Exception as e:
        print(f"Error: {e}")
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
