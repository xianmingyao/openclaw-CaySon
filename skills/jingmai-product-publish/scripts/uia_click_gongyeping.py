# -*- coding: utf-8 -*-
"""
点击"工业品"一级类目
"""
import platform
if platform.system() != "Windows":
    print("This script only works on Windows")
    exit(1)

print("Clicking '工业品' first-level category...")

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
    
    # 找"工业品"文本 - 在y=271附近
    texts = jingmai.descendants(control_type="Text")
    
    gongyepin = None
    for txt in texts:
        try:
            name = txt.element_info.name or ""
            rect = txt.rectangle()
            # 找"工业品 "，注意后面有空格
            if name == "工业品 " or name.strip() == "工业品":
                # 在正确区域
                if 270 < rect.top < 280 and 600 < rect.left < 650:
                    print(f"Found '工业品 ' at ({rect.left}, {rect.top})")
                    gongyepin = txt
                    break
        except:
            pass
    
    if not gongyepin:
        # 尝试更宽的范围找"工业品"
        for txt in texts:
            try:
                name = txt.element_info.name or ""
                if "工业品" in name and len(name) < 10:
                    rect = txt.rectangle()
                    print(f"Checking '{name}' at ({rect.left}, {rect.top})")
                    if 260 < rect.top < 280:
                        gongyepin = txt
                        print(f"  -> Selected!")
                        break
            except:
                pass
    
    if gongyepin:
        print("Clicking '工业品'...")
        try:
            gongyepin.invoke()
        except:
            try:
                gongyepin.click_input()
            except:
                rect = gongyepin.rectangle()
                pyautogui.click(rect.left + 50, rect.top + 5)
        time.sleep(2)
        print("Clicked!")
    else:
        print("'工业品' not found, trying coordinate...")
        # (608, 271) 是之前找到的位置
        pyautogui.click(608, 271)
        time.sleep(2)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
