# -*- coding: utf-8 -*-
# 根据京东数据完善京麦商品信息
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
    
    # ========== 1. 完善商品标题 ==========
    print("\n=== 1. 完善商品标题 ===")
    edits = jingmai.descendants(control_type="Edit")
    
    if len(edits) > 1:
        title_edit = edits[1]
        rect = title_edit.rectangle()
        print(f"Title Edit at ({rect.left}, {rect.top})")
        
        # 点击激活
        pyautogui.click(rect.left + 50, rect.top + 10)
        time.sleep(0.5)
        
        # 全选清除
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # 输入完整标题（根据京东数据）
        title = "公牛BULL插座B5系列8位总控5米新国标防过载带儿童保护门插座B5440"
        print(f"Inputting: {title}")
        pyautogui.typewrite(title, interval=0.05)
        time.sleep(0.5)
    
    # ========== 2. 完善型号 ==========
    print("\n=== 2. 确认型号 ===")
    if len(edits) > 2:
        model_edit = edits[2]
        rect = model_edit.rectangle()
        
        # 点击确认
        pyautogui.click(rect.left + 50, rect.top + 10)
        time.sleep(0.3)
        pyautogui.press("tab")
        time.sleep(0.3)
        print(f"Model confirmed: B5440")
    
    # ========== 3. 选择额定电压（250V） ==========
    print("\n=== 3. 选择额定电压 250V ===")
    
    # 关闭任何弹窗
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # 点击额定电压下拉框
    pyautogui.click(1036, 883)
    time.sleep(1.5)
    
    # 选择250V
    pyautogui.click(1037, 960)
    time.sleep(1)
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
