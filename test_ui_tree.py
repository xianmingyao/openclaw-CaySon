from pywinauto import Application, Desktop
import time
import pyautogui

# 获取桌面
desktop = Desktop(backend='win32')

# 连接到指定 HWND 的窗口 (5311680 - 第一个有道云笔记相关窗口)
print('Connecting to HWND 5639224...')
try:
    app = Application(backend='win32')
    app.connect(handle=5639224)
    dlg = app.window(handle=5639224)
    
    # 激活窗口
    dlg.set_focus()
    time.sleep(0.3)
    
    # 尝试最大化
    try:
        dlg.maximize()
        time.sleep(0.3)
    except:
        pass
    
    # 打印窗口信息
    print(f'Window title: {dlg.window_text()}')
    print(f'Window is visible: {dlg.is_visible()}')
    
    # 截图
    screenshot = pyautogui.screenshot()
    screenshot.save('E:\\workspace\\chrome_hwnd.png')
    print('Screenshot saved')
    
except Exception as e:
    print(f'Error: {e}')
