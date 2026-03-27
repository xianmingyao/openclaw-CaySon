import win32gui
import win32con

# 枚举所有窗口
all_windows = []
def callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        classname = win32gui.GetClassName(hwnd)
        if title:  # 只显示有标题的窗口
            all_windows.append({
                'hwnd': hwnd,
                'title': title,
                'class': classname
            })
win32gui.EnumWindows(callback, all_windows)

print(f"Found {len(all_windows)} visible windows with titles:\n")
for w in sorted(all_windows, key=lambda x: x['title']):
    print(f"HWND: {w['hwnd']}, Title: {w['title']}")
