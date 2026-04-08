# -*- coding: utf-8 -*-
import requests
import re
import json
import sys
import time
import random
sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://www.douyin.com/',
})

# Try the aweme API
url = 'https://www.douyin.com/aweme/v1/web/search/item/'
params = {
    'keyword': 'AI人工智能技术',
    'offset': 0,
    'count': 20,
    'device_platform': 'webapp',
    'aid': '6383',
    'channel': 'channel_pc_web',
    'search_source': 'normal_search',
    'query_correct_type': '1',
}
try:
    resp = session.get(url, params=params, timeout=10)
    print('Status: %d' % resp.status_code)
    print('Response length: %d' % len(resp.text))
    if resp.status_code == 200:
        data = resp.json()
        print('Code: %s' % data.get('code'))
        print('Message: %s' % data.get('message'))
        if data.get('data'):
            print('Items: %d' % len(data['data']))
except Exception as e:
    print('Error: %s' % e)

# Try toutiao video search
print('\n--- Trying toutiao video search ---')
try:
    url2 = 'https://so.toutiao.com/c/search/search'
    params2 = {
        'keyword': 'AI人工智能技术 抖音',
        'pd': 'video',
        'source': 'input',
    }
    resp2 = session.get(url2, params=params2, timeout=10)
    print('Toutiao Status: %d' % resp2.status_code)
    print('Toutiao Length: %d' % len(resp2.text))
except Exception as e:
    print('Toutiao Error: %s' % e)
