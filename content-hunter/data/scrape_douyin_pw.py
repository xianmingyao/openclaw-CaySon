# -*- coding: utf-8 -*-
"""
内容捕手 - 抖音AI技术热门内容抓取脚本 (Playwright版本)
"""
import json
import time
import re
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def scrape_douyin():
    results = []
    
    with sync_playwright() as p:
        # 启动浏览器 - 使用移动端视图
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            viewport={'width': 390, 'height': 844},
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            geolocation={'latitude': 31.2304, 'longitude': 121.4737},
            permissions=['geolocation'],
        )
        
        page = context.new_page()
        
        # 尝试访问抖音搜索页面
        search_url = 'https://www.douyin.com/search/AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD?type=video'
        print('Opening: %s' % search_url)
        
        try:
            response = page.goto(search_url, timeout=30000, wait_until='domcontentloaded')
            print('Status: %s' % response.status)
            time.sleep(5)
            
            # 截图看看
            page.screenshot(path='E:/workspace/content-hunter/data/douyin_pw_check.png', full_page=False)
            print('Screenshot saved')
            
            # 获取页面内容
            content = page.content()
            print('Page content length: %d' % len(content))
            
            # 尝试找视频元素
            video_items = page.query_selector_all('[data-e2e="search-card-vidoe-item"]')
            print('Video items found: %d' % len(video_items))
            
            if not video_items:
                # Try different selectors
                selectors = [
                    '.search-card-video',
                    '[class*="video"]',
                    '.video-item',
                    '[data-e2e*="video"]',
                ]
                for sel in selectors:
                    items = page.query_selector_all(sel)
                    if items:
                        print('Selector "%s": %d items' % (sel, len(items)))
            
        except Exception as e:
            print('Error: %s' % e)
            import traceback
            traceback.print_exc()
        
        browser.close()
    
    return results

if __name__ == '__main__':
    print('=== 抖音 Playwright 抓取测试 ===')
    results = scrape_douyin()
    print('Found %d items' % len(results))
