# -*- coding: utf-8 -*-
# 点击第一个草稿进行编辑
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
    
    # 查找第一个草稿的编辑按钮
    # 根据截图，"暂无商品标题"在第一行
    # 编辑链接通常在商品行的某列
    
    # 尝试点击第一行的编辑链接
    # 商品名称列在左侧，编辑按钮通常在右侧
    # 根据UI分析，编辑链接可能在 x=2100, y=430 附近
    
    print("Looking for edit links...")
    
    links = jingmai.descendants(control_type="Hyperlink")
    for link in links:
        try:
            name = link.element_info.name or ""
            rect = link.rectangle()
            if "编辑" in name:
                print(f"  Found: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 点击第一个"编辑"链接
    print("\nClicking first edit link...")
    pyautogui.click(2150, 430)
    time.sleep(3)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
