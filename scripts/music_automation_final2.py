"""
智能音乐自动化脚本 FINAL - 精确坐标 (215, 28)
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
    print("=== Smart Music Automation FINAL (Correct: 215, 28) ===")
    
    dc = load_skill().DesktopController()
    
    # 1. 启动QQ音乐
    print("[Step 1] Starting QQMusic...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)
    
    # 2. 激活窗口
    print("[Step 2] Activating QQMusic window...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'final_step1_started.png'))
    
    # 3. 关闭弹窗
    print("[Step 3] Closing popup...")
    pyautogui.press('esc')
    time.sleep(0.5)
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'final_step2_clean.png'))
    
    # 4. 点击搜索框 - 精确坐标
    print("[Step 4] Clicking search box at (215, 28)...")
    dc.click(215, 28)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'final_step3_after_click.png'))
    
    # 5. 输入搜索词
    print("[Step 5] Typing 'faruxue'...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'final_step4_typed.png'))
    
    # 6. 按回车搜索
    print("[Step 6] Pressing Enter...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    dc.press("enter")
    time.sleep(4)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'final_step5_results.png'))
    
    # 7. 点击第一首歌曲
    print("[Step 7] Clicking first song...")
    dc.click(500, 280)
    time.sleep(1)
    dc.double_click(500, 280)
    time.sleep(2)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'final_step6_playing.png'))
    
    # 8. 最终确认
    print("[Step 8] Final check...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(3)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'final_step7_final.png'))
    
    print("=== Automation Complete ===")

if __name__ == "__main__":
    main()
