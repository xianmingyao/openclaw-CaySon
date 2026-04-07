#!/usr/bin/env python3
"""内容捕手 - 本次任务抓取抖音+B站各100条AI热门内容"""
import urllib.request
import urllib.parse
import json
import time
import random
import re
import os

# ========== 1. 抓取抖音 ==========
def scrape_douyin(keyword="AI人工智能", target_count=100):
    results = []
    cursor = 0
    
    while len(results) < target_count:
        url = 'https://www.douyin.com/aweme/v1/web/search/item/?' + urllib.parse.urlencode({
            'keyword': keyword,
            'count': '20',
            'offset': str(cursor),
            'device_platform': 'webapp',
            'aid': '6383',
            'channel': 'channel_pc_web',
            'search_channel': 'aweme_video_web',
            'sort_type': '0',
            'publish_time': '0',
            'source': 'normal_search',
            'pc_client_type': '1',
            'version_code': '190600',
            'version_name': '19.6.0',
            'cookie_enabled': 'true',
            'screen_width': '1920',
            'screen_height': '1080',
            'browser_language': 'zh-CN',
            'browser_platform': 'Win32',
            'browser_name': 'Chrome',
            'browser_version': '120.0.0.0',
        })
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.douyin.com/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=15)
            raw = resp.read().decode('utf-8')
            data = json.loads(raw)
            
            status = data.get('status_code', -1)
            has_more = data.get('has_more', 0)
            items = data.get('data', [])
            
            print(f'抖音 Offset {cursor}: status={status}, has_more={has_more}, items={len(items)}')
            
            if not items:
                print('  -> 空结果，停止')
                break
            
            for item in items:
                aweme = item.get('aweme_info', {}) or item
                video_desc = aweme.get('desc', '')
                author = aweme.get('author', {}).get('nickname', '')
                digg_count = aweme.get('statistics', {}).get('digg_count', 0)
                share_url = aweme.get('share_url', '')
                aweme_id = aweme.get('aweme_id', '')
                tags = re.findall(r'#(\w+)', video_desc)
                
                results.append({
                    'title': video_desc or '无标题',
                    'author': author,
                    'likes': digg_count,
                    'tags': ' '.join([f'#{t}' for t in tags[:5]]),
                    'url': share_url or f'https://www.douyin.com/video/{aweme_id}',
                })
            
            if not has_more:
                print('  -> 没有更多结果')
                break
                
            cursor += 20
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f'抖音 Offset {cursor} 失败: {e}')
            break
    
    return results

# ========== 2. 抓取B站 ==========
def scrape_bilibili(keyword="AI人工智能", target_count=100, pagesize=20):
    results = []
    page = 1
    max_pages = 50
    consecutive_fail = 0
    max_consecutive_fail = 3
    
    while len(results) < target_count and page <= max_pages:
        url = f'https://api.bilibili.com/x/web-interface/search/type?keyword={urllib.parse.quote(keyword)}&search_type=video&order=hot&page={page}&pagesize={pagesize}&platform=web'
        
        headers = {
            'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(115, 125)}.0.0.{random.randint(0, 9)} Safari/537.36',
            'Referer': 'https://search.bilibili.com/',
            'Origin': 'https://search.bilibili.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read().decode('utf-8'))
            
            if data.get('code') == 0:
                results_raw = data.get('data', {}).get('result', [])
                if not results_raw:
                    print(f'B站 第{page}页: 空结果，停止')
                    break
                    
                consecutive_fail = 0
                print(f'B站 第{page}页: 获得 {len(results_raw)} 条 (累计{len(results)})')
                
                for r in results_raw:
                    title = r.get('title', '').replace('<em class="keyword">', '').replace('</em>', '')
                    results.append({
                        'title': title,
                        'author': r.get('author', ''),
                        'play': r.get('play', 0),
                        'danmaku': r.get('video_review', 0),
                        'likes': r.get('like', 0),
                        'coins': r.get('coin', 0),
                        'favs': r.get('favorites', 0),
                        'duration': r.get('duration', ''),
                        'aid': r.get('aid', ''),
                        'description': r.get('description', ''),
                    })
            else:
                print(f'B站 第{page}页 API错误: {data.get("message", "unknown")}')
                consecutive_fail += 1
        except Exception as e:
            print(f'B站 第{page}页 请求失败: {e}')
            consecutive_fail += 1
        
        if consecutive_fail >= max_consecutive_fail:
            print(f'B站 连续失败{max_consecutive_fail}次，停止')
            break
            
        page += 1
        time.sleep(random.uniform(0.5, 1.5))
    
    return results

# ========== 3. 保存到文件（追加模式）==========
DATA_DIR = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'content-hunter', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def append_douyin(results, start_num=173):
    filepath = os.path.join(DATA_DIR, 'douyin.md')
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f'\n\n---\n')
        f.write(f'> [追加抓取时间: {ts}]\n')
        f.write(f'> [本次新增: {len(results)} 条 抖音AI技术热门内容]\n\n')
        
        for i, item in enumerate(results, start_num):
            f.write(f'### 第{i}条\n')
            f.write(f'- 标题: {item["title"]}\n')
            f.write(f'- 作者: @{item["author"]}\n')
            f.write(f'- 点赞: {item["likes"]}\n')
            f.write(f'- 话题: {item["tags"]}\n')
            f.write(f'- 链接: {item["url"]}\n')
            f.write(f'- 内容总结: 视频主题为{item["title"]}，由@{item["author"]}创作，点赞数{item["likes"]}，内容涉及AI人工智能相关领域...\n\n')
    print(f'抖音: 已追加 {len(results)} 条到 {filepath}')

def append_bilibili(results, start_num=227):
    filepath = os.path.join(DATA_DIR, 'bilibili.md')
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f'\n\n---\n')
        f.write(f'> [追加抓取时间: {ts}]\n')
        f.write(f'> [本次新增: {len(results)} 条 B站AI技术热门内容]\n\n')
        
        for i, item in enumerate(results, start_num):
            f.write(f'### 第{i}条\n')
            f.write(f'- 标题: {item["title"]}\n')
            f.write(f'- UP主: {item["author"]}\n')
            f.write(f'- 播放: {item["play"]}\n')
            f.write(f'- 弹幕: {item["danmaku"]}\n')
            f.write(f'- 点赞: {item["likes"]}\n')
            f.write(f'- 投币: {item["coins"]}\n')
            f.write(f'- 收藏: {item["favs"]}\n')
            f.write(f'- 时长: {item["duration"]}\n')
            f.write(f'- 链接: https://www.bilibili.com/video/av{item["aid"]}\n')
            desc = (item['description'] or '暂无描述')[:200]
            f.write(f'- 内容总结: {desc}...\n\n')
    print(f'B站: 已追加 {len(results)} 条到 {filepath}')

# ========== 主流程 ==========
if __name__ == '__main__':
    print('=' * 50)
    print('开始抓取: 抖音 + B站 各100条AI技术热门内容')
    print('=' * 50)
    
    # 抖音
    print('\n[1/2] 抓取抖音...')
    douyin_results = scrape_douyin(keyword="AI人工智能", target_count=100)
    print(f'抖音抓取完成: {len(douyin_results)} 条')
    
    # B站
    print('\n[2/2] 抓取B站...')
    bilibili_results = scrape_bilibili(keyword="AI人工智能", target_count=100)
    print(f'B站抓取完成: {len(bilibili_results)} 条')
    
    # 追加保存
    print('\n[3/3] 保存到文件（追加模式）...')
    if douyin_results:
        append_douyin(douyin_results, start_num=173)
    if bilibili_results:
        append_bilibili(bilibili_results, start_num=227)
    
    print('\n全部完成！')
    print(f'  抖音: {len(douyin_results)} 条')
    print(f'  B站: {len(bilibili_results)} 条')
