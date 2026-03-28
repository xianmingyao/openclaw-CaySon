#!/usr/bin/env python
"""
有道云笔记登录脚本
功能：打开有道云笔记，等待用户手动扫码登录，然后保存cookies供后续使用
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_FILE = Path(__file__).parent.parent / ".cache" / "youdao_cookies.json"

def main():
    with sync_playwright() as p:
        # 启动Chromium浏览器
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("=" * 50)
        print("有道云笔记登录助手")
        print("=" * 50)
        print("正在打开有道云笔记...")
        
        # 打开有道云笔记
        page.goto("https://note.youdao.com/web/")
        page.wait_for_load_state("networkidle")
        
        print("请在打开的浏览器窗口中扫码登录有道云笔记！")
        print("登录成功后，按回车键继续保存cookies...")
        print("-" * 50)
        
        # 等待用户登录 - 检查是否已登录
        while True:
            try:
                # 检查是否有登录状态的元素
                page.wait_for_timeout(1000)
                # 尝试点击某个需要登录才能看到的元素
                title = page.title()
                print(f"当前页面标题: {title}")
                
                # 检查URL是否已跳转到笔记页面
                if "note.youdao.com" in page.url and "login" not in page.url.lower():
                    print("检测到已登录！")
                    break
                    
            except Exception as e:
                pass
            
            user_input = input("已登录请按回车，未登录请在浏览器中扫码登录后按回车: ").strip()
            if user_input == "":
                break
        
        # 保存cookies
        print("正在保存cookies...")
        cookies = context.cookies()
        
        # 确保目录存在
        COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        
        print(f"Cookies已保存到: {COOKIES_FILE}")
        print(f"共保存 {len(cookies)} 个cookie")
        
        # 显示一些cookie信息
        domain_cookies = {}
        for c in cookies:
            domain = c.get("domain", "unknown")
            if domain not in domain_cookies:
                domain_cookies[domain] = []
            domain_cookies[domain].append(c["name"])
        
        print("\n保存的Cookie域名:")
        for domain, names in domain_cookies.items():
            print(f"  {domain}: {', '.join(names[:5])}{'...' if len(names) > 5 else ''}")
        
        print("\n" + "=" * 50)
        print("登录完成！现在可以用保存的cookies来操作有道云笔记了。")
        print("=" * 50)
        
        browser.close()

if __name__ == "__main__":
    main()
