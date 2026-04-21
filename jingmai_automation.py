"""京麦窗口自动化控制 - 使用Windows API精确点击"""
import win32gui
import win32con
import win32api
import time
import ctypes

# 查找京麦窗口
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

# 激活窗口并保持前台
def activate_and_stay(hwnd):
    # 先让窗口最小化再恢复，这是激活 Qt 窗口的常用方法
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    time.sleep(0.2)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.3)
    # 使用 AllowSetForegroundWindow 允许设置前台
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass
    time.sleep(0.3)

# 发送鼠标点击到指定窗口的相对坐标
def click_in_window(hwnd, x, y):
    # 将前台窗口设置为目标窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    
    # 获取窗口客户区 rect
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    # 转换为屏幕坐标
    pt = win32gui.ClientToScreen(hwnd, (x, y))
    
    print(f"点击窗口 ({hwnd}) 坐标 ({x}, {y}) -> 屏幕坐标 ({pt[0]}, {pt[1]})")
    
    # 直接使用SetCursorPos和mouse_event
    win32api.SetCursorPos((pt[0], pt[1]))
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print(f"点击完成!")

def main():
    print("=" * 50)
    print("京麦窗口自动化控制")
    print("=" * 50)
    
    # 1. 找到京麦窗口
    windows = find_jingmai_window()
    if not windows:
        print("未找到京麦窗口!")
        return
    
    print(f"\n找到 {len(windows)} 个京麦窗口:")
    for hwnd, title in windows:
        print(f"  [{hwnd}] {title}")
    
    hwnd = windows[0][0]
    
    # 2. 激活窗口
    print(f"\n激活窗口: {windows[0][1]}")
    activate_and_stay(hwnd)
    
    # 3. 获取窗口信息
    rect = win32gui.GetWindowRect(hwnd)
    print(f"\n窗口区域: {rect}")
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    print(f"窗口大小: {width}x{height}")
    
    # 4. 根据窗口大小计算左侧菜单位置
    # 假设左侧菜单宽度约60px，高度约40px/项
    menu_items = ["首页", "常用", "商品", "采购", "库存", "营销", "店铺", "价格", "推广", "售后", "厂直", "定制品", "财务", "合规", "服务", "配置"]
    
    print(f"\n左侧菜单项 (假设菜单宽度60px):")
    for i, item in enumerate(menu_items):
        y = 100 + i * 45  # 从Y=100开始，每项间隔45px
        print(f"  {item}: X=30, Y={y}")
    
    # 5. 点击"商品" (第3项)
    item_to_click = "商品"
    idx = menu_items.index(item_to_click)
    target_y = 100 + idx * 45
    
    print(f"\n>>> 点击 '{item_to_click}' at X=30, Y={target_y}")
    click_in_window(hwnd, 30, target_y)
    
    # 6. 等待并截图
    time.sleep(1)
    
    print("\n完成! 请查看屏幕确认结果。")

if __name__ == "__main__":
    main()
