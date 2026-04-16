"""
智能音乐自动化脚本 v7 - 使用正确坐标
使用修复后的 desktop-control 技能
"""
import pyautogui
import time
import os
import subprocess
import sys
import importlib.util

# 截图保存目录
SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 桌面端应用路径
DESKTOP_APP_PATH = r'E:\Program Files\Tencent\QQMusic\QQMusic.exe'

# 动态加载技能
def load_skill():
    spec = importlib.util.spec_from_file_location("dc", 
        r'E:\workspace\skills\desktop-control-1-0-0\__init__.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules["dc"] = module
    spec.loader.exec_module(module)
    return module

def main():
    print("=== Smart Music Automation v7 (Correct Coordinates) ===")
    
    dc = load_skill().DesktopController()
    
    print(f"[CHECK] Desktop app exists: {os.path.exists(DESKTOP_APP_PATH)}")
    
    # 1. 启动QQ音乐
    print("[Step 1] Starting QQMusic...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(6)
    
    # 2. 激活窗口
    print("[Step 2] Activating QQMusic window...")
    dc.activate_window_by_process("QQMusic")
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v7_step1_started.png'))
    
    # 3. 关闭弹窗
    print("[Step 3] Closing popup...")
    pyautogui.press('esc')
    time.sleep(0.5)
    dc.activate_window_by_process("QQMusic")
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v7_step2_popup_closed.png'))
    
    # 4. 点击搜索框 - 使用正确的坐标 (1338, 160)
    print("[Step 4] Clicking search box at (1338, 160)...")
    dc.click(1338, 160)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v7_step3_search_clicked.png'))
    
    # 5. 验证搜索框获得焦点
    print("[Step 5] Verifying search box focus...")
    time.sleep(0.5)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v7_step4_focused.png'))
    
    # 6. 输入搜索词
    print("[Step 6] Typing search keywords...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v7_step5_typed.png'))
    
    # 7. 按回车搜索
    print("[Step 7] Pressing Enter to search...")
    dc.activate_window_by_process("QQMusic")
    dc.press("enter")
    time.sleep(4)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v7_step6_search_results.png'))
    
    # 8. 点击第一首歌曲
    print("[Step 8] Clicking first song...")
    # 搜索结果页面的歌曲位置（需要根据实际结果调整）
    dc.click(650, 280)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v7_step7_song_clicked.png'))
    
    # 9. 双击播放
    print("[Step 9] Double-clicking to play...")
    dc.double_click(650, 280)
    time.sleep(2)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v7_step8_playing.png'))
    
    # 10. 最终确认
    print("[Step 10] Final check...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(3)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v7_step9_final.png'))
    
    print("=== Automation Complete ===")
    print(f"Screenshots: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    main()
