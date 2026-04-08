# -*- coding: utf-8 -*-
"""
尝试多种方式获取抖音数据
"""
import requests
import json
import re
import time
from bs4 import BeautifulSoup

def try_douyin_api():
    """尝试抖音移动版API"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'https://www.douyin.com/',
        'Cookie': ''
    }
    
    keywords = ['AI人工智能', 'ChatGPT', '大模型', 'AIGC']
    results = []
    seen = set()
    
    for kw in keywords:
        # 尝试移动端搜索
        url = f'https://m.douyin.com/search/{kw}'
        try:
            r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            print(f'移动端douyin: {r.status_code} -> {r.url[:60]}')
            
            # 检查是否被重定向到验证页
            if 'verify' in r.url.lower() or 'captcha' in r.url.lower():
                print(f'  被重定向到验证页')
                continue
                
            # 解析HTML中的数据
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # 尝试找script标签中的JSON数据
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'aweme_id' in script.string:
                    try:
                        # 提取JSON数据块
                        match = re.search(r'\{[^{}]*\"aweme_id\"[^{}]*\}', script.string)
                        if match:
                            data = json.loads(match.group())
                            print(f'  Found data: {data.get("desc", "")[:50]}')
                    except:
                        pass
            
            # 从HTML文本中提取视频信息
            ids = re.findall(r'"aweme_id"\s*:\s*"(\d+)"', r.text)
            titles = re.findall(r'"desc"\s*:\s*"([^"]{5,100})"', r.text)
            authors = re.findall(r'"nickname"\s*:\s*"([^"]+)"', r.text)
            diggs = re.findall(r'"digg_count"\s*:\s*(\d+)', r.text)
            
            print(f'  IDs:{len(ids)}, titles:{len(titles)}, authors:{len(authors)}, diggs:{len(diggs)}')
            
            for i, vid in enumerate(ids[:20]):
                if vid not in seen:
                    seen.add(vid)
                    title = titles[i] if i < len(titles) else ''
                    author = authors[i] if i < len(authors) else ''
                    digg = diggs[i] if i < len(diggs) else '0'
                    results.append({
                        'id': vid,
                        'title': title,
                        'author': author,
                        'digg': digg,
                        'url': f'https://www.douyin.com/video/{vid}'
                    })
                    
        except Exception as e:
            print(f'  Error: {e}')
        time.sleep(2)
    
    return results

def try_toutiao_pc():
    """尝试PC版头条搜索"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://www.toutiao.com/',
        'Accept': 'text/html,application/xhtml+xml,*/*',
    }
    
    keywords = ['AI人工智能 抖音', 'ChatGPT 教程 抖音', '大模型 技术 抖音']
    results = []
    seen = set()
    
    for kw in keywords:
        url = f'https://www.toutiao.com/search/?keyword={kw}'
        try:
            r = requests.get(url, headers=headers, timeout=15)
            print(f'头条PC: {kw[:15]}... -> {r.status_code}')
            
            # 提取头条号的抖音视频
            ids = re.findall(r'douyin\.com/video/(\d+)', r.text)
            titles = re.findall(r'"title"\s*:\s*"([^"]{10,100})"', r.text)
            
            print(f'  找到 IDs:{len(ids)}, titles:{len(titles)}')
            
            for i, vid in enumerate(ids[:10]):
                if vid not in seen:
                    seen.add(vid)
                    results.append({
                        'id': vid,
                        'title': titles[i] if i < len(titles) else '',
                        'author': '',
                        'digg': '0',
                        'url': f'https://www.douyin.com/video/{vid}'
                    })
        except Exception as e:
            print(f'  Error: {e}')
        time.sleep(1)
    
    return results

# 综合尝试
print("=== 尝试抖音移动端 ===")
r1 = try_douyin_api()
print(f"抖音移动端获取: {len(r1)} 条")

print("\n=== 尝试头条PC搜索 ===")
r2 = try_toutiao_pc()
print(f"头条PC搜索获取: {len(r2)} 条")

# 合并去重
all_data = r1 + r2
seen_ids = set()
unique_data = []
for item in all_data:
    if item['id'] not in seen_ids:
        seen_ids.add(item['id'])
        unique_data.append(item)

print(f"\n总计去重后: {len(unique_data)} 条")

if unique_data:
    with open('E:/workspace/content-hunter/data/douyin_raw.json', 'w', encoding='utf-8') as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=2)
    print("已保存到 douyin_raw.json")
else:
    print("未能获取到抖音数据，将使用备选方案")
