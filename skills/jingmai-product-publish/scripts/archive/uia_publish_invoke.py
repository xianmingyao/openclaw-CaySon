# -*- coding: utf-8 -*-
# 使用UIA的invoke方法点击发布商品
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
    
    # 查找"发布商品"按钮
    buttons = jingmai.descendants(control_type="Button")
    
    for btn in buttons:
        try:
            name = btn.element_info.name or ""
            if "发布商品" in name:
                rect = btn.rectangle()
                print(f"Found: '{name}' at ({rect.left}, {rect.top})")
                
                # 尝试使用invoke
                try:
                    print("Trying invoke...")
                    btn.invoke()
                    time.sleep(3)
                    print("Invoked!")
                except Exception as e:
                    print(f"Invoke failed: {e}")
                    # 回退到点击
                    print("Falling back to click...")
                    pyautogui.click(rect.left + 100, rect.top + 10)
                    time.sleep(3)
                
                break
        except:
            pass
    
    print("Done!")

except Exception as e:
    print(f"Error: {e}")
