#!/usr/bin/env python3
"""打开QQ音乐并搜索播放发如雪"""
import subprocess
import time
import pyautogui
import sys
import io

# 解决Windows控制台GBK编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置
SEARCH_KEYWORD = "发如雪"
APP_NAME = "qqmusic"
SEARCH_KEYWORD_CN = "QQ音乐"

def open_app_with_retry(app_name, search_keyword, max_retries=3):
    """智能打开应用，支持快捷方式搜索"""
    for attempt in range(max_retries):
        print(f"[尝试 {attempt+1}/{max_retries}] 正在打开 {search_keyword}...")
        
        # 方法1: 直接启动进程
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"Start-Process '{search_keyword}'"],
                capture_output=True, text=True, timeout=10
            )
            print(f"[OK] 启动命令已执行")
        except Exception as e:
            print(f"[WARN] 启动命令失败: {e}")
        
        time.sleep(3)  # 等待窗口打开
        
        # 检查进程是否运行
        result = subprocess.run(
            ["powershell", "-Command", f"Get-Process | Where-Object {{$_.ProcessName -like '*{app_name}*'}}"],
            capture_output=True, text=True
        )
        
        if result.stdout.strip():
            print(f"[OK] {search_keyword} 已启动!")
            return True
        
        print(f"[RETRY] 应用未启动，重试...")
        time.sleep(2)
    
    return False

def main():
    print("=" * 50)
    print("🎵 QQ音乐自动化 - 搜索并播放发如雪")
    print("=" * 50)
    
    # Step 1: 打开QQ音乐
    print("\n[Step 1] 打开QQ音乐...")
    if not open_app_with_retry(APP_NAME, SEARCH_KEYWORD_CN):
        print("[FAIL] 无法打开QQ音乐，请手动打开后按回车继续...")
        input()
    
    # 等待应用完全加载
    print("[INFO] 等待窗口加载...")
    time.sleep(3)
    
    # Step 2: 点击搜索框
    print("\n[Step 2] 点击搜索框...")
    # 尝试在右侧区域找到搜索图标/输入框
    # QQ音乐界面通常在右上角有搜索图标
    try:
        # 尝试点击搜索图标 (放大镜图标的大致位置)
        search_icon_x, search_icon_y = 1200, 35  # 这个坐标需要根据实际屏幕调整
        pyautogui.click(search_icon_x, search_icon_y)
        print(f"[OK] 点击搜索框位置 ({search_icon_x}, {search_icon_y})")
        time.sleep(0.5)
    except Exception as e:
        print(f"[WARN] 点击搜索框失败: {e}")
    
    # Step 3: 输入搜索关键词
    print(f"\n[Step 3] 输入搜索关键词: {SEARCH_KEYWORD}")
    pyautogui.typewrite(SEARCH_KEYWORD, interval=0.1)
    time.sleep(0.3)
    pyautogui.press('enter')
    print("[OK] 按下回车搜索")
    
    # 等待搜索结果
    print("[INFO] 等待搜索结果...")
    time.sleep(2)
    
    # Step 4: 点击播放
    print("\n[Step 4] 点击播放按钮...")
    try:
        # 搜索结果中的播放按钮位置
        play_x, play_y = 180, 280  # 这个坐标需要根据实际界面调整
        pyautogui.click(play_x, play_y)
        print(f"[OK] 点击播放按钮 ({play_x}, {play_y})")
    except Exception as e:
        print(f"[WARN] 点击播放按钮失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎵 操作完成!")
    print("=" * 50)

if __name__ == "__main__":
    main()
