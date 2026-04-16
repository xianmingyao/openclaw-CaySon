"""
QQ音乐自动化脚本 v4 - 处理登录弹窗
打开QQ音乐搜索页面，关闭登录弹窗，播放周杰伦-发如雪
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

def activate_chrome():
    """激活Chrome窗口"""
    try:
        windows = gw.getWindowsWithTitle("Chrome")
        if windows:
            windows[0].activate()
            time.sleep(0.5)
            return True
        return False
    except Exception as e:
        print(f"[warn] Window activation failed: {e}")
        return False

def close_popup():
    """尝试关闭弹窗"""
    # 按ESC尝试关闭弹窗
    pyautogui.press('esc')
    time.sleep(0.5)
    # 点击页面右上角关闭按钮（如果可见）
    pyautogui.click(x=960, y=110)  # 关闭按钮的大致位置
    time.sleep(0.5)

def main():
    print("=== QQ Music Automation Script v4 ===")
    
    # 1. 关闭可能存在的Chrome窗口
    print("[Step 0] Closing existing Chrome windows...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                      capture_output=True, timeout=5)
        time.sleep(1)
    except:
        pass
    
    # 2. 直接打开搜索URL
    print("[Step 1] Opening QQ Music search page...")
    search_url = 'https://y.qq.com/portal/search.html#search=song&key=%E5%8F%91%E5%A6%82%E9%9B%AA'
    subprocess.Popen([CHROME_PATH, '--new-window', search_url])
    time.sleep(6)
    
    activate_chrome()
    screenshot('step1_page_opened')
    
    # 3. 关闭登录弹窗
    print("[Step 2] Closing login popup...")
    close_popup()
    time.sleep(1)
    
    # 如果弹窗还在，尝试按ESC
    pyautogui.press('esc')
    time.sleep(1)
    
    activate_chrome()
    screenshot('step2_popup_closed')
    
    # 4. 确认页面加载完成
    print("[Step 3] Waiting for search results...")
    time.sleep(3)
    
    activate_chrome()
    screenshot('step3_results_ready')
    
    # 5. 点击第一首歌曲
    print("[Step 4] Clicking the first song...")
    pyautogui.click(x=500, y=320)
    time.sleep(1)
    
    screenshot('step4_song_clicked')
    
    # 6. 双击播放
    print("[Step 5] Double-clicking to play...")
    pyautogui.doubleClick(x=500, y=320)
    time.sleep(2)
    
    screenshot('step5_playing')
    
    # 7. 最终确认
    print("[Step 6] Final check...")
    time.sleep(3)
    
    activate_chrome()
    screenshot('step6_final')
    
    print("=== Automation completed! ===")
    print("Check screenshots in:", SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
