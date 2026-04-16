"""
智能音乐自动化脚本 - 完整成功版 v3
使用正确的歌曲位置坐标 (261, 436)
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

def load_skill():
    spec = importlib.util.spec_from_file_location("dc", 
        r'E:\workspace\skills\desktop-control-1-0-0\__init__.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules["dc"] = module
    spec.loader.exec_module(module)
    return module

def main():
    print("=== Smart Music Automation - FINAL v3 ===")
    
    dc = load_skill().DesktopController()
    
    # 1. 启动QQ音乐
    print("[Step 1] Starting QQMusic...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)
    
    # 2. 激活窗口
    print("[Step 2] Activating window...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(1)
    
    # 3. 关闭弹窗
    print("[Step 3] Closing popup...")
    pyautogui.press('esc')
    time.sleep(0.5)
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    
    # 4. 点击搜索框
    print("[Step 4] Clicking search box at (242, 22)...")
    dc.click(242, 22)  # 搜索框位置
    time.sleep(1)
    
    # 5. 输入搜索词
    print("[Step 5] Typing 'faruxue'...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    
    # 6. 按回车搜索
    print("[Step 6] Pressing Enter...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    dc.press("enter")
    time.sleep(4)
    
    # 7. 点击第一首歌（发如雪）- 正确坐标 (261, 436)
    print("[Step 7] Clicking first song (发如雪) at (261, 436)...")
    dc.click(261, 436)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v3_step7_clicked.png'))
    
    # 8. 双击播放
    print("[Step 8] Double-clicking to play...")
    dc.double_click(261, 436)
    time.sleep(3)
    
    # 9. 最终确认
    print("[Step 9] Final check...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(3)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v3_final.png'))
    
    print("=== Automation Complete ===")

if __name__ == "__main__":
    main()
