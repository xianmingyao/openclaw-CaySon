from pywinauto import Application, Desktop
import time
import pyautogui
import win32gui
import win32con

# 直接使用 Win32 API 激活窗口
def activate_window_hwnd(hwnd):
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.3)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)

# 有道云笔记窗口的 HWND
Hwnd = 5639224

print('Activating window...')
activate_window_hwnd(Hwnd)
time.sleep(0.3)

# 尝试点击侧边栏顶部的 "+ 新建" 按钮
# 侧边栏在左侧，顶部按钮应该在 (100, 80) 左右
positions = [
    (100, 80),   # 侧边栏顶部
    (100, 100),  # 稍下
    (80, 80),    # 更左
    (120, 80),   # 更右
]

for i, (x, y) in enumerate(positions):
    print(f'Clicking at sidebar ({x}, {y})...')
    pyautogui.click(x, y)
    time.sleep(1)
    
    screenshot = pyautogui.screenshot()
    screenshot.save(f'E:\\workspace\\sidebar_click_{i+1}.png')

# 最终截图
screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\sidebar_final.png')
print('Done')
