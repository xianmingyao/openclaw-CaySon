import win32gui
import win32ui
import win32con

hwnd = 1377392

def get_child_windows(hwnd):
    """枚举所有子窗口"""
    result = []
    child = win32gui.FindWindowEx(hwnd, 0, None, None)
    while child:
        result.append(child)
        # 递归获取子窗口
        result.extend(get_child_windows(child))
        child = win32gui.FindWindowEx(hwnd, child, None, None)
    return result

children = get_child_windows(hwnd)
print(f'找到 {len(children)} 个子窗口')

# 获取每个子窗口的信息
for child in children[:50]:  # 只打印前50个
    try:
        title = win32gui.GetWindowText(child)
        cls_name = win32gui.GetClassName(child)
        rect = win32gui.GetWindowRect(child)
        if title:
            print(f'hwnd={child}, class="{cls_name}", title="{title}", rect={rect}')
    except Exception as e:
        pass
