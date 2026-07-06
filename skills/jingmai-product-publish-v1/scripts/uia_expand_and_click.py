# -*- coding: utf-8 -*-
# 展开下拉框后用鼠标点击选项
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
    
    # 1. 先点击空白处关闭所有展开的控件
    pyautogui.click(100, 100)
    time.sleep(0.3)
    
    # 2. 选择销售单位 - 先点击展开下拉框
    print("1. Clicking 销售单位 dropdown...")
    pyautogui.click(1028, 881)
    time.sleep(1)
    
    # 分析展开后的所有元素
    all_elements = jingmai.descendants()
    
    print("\n=== Looking for dropdown options ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            # 查找y坐标在880-980范围内的元素（销售单位下拉展开后的选项）
            if 850 <= rect.top <= 980 and rect.left > 0:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击"个"选项 - 根据分析，"个"应该在y=910附近
    print("\nClicking '个' option...")
    pyautogui.click(1100, 910)
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
