# -*- coding: utf-8 -*-
# 使用pywinauto正确操作ComboBox
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
    
    print(f"Found {len(combos)} ComboBox elements")
    for i, combo in enumerate(combos):
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 尝试展开ComboBox[1] (销售单位)
    if len(combos) > 1:
        print("\nTrying ComboBox[1] - 销售单位...")
        combo = combos[1]
        rect = combo.rectangle()
        
        # 点击展开
        pyautogui.click(rect.left + 100, rect.top + 10)
        time.sleep(1)
        
        # 尝试用pywinauto获取选项
        try:
            # 这是关键 - 使用wrapper_object()获取更强大的操作能力
            wrapper = combo.wrapper_object()
            print(f"  Combo wrapper: {wrapper}")
            
            # 尝试展开
            wrapper.expand()
            time.sleep(1)
            
            # 获取选项
            items = wrapper.items()
            print(f"  Items: {items}")
            
            # 选择"个"
            for item in items:
                item_text = str(item)
                print(f"    - '{item_text}'")
                if "个" in item_text:
                    item.select()
                    time.sleep(0.5)
                    print(f"  Selected: {item_text}")
                    break
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
