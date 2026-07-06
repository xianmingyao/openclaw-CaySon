# -*- coding: utf-8 -*-
# 直接找到SKU表格中的Edit元素
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
    
    # 向上滚动
    for i in range(15):
        pyautogui.scroll(3, x=1280, y=700)
        time.sleep(0.2)
    
    # 获取SKU表格区域的所有Edit
    all_edits = jingmai.descendants(control_type="Edit")
    
    print(f"\nFound {len(all_edits)} Edit elements total")
    
    # 打印SKU表格范围内的Edit（y=1200-1300）
    print("\n=== SKU Table Edits (y=1200-1300) ===")
    sku_edits = []
    for i, edit in enumerate(all_edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if 1200 <= rect.top <= 1300 and rect.width() > 50:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top}) size({rect.width()}x{rect.height()})")
                sku_edits.append((edit, name, rect))
        except:
            pass
    
    # 根据列位置，找到对应的Edit
    # 货期在x=912附近, 市场价x=1222, 采购价x=1338, 京东价x=1454
    
    print("\n=== Filling by position ===")
    
    # 遍历SKU edits，找到最接近目标x坐标的
    for edit, name, rect in sku_edits:
        x = rect.left
        # 货期 x≈912
        if 850 <= x <= 970:
            print(f"  货期: clicking at ({x}, {rect.top})")
            pyautogui.click(x + 30, rect.top + 10)
            time.sleep(0.3)
            pyperclip.copy("7")
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
    
    # 再获取一次Edit看结果
    time.sleep(0.5)
    all_edits = jingmai.descendants(control_type="Edit")
    print("\n=== After filling ===")
    for i, edit in enumerate(all_edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            if 1200 <= rect.top <= 1300 and rect.width() > 50:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
