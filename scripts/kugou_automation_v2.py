"""
酷狗音乐自动化脚本 v2 - 直接URL搜索
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

def main():
    print("=== KuGou Music Automation Script v2 ===")
    
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
    screenshot('step1_homepage')
    
    # 3. 关闭可能存在的弹窗
    print("[Step 2] Closing popup if exists...")
    pyautogui.press('esc')
    time.sleep(0.5)
    
    activate_window("Chrome")
    screenshot('step2_popup_closed')
    
    # 4. 点击搜索框
    print("[Step 3] Clicking search box...")
    # 酷狗首页搜索框位置
    pyautogui.click(x=400, y=80)
    time.sleep(1)
    
    screenshot('step3_search_focused')
    
    # 5. 输入搜索词
    print("[Step 4] Typing search keywords...")
    pyautogui.typewrite('faru xue', interval=0.1)  # 用拼音
    time.sleep(0.5)
    
    screenshot('step4_typed')
    
    # 6. 按回车搜索
    print("[Step 5] Pressing Enter to search...")
    pyautogui.press('enter')
    time.sleep(5)
    
    activate_window("Chrome")
    screenshot('step5_search_done')
    
    # 7. 点击第一首歌曲
    print("[Step 6] Clicking first song...")
    # 搜索结果页面的第一首歌
    pyautogui.click(x=480, y=280)
    time.sleep(1)
    
    screenshot('step6_song_clicked')
    
    # 8. 双击播放
    print("[Step 7] Double-clicking to play...")
    pyautogui.doubleClick(x=480, y=280)
    time.sleep(2)
    
    screenshot('step7_playing')
    
    # 9. 最终确认
    print("[Step 8] Final check...")
    time.sleep(3)
    
    activate_window("Chrome")
    screenshot('step8_final')
    
    print("=== Automation completed! ===")
    print("Check screenshots in:", SCREENSHOT_DIR)

if __name__ == "__main__":
    main()
