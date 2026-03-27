from pywinauto import Application, Desktop
import time
import pyautogui
import win32gui
import win32con

# 直接使用 Win32 API 激活窗口
def activate_window_hwnd(hwnd):
    """使用 Win32 API 激活窗口"""
    try:
        # 判断窗口是否最小化
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.3)
        
        # 激活窗口
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        print(f'Window {hwnd} activated')
        return True
    except Exception as e:
        print(f'Error activating window: {e}')
        return False

# 有道云笔记窗口的 HWND
Hwnd = 5639224

print('Step 1: Activating window with Win32 API...')
activate_window_hwnd(Hwnd)

print('Step 2: Taking screenshot to verify...')
time.sleep(0.3)
screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\verify_activation.png')
print('Screenshot saved')

print('Step 3: Clicking on 新建笔记 button...')
# 根据截图，按钮在中间位置
# 屏幕分辨率是 1920x1080
pyautogui.click(960, 540)
time.sleep(1)

print('Step 4: Taking screenshot to check result...')
screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\after_click.png')
print('Done')
