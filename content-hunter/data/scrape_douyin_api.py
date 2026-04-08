# -*- coding: utf-8 -*-
"""
内容捕手 - 抖音AI技术热门内容抓取脚本
尝试多种方式获取数据
"""
import requests
import json
import time
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()

# 尝试多个UA
ua_mobile = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
ua_pc = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

session.headers.update({
    'User-Agent': ua_mobile,
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.douyin.com/',
})

def try_search_api(keyword, offset=0, count=20):
    """尝试抖音搜索API"""
    # 方法1: 移动端API
    apis = [
        # 移动端搜索API
        ('https://m.douyin.com/search/%s?type=video' % keyword, 'mobile_page'),
        # API v1
        ('https://www.douyin.com/aweme/v1/web/search/item/?keyword=%s&count=%d&offset=%d' % (keyword, count, offset), 'api_v1'),
    ]
    
    for url, method in apis:
        try:
            resp = session.get(url, timeout=15)
            print('  Method: %s, Status: %d, Length: %d' % (method, resp.status_code, len(resp.content)))
            if resp.status_code == 200 and resp.content:
                try:
                    data = resp.json()
                    print('  JSON keys: %s' % list(data.keys())[:5])
                    return data
                except:
                    # Try to find JSON in content
                    text = resp.text
                    match = re.search(r'\{.*\}', text, re.DOTALL)
                    if match:
                        try:
                            return json.loads(match.group())
                        except:
                            pass
        except Exception as e:
            print('  Error: %s' % e)
    return None

# 测试搜索
keywords = ['AI人工智能', 'ChatGPT技巧', 'AI工具']
for kw in keywords:
    print('\n=== 搜索: %s ===' % kw)
    result = try_search_api(kw)
    time.sleep(2)
