# -*- coding: utf-8 -*-
# 填写商品标题
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
    
    # 查找所有Edit
    edits = jingmai.descendants(control_type="Edit")
    print(f"Found {len(edits)} Edit elements:")
    
    for i, edit in enumerate(edits):
        try:
            name = edit.element_info.name or ""
            rect = edit.rectangle()
            print(f"  [{i}] '{name}' at ({rect.left}, {rect.top})")
        except:
            pass
    
    # 填写商品标题 - 使用Edit[0] 或第一个大输入框
    print("\nTrying to fill product title...")
    if edits:
        # 找商品标题输入框 - 通常在页面靠上位置
        for edit in edits:
            try:
                name = edit.element_info.name or ""
                rect = edit.rectangle()
                # 商品标题输入框通常在y=300-500范围
                if 300 <= rect.top <= 500 and rect.width() > 500:
                    print(f"  Using: '{name}' at ({rect.left}, {rect.top})")
                    
                    # 点击激活
                    pyautogui.click(rect.left + 50, rect.top + 10)
                    time.sleep(0.3)
                    
                    # 清除
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.2)
                    pyautogui.press('delete')
                    time.sleep(0.2)
                    
                    # 输入标题
                    title = "公牛（BULL）插座B5440系列86型暗装墙壁开关插座多位电源插座"
                    pyautogui.typewrite(title, interval=0.05)
                    time.sleep(0.5)
                    print(f"  Filled: {title[:20]}...")
                    break
            except Exception as e:
                print(f"  Error: {e}")
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
