# -*- coding: utf-8 -*-
"""
抖音搜索API尝试
"""
import requests
import re
import sys
import time
import random
import json

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()

def get_headers():
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    return {
        'User-Agent': ua,
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.douyin.com/',
        'Cookie': 'ttwid=1%7CxXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX; s_v_web_id=verify_xxxxxxxxxxxx; passport_csrf_token=xxxxxxxxxx;',
    }

# 测试多个抖音API端点
endpoints = [
    # 搜索接口
    ('https://www.douyin.com/aweme/v1/web/search/item/?keyword=AI&count=20&offset=0', 'search1'),
    ('https://www.douyin.com/aweme/v1/web/general/search/single/?keyword=AI&count=20&search_channel=aweme_video_web', 'search2'),
    # 热搜接口
    ('https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383', 'hot'),
    # 推荐接口
    ('https://www.douyin.com/aweme/v1/web/tab/feed/?device_platform=webapp&aid=6383', 'feed'),
    # 搜索接口2
    ('https://search-api-nebula-sg.xgcdn.com/api/v3/search/video?keyword=AI&offset=0&count=20', 'search3'),
]

for url, name in endpoints:
    print('\n=== 测试: %s ===' % name)
    print('URL: %s' % url[:80])
    try:
        resp = session.get(url, headers=get_headers(), timeout=10)
        print('状态码: %d' % resp.status_code)
        print('响应大小: %d bytes' % len(resp.content))
        if resp.status_code == 200:
            try:
                data = resp.json()
                print('JSON解析成功: %s' % str(data)[:200])
            except:
                text = resp.text
                print('响应内容: %s' % text[:300])
                # 检查是否是重定向
                if 'captcha' in text.lower() or 'verify' in text.lower():
                    print('  -> 检测到验证码页面!')
    except Exception as e:
        print('异常: %s' % e)
    time.sleep(1)
