"""
智能音乐自动化脚本 - 完整成功版 v4
增加等待时间，确保点击生效
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
    print("=== Smart Music Automation - FINAL v4 ===")
    
    dc = load_skill().DesktopController()
    
    # 1. 启动QQ音乐
    print("[Step 1] Starting QQMusic...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(8)  # 增加等待时间
    
    # 2. 激活窗口
    print("[Step 2] Activating window...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(1)
    
    # 3. 关闭弹窗
    print("[Step 3] Closing popup...")
    pyautogui.press('esc')
    time.sleep(1)
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    
    # 4. 点击搜索框
    print("[Step 4] Clicking search box...")
    dc.click(242, 22)
    time.sleep(1.5)  # 更多等待时间
    
    # 5. 输入搜索词
    print("[Step 5] Typing 'faruxue'...")
    dc.type_text("faruxue", interval=0.08)
    time.sleep(0.5)
    
    # 6. 按回车搜索
    print("[Step 6] Pressing Enter...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(0.5)
    dc.press("enter")
    time.sleep(6)  # 等待搜索结果加载
    
    # 7. 截图确认搜索结果
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v4_before_click.png'))
    
    # 8. 点击第一首歌（发如雪）- 使用更精确的位置
    print("[Step 7] Clicking first song (发如雪)...")
    # 歌曲名位置，大约在 (300, 436) 附近
    dc.click(300, 436)
    time.sleep(1)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v4_after_single_click.png'))
    
    # 9. 再次点击确保选中
    print("[Step 8] Clicking again to select...")
    dc.click(300, 436)
    time.sleep(0.5)
    
    # 10. 双击播放
    print("[Step 9] Double-clicking to play...")
    dc.double_click(300, 436)
    time.sleep(4)  # 更多等待时间让播放开始
    
    # 11. 最终确认
    print("[Step 10] Final check...")
    dc.activate_window_by_process("QQMusic")
    time.sleep(2)
    dc.screenshot(os.path.join(SCREENSHOT_DIR, 'v4_final.png'))
    
    print("=== Automation Complete ===")

if __name__ == "__main__":
    main()
