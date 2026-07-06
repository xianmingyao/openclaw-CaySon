# -*- coding: utf-8 -*-
# 继续填写下拉框
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
    
    # 向下滚动
    for i in range(5):
        pyautogui.scroll(-2, x=1280, y=700)
        time.sleep(0.2)
    
    # 分析当前控件
    combos = jingmai.descendants(control_type="ComboBox")
    
    print("\n=== ComboBox elements ===")
    for i, combo in enumerate(combos):
        try:
            name = combo.element_info.name or ""
            rect = combo.rectangle()
            if rect.left > 0 and rect.width() > 0:
                print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 根据坐标，正确的下拉框是：
    # 销售单位: (1028, 890) -> ComboBox[9]
    # 商品包装: (628, 987) -> ComboBox[11]
    # 特殊发货时效: (1028, 987) -> ComboBox[12]
    
    # 1. 选择销售单位 - 点击后按4次下箭头选择"个"
    print("\n1. Selecting 销售单位...")
    pyautogui.click(1028, 890)
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.1)
    pyautogui.press('down')
    time.sleep(0.1)
    pyautogui.press('down')
    time.sleep(0.1)
    pyautogui.press('down')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # 2. 选择商品包装
    print("2. Selecting 商品包装...")
    pyautogui.click(628, 987)
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.1)
    pyautogui.press('down')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    # 3. 选择特殊发货时效标记
    print("3. Selecting 特殊发货时效标记...")
    pyautogui.click(1028, 987)
    time.sleep(0.5)
    pyautogui.press('down')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
