"""将京麦窗口激活并显示到前台"""
import win32gui
import win32con
import win32api
import time

def find_jingmai_window():
    """找到京麦窗口"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and ('jingmai' in title.lower() or 'jd_' in title.lower() or '京麦' in title):
                windows.append((hwnd, title))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

def activate_window(hwnd):
    """激活窗口"""
    # 先恢复窗口（如果最小化）
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.2)
    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)

def main():
    print("正在查找京麦窗口...")
    windows = find_jingmai_window()
    
    if not windows:
        print("未找到京麦窗口！")
        return
    
    print(f"找到 {len(windows)} 个可能的京麦窗口:")
    for hwnd, title in windows:
        print(f"  - HWND: {hwnd}, 标题: {title}")
    
    # 激活第一个（主）京麦窗口
    hwnd = windows[0][0]
    print(f"\n激活窗口: {windows[0][1]}")
    activate_window(hwnd)
    print("完成！")

if __name__ == "__main__":
    main()
