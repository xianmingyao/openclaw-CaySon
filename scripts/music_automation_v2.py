"""
智能音乐自动化脚本 v2 - 使用desktop-control技能
优先使用桌面端应用，优化搜索逻辑
"""
import pyautogui
import time
import os
import subprocess
import sys
import pygetwindow as gw

# 配置PyAutoGUI
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0.1

# 截图保存目录
SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 桌面端应用路径
DESKTOP_APP_PATH = r'E:\Program Files\Tencent\QQMusic\QQMusic.exe'
CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

def screenshot(name):
    """保存截图"""
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    pyautogui.screenshot(path)
    print(f"[screenshot] {path}")
    return path

def activate_window(title_part):
    """激活窗口"""
    try:
        windows = gw.getWindowsWithTitle(title_part)
        if windows:
            windows[0].activate()
            time.sleep(0.5)
            return True
        return False
    except Exception as e:
        print(f"[warn] Window activation failed: {e}")
        return False

def check_desktop_app():
    """检测桌面端应用是否存在"""
    return os.path.exists(DESKTOP_APP_PATH)

def close_popup():
    """关闭弹窗"""
    pyautogui.press('esc')
    time.sleep(0.3)
    pyautogui.press('esc')
    time.sleep(0.3)

def search_and_play_desktop():
    """使用桌面端进行搜索和播放"""
    print("=== Using Desktop App (QQMusic) ===")
    
    # 1. 启动QQ音乐桌面端
    print("[Step 1] Starting QQMusic desktop app...")
    subprocess.Popen([DESKTOP_APP_PATH])
    time.sleep(8)  # 等待应用启动
    
    activate_window("QQMusic")
    screenshot('desktop_step1_app_started')
    
    # 2. 关闭可能存在的弹窗
    print("[Step 2] Closing popup...")
    close_popup()
    time.sleep(1)
    
    activate_window("QQMusic")
    screenshot('desktop_step2_popup_closed')
    
    # 3. 点击搜索框 - QQ音乐桌面端的搜索框在顶部居中
    print("[Step 3] Clicking search box...")
    # QQ音乐界面，搜索框通常在顶部logo旁边
    pyautogui.click(x=500, y=35)
    time.sleep(1)
    
    screenshot('desktop_step3_search_focused')
    
    # 4. 输入搜索词
    print("[Step 4] Typing search keywords...")
    pyautogui.typewrite('fa ru xue', interval=0.1)
    time.sleep(0.5)
    
    screenshot('desktop_step4_typed')
    
    # 5. 按回车搜索
    print("[Step 5] Pressing Enter to search...")
    pyautogui.press('enter')
    time.sleep(4)
    
    activate_window("QQMusic")
    screenshot('desktop_step5_search_results')
    
    # 6. 点击搜索结果中的歌曲（第一首）
    print("[Step 6] Clicking first song in results...")
    # 搜索结果页面的第一首歌位置
    pyautogui.click(x=550, y=200)
    time.sleep(1)
    
    screenshot('desktop_step6_song_clicked')
    
    # 7. 双击播放
    print("[Step 7] Double-clicking to play...")
    pyautogui.doubleClick(x=550, y=200)
    time.sleep(2)
    
    screenshot('desktop_step7_playing')
    
    # 8. 最终确认
    print("[Step 8] Final check...")
    time.sleep(3)
    
    activate_window("QQMusic")
    screenshot('desktop_step8_final')

def search_and_play_web():
    """使用网页版进行搜索和播放"""
    print("=== Using Web Version (KuGou) ===")
    
    # 1. 关闭可能存在的Chrome窗口
    print("[Step 0] Closing existing Chrome windows...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      capture_output=True, timeout=5)
        time.sleep(1)
    except:
        pass
    
    # 2. 打开酷狗音乐主页
    print("[Step 1] Opening KuGou homepage...")
    subprocess.Popen([CHROME_PATH, '--new-window', 'https://www.kugou.com/'])
    time.sleep(6)
    
    activate_window("Chrome")
    
    # 3. 关闭登录弹窗
    print("[Step 2] Closing login popup...")
    close_popup()
    time.sleep(1)
    
    activate_window("Chrome")
    screenshot('web_step1_popup_closed')
    
    # 4. 点击搜索框
    print("[Step 3] Clicking search box...")
    pyautogui.click(x=350, y=75)
    time.sleep(1)
    
    screenshot('web_step2_search_focused')
    
    # 5. 输入搜索词
    print("[Step 4] Typing search keywords...")
    pyautogui.typewrite('fa ru xue', interval=0.1)
    time.sleep(0.5)
    
    screenshot('web_step3_typed')
    
    # 6. 按回车搜索
    print("[Step 5] Pressing Enter to search...")
    pyautogui.press('enter')
    time.sleep(5)
    
    activate_window("Chrome")
    screenshot('web_step4_search_results')
    
    # 7. 点击第一首歌曲
    print("[Step 6] Clicking first song...")
    pyautogui.click(x=480, y=280)
    time.sleep(1)
    
    screenshot('web_step5_song_clicked')
    
    # 8. 双击播放
    print("[Step 7] Double-clicking to play...")
    pyautogui.doubleClick(x=480, y=280)
    time.sleep(2)
    
    screenshot('web_step6_playing')
    
    # 9. 最终确认
    print("[Step 8] Final check...")
    time.sleep(3)
    
    activate_window("Chrome")
    screenshot('web_step7_final')

def main():
    print("=== Smart Music Automation v2 ===")
    print(f"Checking for desktop app: {DESKTOP_APP_PATH}")
    
    if check_desktop_app():
        print("[OK] Desktop app found! Will use desktop version.")
        search_and_play_desktop()
    else:
        print("[WARN] Desktop app not found. Using web version.")
        search_and_play_web()
    
    print("=== Automation completed! ===")
    print("Check screenshots in:", SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
