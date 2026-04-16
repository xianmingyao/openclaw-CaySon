"""
酷狗音乐自动化脚本 v3 - 解决登录弹窗
使用desktop-control技能搜索并播放周杰伦-发如雪
"""
import pyautogui
import time
import os
import subprocess
import pygetwindow as gw

# 配置PyAutoGUI
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0.1

# 截图保存目录
SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

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

def close_login_popup():
    """关闭登录弹窗"""
    # 方法1: 按ESC
    pyautogui.press('esc')
    time.sleep(0.5)
    
    # 方法2: 点击页面右下角空白处关闭
    pyautogui.click(x=1200, y=700)
    time.sleep(0.3)
    
    # 方法3: 再次按ESC
    pyautogui.press('esc')
    time.sleep(0.5)

def main():
    print("=== KuGou Music Automation Script v3 ===")
    
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
    close_login_popup()
    
    activate_window("Chrome")
    screenshot('step1_after_popup_close')
    
    # 4. 再次尝试关闭弹窗
    print("[Step 3] Verifying popup is closed...")
    pyautogui.press('esc')
    time.sleep(1)
    
    # 点击页面中心位置（如果还有弹窗）
    pyautogui.click(x=640, y=360)
    time.sleep(0.5)
    pyautogui.press('esc')
    time.sleep(1)
    
    activate_window("Chrome")
    screenshot('step2_clean_state')
    
    # 5. 点击搜索框
    print("[Step 4] Clicking search box...")
    # 搜索框在页面顶部
    pyautogui.click(x=350, y=75)
    time.sleep(1)
    
    screenshot('step3_search_focused')
    
    # 6. 输入搜索词
    print("[Step 5] Typing search keywords...")
    pyautogui.typewrite('fa ru xue', interval=0.1)
    time.sleep(0.5)
    
    screenshot('step4_typed')
    
    # 7. 按回车搜索
    print("[Step 6] Pressing Enter to search...")
    pyautogui.press('enter')
    time.sleep(5)
    
    activate_window("Chrome")
    screenshot('step5_search_results')
    
    # 8. 点击第一首歌曲
    print("[Step 7] Clicking first song...")
    pyautogui.click(x=480, y=280)
    time.sleep(1)
    
    screenshot('step6_song_clicked')
    
    # 9. 双击播放
    print("[Step 8] Double-clicking to play...")
    pyautogui.doubleClick(x=480, y=280)
    time.sleep(2)
    
    screenshot('step7_playing')
    
    # 10. 最终确认
    print("[Step 9] Final check...")
    time.sleep(3)
    
    activate_window("Chrome")
    screenshot('step8_final')
    
    print("=== Automation completed! ===")
    print("Check screenshots in:", SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
