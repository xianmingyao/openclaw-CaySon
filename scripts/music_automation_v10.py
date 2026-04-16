"""
智能音乐自动化脚本 v10 - 基于窗口位置计算坐标
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
    _fields_ = [('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long)]

def get_window_rect_by_name(process_name):
    """通过进程名获取窗口位置"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', f'Get-Process -Name {process_name} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty MainWindowHandle'],
            capture_output=True, text=True, timeout=5
        )
        hwnd = int(result.stdout.strip())
        if hwnd:
            user32 = ctypes.windll.user32
            rect = RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            return rect
    except:
        pass
    return None

def load_skill():
    spec = importlib.util.spec_from_file_location("dc", 
        r'E:\workspace\skills\desktop-control-1-0-0\__init__.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules["dc"] = module
    spec.loader.exec_module(module)
    return module

def main():
    print("=== Smart Music Automation v10 (Dynamic Coordinates) ===")
    
    dc = load_skill().DesktopController()
    
    # 1. 启动QQ音乐
    print("[Step 1] Starting QQMusic...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)
    
    # 2. 获取窗口位置
    print("[Step 2] Getting window position...")
    rect = get_window_rect_by_name("QQMusic")
    if rect:
        win_w = rect.right - rect.left
        win_h = rect.bottom - rect.top
        win_cx = (rect.left + rect.right) // 2
        win_cy = (rect.top + rect.bottom) // 2
        
        print(f"[INFO] Window: {win_w}x{win_h} at ({rect.left}, {rect.top})")
        print(f"[INFO] Window Center: ({win_cx}, {win_cy})")
        
        # 计算搜索框位置（窗口内顶部居右）
        search_x = win_cx + win_w//4  # 窗口中心偏右
        search_y = win_cy - win_h//2 + 50  # 窗口顶部以下50像素
        
        print(f"[INFO] Calculated search box: ({search_x}, {search_y})")
    else:
        search_x, search_y = 1380, 42  # 默认值
        print(f"[WARN] Could not get window rect, using default: ({search_x}, {search_y})")
    
    # 3. 激活窗口
    print("[Step 3] Activating window...")
    dc.activate_window_by_process("QQMusic")
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v10_step1_started.png'))
    
    # 4. 关闭弹窗
    print("[Step 4] Closing popup...")
    pyautogui.press('esc')
    time.sleep(0.5)
    dc.activate_window_by_process("QQMusic")
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v10_step2_clean.png'))
    
    # 5. 点击搜索框
    print(f"[Step 5] Clicking search box at ({search_x}, {search_y})...")
    dc.click(search_x, search_y)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v10_step3_after_click.png'))
    
    # 6. 输入搜索词
    print("[Step 6] Typing search keywords...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v10_step4_typed.png'))
    
    # 7. 按回车搜索
    print("[Step 7] Pressing Enter...")
    dc.activate_window_by_process("QQMusic")
    dc.press("enter")
    time.sleep(4)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v10_step5_results.png'))
    
    # 8. 点击第一首歌曲
    print("[Step 8] Clicking first song...")
    dc.click(650, 280)
    time.sleep(1)
    dc.double_click(650, 280)
    time.sleep(2)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v10_step6_playing.png'))
    
    # 9. 最终确认
    print("[Step 9] Final check...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(3)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v10_step7_final.png'))
    
    print("=== Done ===")

if __name__ == "__main__":
    main()
