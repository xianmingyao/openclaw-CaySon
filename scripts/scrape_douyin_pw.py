#!/usr/bin/env python3
"""Scrape Douyin AI tech content using Playwright - Enhanced"""
import asyncio
import os
import sys
import json
import re
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'

async def scrape_douyin():
    from playwright.async_api import async_playwright
    
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        
        # Stealth: remove webdriver flag
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        """)
        
        page = await context.new_page()
        
        keywords = ["AI技术", "ChatGPT", "人工智能大模型", "LLM大语言模型"]
        
        for kw in keywords:
            sys.stderr.write(f"\n=== {kw} ===\n")
            try:
                url = f"https://www.douyin.com/search/{kw}?type=video"
                
                # Wait for the dynamic content
                response = await page.goto(url, timeout=45000)
                sys.stderr.write(f"  Status: {response.status if response else 'None'}\n")
                
                # Wait for content to load
                try:
                    await page.wait_for_selector('[class*="video"]', timeout=15000)
                    sys.stderr.write("  Video container found\n")
                except:
                    sys.stderr.write("  No video container found\n")
                
                # Wait more for JS
                await asyncio.sleep(5)
                
                # Get page text content as fallback
                text = await page.inner_text("body")
                sys.stderr.write(f"  Body text length: {len(text)}\n")
                
                # Extract hashtags
                hashtags = re.findall(r'#([^#\s]{2,20})', text)
                sys.stderr.write(f"  Hashtags found: {len(set(hashtags))}\n")
                
                # Try to find search result items
                try:
                    # Look for list items
                    items = await page.query_selector_all('ul li')
                    sys.stderr.write(f"  LI items: {len(items)}\n")
                except:
                    items = []
                
                # Try evaluating JS to get data
                try:
                    data = await page.evaluate("""
                        () => {
                            // Try to find data in page
                            const scripts = document.querySelectorAll('script');
                            let data = [];
                            scripts.forEach(s => {
                                try {
                                    const text = s.textContent;
                                    if (text.includes('aweme_id') || text.includes('video')) {
                                        data.push(text.substring(0, 500));
                                    }
                                } catch(e) {}
                            });
                            return { scripts: data.length, text: document.body.innerText.substring(0, 1000) };
                        }
                    """)
                    sys.stderr.write(f"  JS eval: {data.get('scripts', 0)} relevant scripts\n")
                except Exception as e:
                    sys.stderr.write(f"  JS eval error: {e}\n")
                
                # If page is blocked, check for verification
                page_text = await page.inner_text("body")
                if "验证" in page_text or "验证码" in page_text:
                    sys.stderr.write("  CAPTCHA detected!\n")
                
            except Exception as e:
                sys.stderr.write(f"  Error: {e}\n")
            
            await asyncio.sleep(3)
        
        await browser.close()
    
    return results

async def main():
    sys.stderr.write("Starting enhanced Playwright Douyin scraper...\n")
    await scrape_douyin()
    print("DONE")

if __name__ == "__main__":
    asyncio.run(main())
