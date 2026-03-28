#!/usr/bin/env python
"""
有道云笔记写入脚本
使用保存的cookies来访问已登录的有道云笔记
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

COOKIES_FILE = Path(__file__).parent.parent / ".cache" / "youdao_cookies.json"

def load_cookies():
    """加载保存的cookies"""
    if not COOKIES_FILE.exists():
        return None
    with open(COOKIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_to_youdao(title: str, content: str, note_url: str = None):
    """写入有道云笔记"""
    cookies = load_cookies()
    if not cookies:
        print("错误: 未找到cookies文件，请先运行 youdao_login.py 登录")
        return False
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # 设置cookies
        context.add_cookies(cookies)
        
        page = context.new_page()
        
        if note_url:
            print(f"正在打开笔记: {note_url}")
            page.goto(note_url)
            page.wait_for_load_state("networkidle")
        else:
            print("正在打开有道云笔记...")
            page.goto("https://note.youdao.com/web/")
            page.wait_for_load_state("networkidle")
        
        # 等待页面加载
        page.wait_for_timeout(2000)
        
        # 截图保存
        screenshot_path = Path(__file__).parent.parent / ".cache" / "youdao_status.png"
        page.screenshot(path=str(screenshot_path))
        print(f"截图已保存: {screenshot_path}")
        
        browser.close()
        return True

def main():
    if len(sys.argv) < 3:
        print("用法: python youdao_writer.py <标题> <内容> [笔记URL]")
        print("示例: python youdao_writer.py '测试笔记' '这是笔记内容' 'https://note.youdao.com/...'")
        sys.exit(1)
    
    title = sys.argv[1]
    content = sys.argv[2]
    note_url = sys.argv[3] if len(sys.argv) > 3 else None
    
    print(f"标题: {title}")
    print(f"内容: {content[:100]}...")
    if note_url:
        print(f"笔记URL: {note_url}")
    
    success = write_to_youdao(title, content, note_url)
    
    if success:
        print("完成！请检查截图查看结果。")
    else:
        print("写入失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
