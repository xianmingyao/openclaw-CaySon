#!/usr/bin/env python3
"""抖音 AI技术内容抓取 - 移动端API方式"""
import urllib.request
import urllib.parse
import json
import time
import os
import random
import re

def scrape_douyin(keyword="AI人工智能", target_count=100):
    """抓取抖音搜索结果（移动端API）"""
    results = []
    cursor = 0
    
    while len(results) < target_count:
        # 视频搜索API
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
        
        req = urllib.request.Request(url, headers=headers)
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            raw = resp.read().decode('utf-8')
            data = json.loads(raw)
            
            status = data.get('status_code', -1)
            has_more = data.get('has_more', 0)
            items = data.get('data', [])
            
            print(f"Offset {cursor}: status={status}, has_more={has_more}, items={len(items)}")
            
            if not items:
                print(f"  -> 空结果，停止")
                break
            
            for item in items:
                aweme = item.get('aweme_info', {}) or item
                video_desc = aweme.get('desc', '')
                author = aweme.get('author', {}).get('nickname', '')
                digg_count = aweme.get('statistics', {}).get('digg_count', 0)
                share_url = aweme.get('share_url', '')
                aweme_id = aweme.get('aweme_id', '')
                
                # 提取话题
                tags = re.findall(r'#(\w+)', video_desc)
                
                results.append({
                    'title': video_desc or '无标题',
                    'author': author,
                    'likes': digg_count,
                    'tags': ' '.join([f'#{t}' for t in tags[:5]]),
                    'url': share_url or f'https://www.douyin.com/video/{aweme_id}',
                    'aweme_id': aweme_id,
                })
            
            if not has_more:
                print(f"  -> 没有更多结果")
                break
                
            cursor += 20
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"Offset {cursor} 失败: {e}")
            # 尝试备用API
            try:
                url2 = 'https://api.douyin.wtf/api.json?' + urllib.parse.urlencode({'word': keyword, 'count': '20', 'offset': str(cursor)})
                req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
                resp2 = urllib.request.urlopen(req2, timeout=10)
                print(f"  -> 备用API成功!")
            except:
                pass
            break
    
    return results

def save_to_markdown(results, filepath):
    """保存为markdown格式（追加模式）"""
    content = f"# 抖音 AI技术热门内容\n\n"
    content += f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"总条数: {len(results)}\n\n"
    
    for i, item in enumerate(results, 1):
        content += f"### 第{i}条\n"
        content += f"- 标题: {item['title']}\n"
        content += f"- 作者: @{item['author']}\n"
        content += f"- 点赞: {item['likes']}\n"
        content += f"- 话题: {item['tags']}\n"
        content += f"- 内容总结: 视频内容为{item['title']}，作者{item['author']}创作...\n\n"
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已追加保存 {len(results)} 条到 {filepath}")

if __name__ == '__main__':
    results = scrape_douyin(keyword="AI人工智能", target_count=100)
    
    data_dir = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'content-hunter', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, 'douyin.md')
    save_to_markdown(results, filepath)
    print(f"完成! 共抓取 {len(results)} 条抖音内容")
