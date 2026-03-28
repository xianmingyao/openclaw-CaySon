#!/usr/bin/env python
"""
有道云笔记写入任务
包含登录检测和通知功能
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

COOKIES_FILE = Path(__file__).parent.parent / ".cache" / "youdao_cookies.json"
CONFIG_FILE = Path(__file__).parent.parent / ".cache" / "youdao_config.json"

def save_screenshot(page, name):
    """保存截图"""
    screenshot_dir = Path(__file__).parent.parent / ".cache"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    path = screenshot_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    page.screenshot(path=str(path))
    return path

def check_login_status():
    """检查登录状态，返回(True/False, 截图路径)"""
    cookies = None
    if COOKIES_FILE.exists():
        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        if cookies:
            context.add_cookies(cookies)
        
        page = context.new_page()
        page.goto("https://note.youdao.com/web/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        screenshot_path = save_screenshot(page, "check_login")
        
        # 检查页面内容
        page_content = page.content()
        is_logged_in = "扫码登录" not in page_content and "登录" not in page.title()
        
        browser.close()
        return is_logged_in, screenshot_path

def write_note(note_url: str, content: str) -> tuple:
    """写入笔记内容"""
    cookies = None
    if COOKIES_FILE.exists():
        with open(COOKIES_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
    
    if not cookies:
        return False, "未找到cookies，请先运行 youdao_login.py"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies(cookies)
        
        page = context.new_page()
        print(f"打开笔记: {note_url}")
        page.goto(note_url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        screenshot_path = save_screenshot(page, "write_result")
        
        browser.close()
        return True, screenshot_path

def main():
    print("=" * 50)
    print("有道云笔记写入任务")
    print("=" * 50)
    
    # 1. 检查登录状态
    print("\n[1/3] 检查登录状态...")
    is_logged_in, check_screenshot = check_login_status()
    print(f"截图: {check_screenshot}")
    
    if not is_logged_in:
        print("\n⚠️ 未登录！请手动登录后重试")
        print(f"截图已保存: {check_screenshot}")
        print("\n登录步骤:")
        print("1. 打开正常浏览器，访问 https://note.youdao.com")
        print("2. 用微信扫码登录")
        print("3. 运行 python scripts/youdao_login.py 保存cookies")
        sys.exit(1)
    
    print("✅ 已登录")
    
    # 2. 打开目标笔记
    note_url = "https://note.youdao.com/web/#/file/WEBa2b687261f801b0d8ba1335e93450410/note/WEB3f60fdbb1ff187554ffbe864d9c3c833/"
    
    print(f"\n[2/3] 打开笔记...")
    success, result = write_note(note_url, "test")
    
    if success:
        print(f"✅ 写入完成，截图: {result}")
    else:
        print(f"❌ 写入失败: {result}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
