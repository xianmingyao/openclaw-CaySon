# -*- coding: utf-8 -*-
"""
使用UIA invoke()方法点击"修改"
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Using UIA invoke() to click 'xiugai'...")

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
    
    # Find all Hyperlinks with "修改"
    print("Finding '修改' hyperlink...")
    links = jingmai.descendants(control_type="Hyperlink")
    xiugai = None
    for link in links:
        try:
            name = link.element_info.name or ""
            if "修改" in name:
                rect = link.rectangle()
                print(f"Found: '{name}' at ({rect.left}, {rect.top})")
                xiugai = link
                break
        except:
            pass
    
    if xiugai:
        print("Clicking via invoke()...")
        try:
            # 方法1: invoke()
            xiugai.invoke()
            print("invoke() called!")
        except Exception as e:
            print(f"Error: {e}")
            # 方法2: 直接调用
            try:
                xiugai()
                print("Direct call worked!")
            except Exception as e2:
                print(f"Error2: {e2}")
        time.sleep(3)
    else:
        print("'修改' not found")
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
