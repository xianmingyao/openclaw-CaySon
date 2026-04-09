# -*- coding: utf-8 -*-
import requests
import json
import time
import re

def search_bilibili(keyword, page=1, page_size=30):
    """搜索B站视频"""
    results = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://search.bilibili.com',
    }
    
    url = f"https://api.bilibili.com/x/web-interface/search/type"
    params = {
        'search_type': 'video',
        'keyword': keyword,
        'page': page,
        'page_size': page_size,
        'order': 'totalrank',
        'duration': 0,
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        data = response.json()
        
        if data.get('code') != 0:
            print(f"API error: {data.get('message')}")
            return results
            
        result = data.get('data', {})
        videos = result.get('result', [])
        
        for v in videos:
            # 解析播放量、点赞、硬币、收藏
            stat_text = v.get('stat', '')
            
            # 播放量
            play_match = re.search(r'(\d+\.?\d*)[万]?', v.get('play', ''))
            plays = play_match.group(1) if play_match else '0'
            if '万' in v.get('play', ''):
                plays = str(float(play_match.group(1)) * 10000)
            
            # 点赞
            like_match = re.search(r'(\d+\.?\d*)[万]?', v.get('like', ''))
            likes = like_match.group(1) if like_match else '0'
            if '万' in v.get('like', ''):
                likes = str(float(like_match.group(1)) * 10000)
            
            results.append({
                'title': v.get('title', ''),
                'author': v.get('author', ''),
                'plays': plays,
                'danmu': v.get('video_review', '0'),  # 弹幕数
                'likes': likes,
                'coins': v.get('coins', '0'),  # 投币
                'favorite': v.get('favorite', '0'),  # 收藏
                'duration': v.get('duration', ''),
                'bvid': v.get('bvid', ''),
                'aid': v.get('aid', ''),
                'desc': v.get('description', ''),
                'pubdate': v.get('pubdate', ''),
                'subtitle': '有' if v.get('subtitle') else '无',
            })
            
    except Exception as e:
        print(f"Error: {e}")
    
    return results

def format_bilibili_entry(index, v):
    """格式化B站视频条目"""
    # 清理标题中的HTML标签
    title = re.sub(r'<[^>]+>', '', v.get('title', ''))
    title = title.replace('&amp;', '&').replace('&quot;', '"')
    
    # 格式化内容摘要
    desc = v.get('desc', '')[:200] if v.get('desc') else '暂无简介'
    
    entry = f"""
### 第{index}条
- 标题: {title}
- UP主: {v.get('author', '未知')}
- 播放: {v.get('plays', '0')}
- 弹幕: {v.get('danmu', '0')}
- 点赞: {v.get('likes', '0')}
- 投币: {v.get('coins', '0')}
- 收藏: {v.get('favorite', '0')}
- 字幕: {v.get('subtitle', '无')}
- 内容总结: {desc}
"""
    return entry

if __name__ == "__main__":
    keywords = ['AI人工智能', 'ChatGPT', '大模型', 'AI工具', 'AIGC', '深度学习', '机器学习']
    all_results = []
    
    for kw in keywords:
        print(f"Searching: {kw}")
        for page in range(1, 4):  # 每关键词抓3页
            results = search_bilibili(kw, page=page)
            if not results:
                break
            all_results.extend(results)
            print(f"  Page {page}: {len(results)} videos")
            time.sleep(0.5)
    
    # 去重
    unique_results = []
    seen_ids = set()
    for r in all_results:
        bvid = r.get('bvid', '')
        if bvid and bvid not in seen_ids:
            seen_ids.add(bvid)
            unique_results.append(r)
    
    print(f"\nTotal unique results: {len(unique_results)}")
    
    # 保存JSON
    with open('E:/workspace/content-hunter/data/bilibili_raw_api.json', 'w', encoding='utf-8') as f:
        json.dump(unique_results, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown
    md_content = "# B站AI技术热门内容\n\n抓取时间: 2026-04-09\n\n---\n\n"
    
    for i, v in enumerate(unique_results[:100], 1):
        md_content += format_bilibili_entry(i, v)
    
    with open('E:/workspace/content-hunter/data/bilibili.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Generated {len(unique_results[:100])} entries")
    print("Saved to bilibili.md")
