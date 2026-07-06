# -*- coding: utf-8 -*-
# 按顺序填写物流相关字段
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
    
    # 向下滚动让页面往下走
    for i in range(5):
        pyautogui.scroll(-2, x=1280, y=700)
        time.sleep(0.2)
    
    # 1. 修正保质期 365
    print("1. Fixing 保质期(365) at (628, 890)...")
    pyautogui.click(628, 890)
    time.sleep(0.5)
    # 多次按delete清除
    for _ in range(10):
        pyautogui.press('delete')
        time.sleep(0.1)
    time.sleep(0.3)
    pyautogui.typewrite('365', interval=0.1)
    time.sleep(0.5)
    
    # 2. 选择销售单位 - 个
    print("2. Selecting 销售单位 at (1028, 890)...")
    pyautogui.click(1028, 890)
    time.sleep(1)
    
    # 查找销售单位选项
    all_elements = jingmai.descendants()
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            if "个" in name and len(name) <= 5:
                rect = elem.rectangle()
                print(f"   Found: '{name}' at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 50, rect.top + 5)
                time.sleep(0.5)
                break
        except:
            pass
    
    # 3. 选择商品包装
    print("3. Selecting 商品包装 at (628, 987)...")
    pyautogui.click(628, 987)
    time.sleep(1)
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            if len(name) <= 5 and name:
                rect = elem.rectangle()
                if 950 <= rect.top <= 1050:
                    print(f"   Found: '{name}' at ({rect.left}, {rect.top})")
                    pyautogui.click(rect.left + 50, rect.top + 5)
                    time.sleep(0.5)
                    break
        except:
            pass
    
    # 4. 选择特殊发货时效标记
    print("4. Selecting 特殊发货时效标记 at (1028, 987)...")
    pyautogui.click(1028, 987)
    time.sleep(1)
    
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if 950 <= rect.top <= 1050 and len(name) <= 5:
                print(f"   Found: '{name}' at ({rect.left}, {rect.top})")
                pyautogui.click(rect.left + 50, rect.top + 5)
                time.sleep(0.5)
                break
        except:
            pass
    
    # 5. 填写包装清单
    print("5. Filling 包装清单 at (616, 1165)...")
    pyautogui.click(616, 1165)
    time.sleep(0.5)
    for _ in range(20):
        pyautogui.press('delete')
        time.sleep(0.05)
    time.sleep(0.3)
    pyautogui.typewrite('插座x1 说明书x1', interval=0.1)
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
