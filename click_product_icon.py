"""点击京麦商品图标"""
import win32gui
import win32con
import win32api
import time

def find_jingmai_window():
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and ('jd_' in title.lower() or 'jingmai' in title.lower()):
                windows.append((hwnd, title))
        return True
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

def click_in_window(hwnd, x, y):
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    pt = win32gui.ClientToScreen(hwnd, (x, y))
    print(f"点击坐标 ({x}, {y}) -> 屏幕 ({pt[0]}, {pt[1]})")
    win32api.SetCursorPos((pt[0], pt[1]))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print("点击完成!")

windows = find_jingmai_window()
if windows:
    hwnd = windows[0][0]
    print(f"窗口: {windows[0][1]}, 大小: {win32gui.GetClientRect(hwnd)}")
    
    # 点击商品图标 - 第二个图标，Y约150-180
    print("点击商品图标...")
    click_in_window(hwnd, 30, 165)
