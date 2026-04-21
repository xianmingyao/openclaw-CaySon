"""京麦自动化 - 使用窗口矩形坐标"""
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

def click_at_screen_coords(x, y):
    """直接点击屏幕坐标"""
    print(f"直接点击屏幕坐标: ({x}, {y})")
    win32api.SetCursorPos((x, y))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print("点击完成!")

windows = find_jingmai_window()
if windows:
    hwnd = windows[0][0]
    title = windows[0][1]
    
    # 获取窗口矩形（屏幕坐标）
    rect = win32gui.GetWindowRect(hwnd)
    print(f"窗口 '{title}' 屏幕矩形: {rect}")
    # rect = (left, top, right, bottom)
    
    # 假设左侧菜单在窗口左侧
    # 根据截图，窗口宽度2560，高度1392
    # 左侧菜单图标模式宽度约60px
    # 商品图标在顶部往下约150px位置（相对于窗口顶部）
    
    # 计算商品图标的屏幕坐标
    window_left, window_top = rect[0], rect[1]
    window_width = rect[2] - rect[0]
    window_height = rect[3] - rect[1]
    
    print(f"窗口大小: {window_width}x{window_height}")
    print(f"窗口左上角: ({window_left}, {window_top})")
    
    # 商品图标位置（根据截图估算）
    # 在图标模式的左侧栏，X约30-40，Y在顶部往下约150-180
    target_x = window_left + 30
    target_y = window_top + 170
    
    print(f"\n点击商品图标: ({target_x}, {target_y})")
    click_at_screen_coords(target_x, target_y)
    
    time.sleep(1)
    
    # 再点击一次确保
    print("再次点击商品图标...")
    click_at_screen_coords(target_x, target_y)
