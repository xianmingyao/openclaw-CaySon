#!/usr/bin/env python3
"""Try to get Douyin data via mobile API / wap site"""
import asyncio
import os
import sys
import re
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'

async def try_mobile():
    from playwright.async_api import async_playwright
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 390, "height": 844},
            locale="zh-CN",
        )
        
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
        page = await context.new_page()
        
        # Try mobile site
        keywords = ["AI技术", "ChatGPT", "人工智能"]
        
        for kw in keywords:
            sys.stderr.write(f"\n=== Mobile: {kw} ===\n")
            try:
                url = f"https://m.douyin.com/search/{kw}"
                resp = await page.goto(url, timeout=30000)
                sys.stderr.write(f"  Status: {resp.status if resp else 'None'}\n")
                
                await asyncio.sleep(8)
                
                text = await page.inner_text("body")
                sys.stderr.write(f"  Text len: {len(text)}\n")
                if len(text) > 100:
                    sys.stderr.write(f"  Preview: {text[:300]}\n")
                
                # Check for captcha
                if "验证" in text or "打开App" in text or "扫码" in text:
                    sys.stderr.write("  BLOCKED by verification\n")
                    
            except Exception as e:
                sys.stderr.write(f"  Error: {e}\n")
            
            await asyncio.sleep(2)
        
        # Also try the wap site
        sys.stderr.write("\n=== Trying wap site ===\n")
        try:
            resp = await page.goto("https://www.douyin.com/wap/search?keyword=AI%E6%8A%80%E6%9C%AF", timeout=30000)
            sys.stderr.write(f"  Status: {resp.status if resp else 'None'}\n")
            await asyncio.sleep(5)
            text = await page.inner_text("body")
            sys.stderr.write(f"  Text len: {len(text)}\n")
            if len(text) > 200:
                # Try to find some text content
                lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 10]
                for line in lines[:10]:
                    sys.stderr.write(f"  {line[:100]}\n")
        except Exception as e:
            sys.stderr.write(f"  Wap error: {e}\n")
        
        await browser.close()
    
    return results

if __name__ == "__main__":
    asyncio.run(try_mobile())
    print("DONE")
