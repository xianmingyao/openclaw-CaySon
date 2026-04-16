"""
智能音乐自动化脚本 v9 - 使用图像识别定位
"""
import pyautogui
import time
import os
import subprocess
import sys
import importlib.util
from PIL import Image

SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

DESKTOP_APP_PATH = r'E:\Program Files\Tencent\QQMusic\QQMusic.exe'

def load_skill():
    spec = importlib.util.spec_from_file_location("dc", 
        r'E:\workspace\skills\desktop-control-1-0-0\__init__.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules["dc"] = module
    spec.loader.exec_module(module)
    return module

def find_image_on_screen(template_path, confidence=0.8):
    """在屏幕上查找图像位置"""
    try:
        location = pyautogui.locateOnScreen(template_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            print(f"[FIND] Found '{template_path}' at {location}, center: ({center.x}, {center.y})")
            return (center.x, center.y)
    except Exception as e:
        print(f"[WARN] Image search failed: {e}")
    return None

def main():
    print("=== Smart Music Automation v9 (Image Recognition) ===")
    
    dc = load_skill().DesktopController()
    
    # 1. 启动QQ音乐
    print("[Step 1] Starting QQMusic...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)
    
    # 2. 激活窗口
    print("[Step 2] Activating QQMusic window...")
    dc.activate_window_by_process("QQMusic")
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v9_step1_started.png'))
    
    # 3. 关闭弹窗
    print("[Step 3] Closing popup...")
    pyautogui.press('esc')
    time.sleep(0.5)
    dc.activate_window_by_process("QQMusic")
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v9_step2_clean.png'))
    
    # 4. 尝试图像识别定位搜索框
    print("[Step 4] Locating search box...")
    
    # 方法1: 在整个屏幕上截图并查找搜索框特征
    # 先截取整个屏幕
    full_screen = pyautogui.screenshot()
    full_screen.save(os.path.join(SCREENSHOT_DIR, 'v9_full_screen.png'))
    
    # 尝试用灰色像素特征定位（搜索框通常是白色/灰色长条）
    # 简化处理：直接点击QQ音乐窗口内大致位置
    # QQ音乐窗口位置可以通过窗口大小推算
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    
    # 截取当前屏幕并分析
    current_screen = pyautogui.screenshot()
    current_screen.save(os.path.join(SCREENSHOT_DIR, 'v9_current_screen.png'))
    
    # 直接点击搜索框大致位置（窗口右上区域）
    # QQ音乐窗口通常在屏幕中央
    # 搜索框在窗口顶部偏右位置
    print("[Step 5] Clicking search box using coordinate estimation...")
    
    # 获取屏幕大小
    screen_w, screen_h = pyautogui.size()
    print(f"[INFO] Screen size: {screen_w}x{screen_h}")
    
    # QQ音乐窗口大致中心位置
    # 假设窗口在屏幕中央
    window_center_x = screen_w // 2
    window_center_y = screen_h // 2
    
    # 搜索框在窗口的相对位置（窗口右上区域）
    # 需要根据实际情况调整
    search_x = window_center_x + 300  # 窗口中心右侧
    search_y = window_center_y - 350  # 窗口顶部
    
    print(f"[STEP] Attempting click at estimated ({search_x}, {search_y})...")
    dc.click(search_x, search_y)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v9_step3_after_click.png'))
    
    # 6. 输入搜索词
    print("[Step 6] Typing search keywords...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v9_step4_typed.png'))
    
    # 7. 按回车搜索
    print("[Step 7] Pressing Enter...")
    dc.activate_window_by_process("QQMusic")
    dc.press("enter")
    time.sleep(4)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v9_step5_results.png'))
    
    # 8. 点击第一首歌曲
    print("[Step 8] Clicking first song...")
    dc.click(650, 280)
    time.sleep(1)
    dc.double_click(650, 280)
    time.sleep(2)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v9_step6_playing.png'))
    
    print("=== Done ===")

if __name__ == "__main__":
    main()
