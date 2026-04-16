"""
QQ音乐自动化脚本 - 使用desktop-control技能
打开QQ音乐网页版，搜索周杰伦-发如雪并播放
"""
import pyautogui
import time
import os
import sys

# 配置PyAutoGUI
pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0.1

# 截图保存目录
SCREENSHOT_DIR = r'E:\workspace\scripts\screenshots'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def screenshot(name):
    """保存截图"""
    path = os.path.join(SCREENSHOT_DIR, f'{name}.png')
    pyautogui.screenshot(path)
    print(f"[screenshot] {path}")
    return path

def main():
    print("=== QQ Music Automation Script ===")
    
    # 1. 打开Chrome浏览器
    print("[Step 1] Opening Chrome browser...")
    pyautogui.hotkey('win', 'r')
    time.sleep(1)
    pyautogui.typewrite('chrome.exe', interval=0.1)
    pyautogui.press('enter')
    time.sleep(4)  # Wait for browser
    
    # 2. 访问QQ音乐网页版
    print("[Step 2] Visiting QQ Music website...")
    pyautogui.typewrite('https://y.qq.com', interval=0.05)
    pyautogui.press('enter')
    time.sleep(5)  # Wait for page load
    
    screenshot('step1_qqmusic_home')
    
    # 3. 等待页面加载完成后，点击搜索框
    print("[Step 3] Focusing search box...")
    
    # 按Tab键尝试聚焦到搜索框
    for _ in range(3):
        pyautogui.press('tab')
        time.sleep(0.3)
    
    time.sleep(1)
    
    # 4. 输入搜索关键词
    print("[Step 4] Typing search keywords...")
    pyautogui.typewrite('zhou guo lun fa ru xue', interval=0.1)
    time.sleep(0.5)
    
    # 5. 按回车搜索
    print("[Step 5] Searching...")
    pyautogui.press('enter')
    time.sleep(4)  # Wait for results
    
    screenshot('step2_search_results')
    
    # 6. 在搜索结果中找到并点击歌曲
    print("[Step 6] Clicking the song to play...")
    pyautogui.click(x=600, y=400)
    time.sleep(2)
    
    screenshot('step3_playing')
    
    print("=== Automation completed! ===")
    print("Tip: If the song didn't play correctly, please check screenshots and adjust coordinates.")

if __name__ == "__main__":
    main()
