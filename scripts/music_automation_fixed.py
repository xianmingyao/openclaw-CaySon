"""
智能音乐自动化脚本 - 使用修复后的 desktop-control 技能
优先使用桌面端，修复了窗口激活和焦点问题
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
CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

# 动态加载 desktop-control 技能
def load_desktop_control():
    """动态加载desktop-control技能"""
    skill_path = r'E:\workspace\skills\desktop-control-1-0-0\__init__.py'
    spec = importlib.util.spec_from_file_location("desktop_control", skill_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["desktop_control"] = module
    spec.loader.exec_module(module)
    return module

# 加载技能
print("[LOAD] Loading desktop-control skill...")
dc_module = load_desktop_control()
DesktopController = dc_module.DesktopController

def main():
    print("=== Smart Music Automation with Fixed Desktop Control ===")
    
    # 初始化控制器
    dc = DesktopController(failsafe=True)
    
    # 检测桌面端
    desktop_exists = os.path.exists(DESKTOP_APP_PATH)
    print(f"[CHECK] Desktop app exists: {desktop_exists}")
    
    if desktop_exists:
        print("[MODE] Using QQMusic Desktop App")
        
        # 1. 启动QQ音乐
        print("[Step 1] Starting QQMusic...")
        subprocess.Popen([DESKTOP_APP_PATH])
        time.sleep(6)
        
        # 2. 使用新方法激活窗口（通过进程名，更可靠）
        print("[Step 2] Activating QQMusic window by process...")
        dc.activate_window_by_process("QQMusic")
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'step1_started.png'))
        
        # 3. 关闭弹窗
        print("[Step 3] Closing popup...")
        pyautogui.press('esc')
        time.sleep(0.5)
        dc.activate_window_by_process("QQMusic")
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'step2_popup_closed.png'))
        
        # 4. 使用 click_verify_focus 确保搜索框获得焦点
        print("[Step 4] Clicking search box with focus verification...")
        success = dc.click_verify_focus(
            x=420, y=45,  # 搜索框坐标
            expected_window_part="QQMusic",  # 验证窗口
            max_retries=3,
            retry_delay_ms=500
        )
        print(f"[DEBUG] Focus verified: {success}")
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'step3_search_focused.png'))
        
        # 5. 输入搜索词
        print("[Step 5] Typing search keywords...")
        dc.type_text("faruxue", interval=0.08)
        time.sleep(0.5)
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'step4_typed.png'))
        
        # 6. 按回车搜索
        print("[Step 6] Pressing Enter to search...")
        dc.activate_window_by_process("QQMusic")
        dc.press("enter")
        time.sleep(4)
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'step5_search_results.png'))
        
        # 7. 点击第一首歌曲
        print("[Step 7] Clicking first song...")
        dc.click_verify_focus(
            x=550, y=220,
            expected_window_part="QQMusic",
            max_retries=2
        )
        dc.click(550, 220)
        time.sleep(1)
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'step6_song_clicked.png'))
        
        # 8. 双击播放
        print("[Step 8] Double-clicking to play...")
        dc.double_click(550, 220)
        time.sleep(2)
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'step7_playing.png'))
        
        # 9. 最终确认
        print("[Step 9] Final check...")
        dc.activate_window_by_process("QQMusic")
        time.sleep(3)
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'step8_final.png'))
        
    else:
        print("[MODE] Using Web Version (Chrome)")
        
        # 关闭Chrome
        try:
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                         capture_output=True, timeout=5)
            time.sleep(1)
        except:
            pass
        
        # 打开酷狗
        print("[Step 1] Opening KuGou...")
        subprocess.Popen([CHROME_PATH, '--new-window', 'https://www.kugou.com/'])
        time.sleep(6)
        
        dc.activate_window("Chrome")
        pyautogui.press('esc')
        time.sleep(1)
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'web_step1.png'))
        
        # 搜索
        print("[Step 2] Searching...")
        dc.click_verify_focus(x=350, y=75, expected_window_part="kugou", max_retries=3)
        dc.type_text("fa ru xue", interval=0.08)
        time.sleep(0.5)
        dc.press("enter")
        time.sleep(4)
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'web_step2_results.png'))
        
        # 点击播放
        print("[Step 3] Playing...")
        dc.click(480, 280)
        time.sleep(1)
        dc.double_click(480, 280)
        time.sleep(2)
        dc.screenshot(os.path.join(SCREENSHOT_DIR, 'web_step3_playing.png'))
    
    print("=== Automation Complete ===")
    print(f"Screenshots saved to: {SCREENSHOT_DIR}")

if __name__ == "__main__":
    main()
