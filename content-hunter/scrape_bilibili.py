#!/usr/bin/env python3
"""B站 AI技术内容抓取 - API方式 (改进版)"""
import urllib.request
import urllib.parse
import json
import time
import os
import random

def scrape_bilibili(keyword="AI人工智能", target_count=100, pagesize=20):
    """抓取B站视频搜索结果，带重试"""
    results = []
    page = 1
    max_pages = 50  # 最多50页 = 1000条
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
        
        req = urllib.request.Request(url, headers=headers)
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read().decode('utf-8'))
            
            if data.get('code') == 0:
                results_raw = data.get('data', {}).get('result', [])
                if not results_raw:
                    print(f"第{page}页: 空结果，停止")
                    break
                    
                consecutive_fail = 0
                print(f"第{page}页: 获得 {len(results_raw)} 条 (累计{len(results)})")
                
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
                        'mid': r.get('mid', ''),
                        'aid': r.get('aid', ''),
                        'description': r.get('description', ''),
                    })
            else:
                print(f"第{page}页 API错误: {data.get('message', 'unknown')}")
                consecutive_fail += 1
        except Exception as e:
            print(f"第{page}页 请求失败: {e}")
            consecutive_fail += 1
        
        if consecutive_fail >= max_consecutive_fail:
            print(f"连续失败{max_consecutive_fail}次，停止")
            break
            
        page += 1
        time.sleep(random.uniform(0.5, 1.5))
    
    return results

def save_to_markdown(results, filepath):
    """保存为markdown格式（追加模式）"""
    content = f"# B站 AI技术热门内容\n\n"
    content += f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"总条数: {len(results)}\n\n"
    
    for i, item in enumerate(results, 1):
        content += f"### 第{i}条\n"
        content += f"- 标题: {item['title']}\n"
        content += f"- UP主: {item['author']}\n"
        content += f"- 播放: {item['play']}\n"
        content += f"- 弹幕: {item['danmaku']}\n"
        content += f"- 点赞: {item['likes']}\n"
        content += f"- 投币: {item['coins']}\n"
        content += f"- 收藏: {item['favs']}\n"
        content += f"- 时长: {item['duration']}\n"
        desc = item['description'][:200] if item['description'] else '暂无描述'
        content += f"- 内容总结: {desc}...\n\n"
    
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已追加保存 {len(results)} 条到 {filepath}")

if __name__ == '__main__':
    results = scrape_bilibili(keyword="AI人工智能", target_count=100)
    
    data_dir = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'content-hunter', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    filepath = os.path.join(data_dir, 'bilibili.md')
    save_to_markdown(results, filepath)
    print(f"完成! 共抓取 {len(results)} 条B站内容")
