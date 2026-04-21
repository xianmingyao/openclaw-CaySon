"""
京麦商品发布 - 直接 UFO 自动化
不依赖 LLM，直接通过坐标点击完成
"""
import sys
import time
import tempfile
import win32gui
import win32con
import win32api
from pathlib import Path

# 添加 desktop-control 到路径
sys.path.insert(0, str(Path(__file__).parent / "skills" / "desktop-control-cli" / "desktop-control"))

from app.services.ufo_service import UFOService

def find_jingmai_window():
    """找到京麦窗口"""
    hwnd = win32gui.FindWindow(None, "jd_465d1abd3ee76")
    if hwnd:
        return hwnd
    
    # 尝试查找包含 jingmai 的窗口
    def enum_handler(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "jingmai" in title.lower() or "jd_" in title.lower():
                result.append(hwnd)
    
    result = []
    win32gui.EnumWindows(lambda h, r=result: enum_handler(h, r) or True, result)
    return result[0] if result else None

def click_at(hwnd, x, y):
    """发送点击事件"""
    # 确保窗口在前台
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    
    # 发送鼠标点击
    lParam = (y << 16) | x
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, lParam)
    time.sleep(0.05)
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

def main():
    print("=" * 50)
    print("京麦商品发布 - 直接自动化")
    print("=" * 50)
    
    # 1. 找到京麦窗口
    print("\n[1] 查找京麦窗口...")
    hwnd = find_jingmai_window()
    if not hwnd:
        print("[X] 未找到京麦窗口!")
        return
    print(f"[OK] Find window: {hwnd}")
    
    # 获取窗口位置
    rect = win32gui.GetWindowRect(hwnd)
    print(f"   窗口位置: {rect}")
    
    # 激活窗口
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    
    # 2. 点击"商品"菜单
    print("\n[2] 点击左侧菜单'商品'...")
    # 商品菜单位置 (相对于窗口)
    product_x = rect[0] + 30
    product_y = rect[1] + 170
    click_at(hwnd, 30, 170)
    time.sleep(0.5)
    print(f"   点击坐标: (30, 170)")
    
    # 3. 点击"发布商品"
    print("\n[3] 点击'发布商品'...")
    # 需要先找到发布商品的选项
    # 先移动鼠标到商品下方区域
    publish_x = rect[0] + 30
    publish_y = rect[1] + 215
    click_at(hwnd, 30, 215)
    time.sleep(0.5)
    print(f"   点击坐标: (30, 215)")
    
    # 4. 截图确认
    print("\n[4] 截图确认...")
    ufo = UFOService()
    screenshot_path = Path(tempfile.gettempdir()) / "jingmai_publish_check.png"
    
    # 简单的截图方式
    import win32ui
    from PIL import Image
    
    # 获取窗口DC
    hwindc = win32gui.GetWindowDC(hwnd)
    mfcdc = win32ui.CreateDCFromHandle(hwindc)
    savedc = mfcdc.CreateCompatibleDC()
    
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfcdc, width, height)
    savedc.SelectObject(bitmap)
    savedc.BitBlt((0, 0), (width, height), mfcdc, (0, 0), win32con.SRCCOPY)
    
    # 保存
    bmp_path = str(Path(tempfile.gettempdir()) / "jingmai_current.png")
    bitmap.SaveBitmapFile(savedc, bmp_path)
    
    # 清理
    win32gui.DeleteObject(bitmap.GetHandle())
    savedc.DeleteDC()
    mfcdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwindc)
    
    print(f"   截图保存: {bmp_path}")
    
    print("\n" + "=" * 50)
    print("自动化流程启动成功!")
    print("请观察京麦窗口，确认是否进入发布商品页面")
    print("=" * 50)

if __name__ == "__main__":
    main()
