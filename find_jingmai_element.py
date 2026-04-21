"""查找京麦窗口中的"商品"菜单项位置"""
import win32gui
import win32con
import win32ui
import win32api
from PIL import ImageGrab, Image
import time

def find_jingmai_menu_item(item_text):
    """查找京麦窗口中包含指定文字的菜单项位置"""
    # 先找到京麦窗口
    def find_jingmai_cb(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and ('jd_' in title.lower() or 'jingmai' in title.lower()):
                windows.append((hwnd, title))
        return True
    
    jingmai_windows = []
    win32gui.EnumWindows(find_jingmai_cb, jingmai_windows)
    
    if not jingmai_windows:
        print("未找到京麦窗口")
        return None
    
    hwnd = jingmai_windows[0][0]
    print(f"找到京麦窗口: {jingmai_windows[0][1]}, HWND: {hwnd}")
    
    # 尝试获取窗口内嵌的菜单栏
    try:
        menu = win32gui.GetMenu(hwnd)
        if menu:
            print(f"窗口有菜单栏: {menu}")
    except:
        print("窗口没有菜单栏")
    
    # 获取窗口客户区位置
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    # 转换为屏幕坐标
    pt = win32gui.ClientToScreen(hwnd, (left, top))
    print(f"客户区左上角: {pt}")
    print(f"客户区大小: {right-left}x{bottom-top}")
    
    # 尝试查找子窗口
    def enum_child_cb(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            classname = win32gui.GetClassName(hwnd)
            if title or classname:
                rect = win32gui.GetWindowRect(hwnd)
                results.append({
                    'hwnd': hwnd,
                    'title': title,
                    'classname': classname,
                    'rect': rect
                })
        return True
    
    children = []
    win32gui.EnumChildWindows(hwnd, enum_child_cb, children)
    
    # 找包含"商品"文字的窗口
    for child in children:
        if child['title'] and '商品' in child['title']:
            print(f"找到: {child['title']} at {child['rect']}")
            rect = child['rect']
            # 返回窗口中心点
            cx = (rect[0] + rect[2]) // 2
            cy = (rect[1] + rect[3]) // 2
            print(f"  -> 中心坐标: ({cx}, {cy})")
            return (cx, cy)
    
    print("未在子窗口中找到'商品'文字")
    
    # 打印所有可见子窗口（调试用）
    print("\n所有可见子窗口:")
    for child in children[:20]:
        if child['title']:
            print(f"  {child['title']} | {child['classname']} | {child['rect']}")
    
    return None

if __name__ == "__main__":
    pos = find_jingmai_menu_item("商品")
    if pos:
        print(f"\n点击位置: {pos}")
