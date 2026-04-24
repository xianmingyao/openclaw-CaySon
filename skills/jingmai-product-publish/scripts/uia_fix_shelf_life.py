# -*- coding: utf-8 -*-
# 修正保质期字段
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
    
    # 查找保质期输入框
    all_elements = jingmai.descendants()
    
    print("\n=== 查找保质期 ===")
    for elem in all_elements:
        try:
            name = elem.element_info.name or ""
            rect = elem.rectangle()
            if "保质" in name or "66" in name:
                ctype = elem.element_info.control_type
                print(f"  {ctype}: '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 保质期应该在 y=1200-1300 范围
    # 根据之前分析，Edit[13] at (1377, 1191) 可能是保质期
    # 但更准确的是找到具体的保质期Edit
    
    # 点击保质期Edit并修正
    print("\nFixing 保质期...")
    pyautogui.click(1377, 1191)
    time.sleep(0.5)
    
    # 只按delete清除，不要用ctrl+a
    pyautogui.press('delete')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.2)
    
    # 输入365（一年）
    pyautogui.typewrite('365', interval=0.1)
    time.sleep(0.5)
    
    print("\nDone!")

except Exception as e:
    print(f"Error: {e}")
