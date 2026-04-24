# -*- coding: utf-8 -*-
# 使用ComboBox选择额定电压
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
    
    # 获取所有ComboBox
    combos = jingmai.descendants(control_type="ComboBox")
    print(f"Found {len(combos)} ComboBoxes")
    
    # 找额定电压的ComboBox
    for i, combo in enumerate(combos):
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            # 额定电压应该在y=848-900范围
            if 840 <= rect.top <= 920:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 选择额定电压 - 通常是第二个ComboBox在那个区域
    # 根据之前信息，额定电压是第三个必填属性
    # 尝试使用combo.select()
    print("\nTrying to select voltage...")
    
    # 找到"额定电压"相关的combo
    for combo in combos:
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            if rect.top == 848:  # 额定电压行
                print(f"Found voltage combo at ({rect.left}, {rect.top})")
                # 展开
                try:
                    combo.expand()
                except:
                    pass
                time.sleep(1)
                
                # 获取下拉选项
                try:
                    items = combo.items()
                    for item in items:
                        if "230V" in str(item):
                            print(f"Selecting 230V...")
                            item.select()
                            break
                except:
                    pass
                break
        except:
            pass
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
