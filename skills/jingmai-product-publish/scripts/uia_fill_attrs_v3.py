# -*- coding: utf-8 -*-
# 使用pywinauto ComboBox.items()选择
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
    
    # 向上滚动
    for i in range(10):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取ComboBox列表
    combos = jingmai.descendants(control_type="ComboBox")
    
    print(f"Found {len(combos)} Combos")
    
    # 打印每个ComboBox的信息
    for i, combo in enumerate(combos):
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            if rect.width() > 0:
                print(f"\n[{i}] '{name}' at ({rect.left}, {rect.top})")
                # 尝试获取items
                try:
                    items = combo.items()
                    for j, item in enumerate(items[:5]):
                        print(f"    [{j}] {item}")
                except Exception as e:
                    print(f"    Error getting items: {e}")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
