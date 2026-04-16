"""
智能音乐自动化脚本 - 正确坐标 (292, 22)
基于窗口位置计算
"""
import pyautogui
import time
import os
import subprocess
import sys
import importlib.util
import ctypes

SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

DESKTOP_APP_PATH = r'E:\Program Files\Tencent\QQMusic\QQMusic.exe'

class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), 
                ('right', ctypes.c_long), ('bottom', ctypes.c_long)]

def get_window_handle(process_name):
    result = subprocess.run(
        ['powershell', '-Command', f'Get-Process -Name {process_name} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty MainWindowHandle'],
        capture_output=True, text=True, timeout=5
    )
    return int(result.stdout.strip())

def get_window_rect(hwnd):
    user32 = ctypes.windll.user32
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect

def load_skill():
    spec = importlib.util.spec_from_file_location("dc", 
        r'E:\workspace\skills\desktop-control-1-0-0\__init__.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules["dc"] = module
    spec.loader.exec_module(module)
    return module

def main():
    print("=== Smart Music Automation - Correct Coordinates ===")
    
    dc = load_skill().DesktopController()
    
    # 1. 启动QQ音乐
    print("[Step 1] Starting QQMusic...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)
    
    # 2. 获取窗口位置
    print("[Step 2] Getting window rect...")
    hwnd = get_window_handle("QQMusic")
    rect = get_window_rect(hwnd)
    print(f"[INFO] Window: ({rect.left}, {rect.top}) to ({rect.right}, {rect.bottom})")
    
    # 计算搜索框位置
    # QQ音乐搜索框在窗口顶部，左侧是Logo，搜索框在Logo右边
    search_x = rect.left + 250  # Logo右侧
    search_y = rect.top + 30    # 窗口顶部以下
    print(f"[INFO] Search box position: ({search_x}, {search_y})")
    
    # 3. 激活窗口
    print("[Step 3] Activating window...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'correct_step1.png'))
    
    # 4. 关闭弹窗
    print("[Step 4] Closing popup...")
    pyautogui.press('esc')
    time.sleep(0.5)
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'correct_step2.png'))
    
    # 5. 点击搜索框
    print(f"[Step 5] Clicking search box at ({search_x}, {search_y})...")
    dc.click(search_x, search_y)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'correct_step3_clicked.png'))
    
    # 6. 输入搜索词
    print("[Step 6] Typing 'faruxue'...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'correct_step4_typed.png'))
    
    # 7. 按回车搜索
    print("[Step 7] Pressing Enter...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    dc.press("enter")
    time.sleep(4)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'correct_step5_results.png'))
    
    # 8. 点击第一首歌曲
    print("[Step 8] Clicking first song...")
    dc.click(600, 280)
    time.sleep(1)
    dc.double_click(600, 280)
    time.sleep(2)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'correct_step6_playing.png'))
    
    print("=== Done ===")

if __name__ == "__main__":
    main()
