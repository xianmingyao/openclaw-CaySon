"""
智能音乐自动化脚本 v8 - 精确坐标
使用修复后的 desktop-control 技能
"""
import pyautogui
import time
import os
import subprocess
import sys
import importlib.util

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

def main():
    print("=== Smart Music Automation v8 (Exact Coordinates) ===")
    
    dc = load_skill().DesktopController()
    
    # 1. 启动QQ音乐
    print("[Step 1] Starting QQMusic...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)
    
    # 2. 激活窗口
    print("[Step 2] Activating QQMusic window...")
    dc.activate_window_by_process("QQMusic")
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v8_step1_started.png'))
    
    # 3. 关闭弹窗
    print("[Step 3] Closing popup...")
    pyautogui.press('esc')
    time.sleep(0.5)
    dc.activate_window_by_process("QQMusic")
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v8_step2_popup_closed.png'))
    
    # 4. 点击搜索框 - 精确坐标 (1376, 154)
    print("[Step 4] Clicking search box at (1376, 154)...")
    dc.click(1376, 154)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v8_step3_search_clicked.png'))
    
    # 5. 输入搜索词
    print("[Step 5] Typing search keywords...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v8_step4_typed.png'))
    
    # 6. 按回车搜索
    print("[Step 6] Pressing Enter to search...")
    dc.activate_window_by_process("QQMusic")
    dc.press("enter")
    time.sleep(4)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v8_step5_search_results.png'))
    
    # 7. 点击第一首歌曲
    print("[Step 7] Clicking first song...")
    dc.click(650, 280)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v8_step6_song_clicked.png'))
    
    # 8. 双击播放
    print("[Step 8] Double-clicking to play...")
    dc.double_click(650, 280)
    time.sleep(2)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v8_step7_playing.png'))
    
    # 9. 最终确认
    print("[Step 9] Final check...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(3)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v8_step8_final.png'))
    
    print("=== Automation Complete ===")
    print(f"Screenshots: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    main()
