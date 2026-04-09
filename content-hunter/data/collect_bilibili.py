# -*- coding: utf-8 -*-
import os
import json
import re
import time

def get_snapshot():
    """获取当前页面快照"""
    stream = os.popen('npx agent-browser snapshot 2>&1')
    try:
        return stream.read().decode('utf-8', errors='ignore')
    except:
        return stream.read()

def extract_bilibili_videos(snapshot):
    """从快照提取B站视频信息"""
    videos = []
    lines = snapshot.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if 'heading' in line and 'ref=e' in line:
            title_match = re.search(r'"([^"]+)"', line)
            if title_match:
                title = title_match.group(1)
                author = ''
                plays = ''
                danmu = ''
                likes = ''
                duration = ''
                
                for j in range(i+1, min(i+15, len(lines))):
                    next_line = lines[j].strip()
                    
                    if author == '' and '·' in next_line:
                        author_match = re.search(r'([^\s·"\'【】]+)\s*·', next_line)
                        if author_match:
                            author = author_match.group(1)
                    
                    stats = re.findall(r'(\d+\.?\d*[万]?)', next_line)
                    if stats and duration == '':
                        if len(stats) >= 1 and plays == '':
                            plays = stats[0]
                        if len(stats) >= 2 and danmu == '':
                            danmu = stats[1]
                        if len(stats) >= 3 and likes == '':
                            likes = stats[2]
                    
                    duration_match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)', next_line)
                    if duration_match:
                        duration = duration_match.group(1)
                    
                    if 'heading' in next_line and j > i + 2:
                        break
                
                ai_keywords = ['AI', '人工智能', 'ChatGPT', 'LLM', '大模型', '机器学习', '深度学习', 'AIGC', '神经网络', 'GPT', 'Gemini', 'Claude']
                if any(kw.lower() in title.lower() for kw in ai_keywords):
                    videos.append({
                        'title': title,
                        'author': author,
                        'plays': plays,
                        'danmu': danmu,
                        'likes': likes,
                        'duration': duration
                    })
        
        i += 1
    
    return videos

def scroll_and_collect(num_pages=5):
    """滚动页面并收集视频数据"""
    all_videos = []
    seen_titles = set()
    
    for page in range(num_pages):
        print(f"Collecting page {page + 1}...")
        snapshot = get_snapshot()
        
        with open(f'E:/workspace/content-hunter/data/bilibili_page{page+1}.txt', 'w', encoding='utf-8', errors='ignore') as f:
            f.write(snapshot)
        
        videos = extract_bilibili_videos(snapshot)
        print(f"  Found {len(videos)} AI videos")
        
        for v in videos:
            title_key = v['title'][:50]
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                all_videos.append(v)
        
        print(f"  Total unique: {len(all_videos)}")
        
        if page < num_pages - 1:
            os.system('npx agent-browser scroll down 5 > nul 2>&1')
            time.sleep(3)
        
        if len(all_videos) >= 100:
            break
    
    return all_videos

def format_markdown(videos):
    """生成Markdown格式"""
    md = "# B站AI技术热门内容\n\n抓取时间: 2026-04-09\n\n---\n\n"
    
    for i, v in enumerate(videos[:100], 1):
        title = v['title']
        title = re.sub(r'<[^>]+>', '', title)
        title = title.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
        
        md += f"### 第{i}条\n"
        md += f"- 标题: {title}\n"
        md += f"- UP主: {v.get('author', '未知')}\n"
        md += f"- 播放: {v.get('plays', '0')}\n"
        md += f"- 弹幕: {v.get('danmu', '0')}\n"
        md += f"- 点赞: {v.get('likes', '0')}\n"
        md += f"- 投币: {v.get('coins', '0')}\n"
        md += f"- 收藏: {v.get('favorite', '0')}\n"
        md += f"- 时长: {v.get('duration', '未知')}\n"
        md += f"- 内容总结: 暂无简介\n\n"
    
    return md

if __name__ == "__main__":
    print("Scrolling and collecting videos...")
    videos = scroll_and_collect(5)
    
    print(f"\nTotal videos collected: {len(videos)}")
    
    with open('E:/workspace/content-hunter/data/bilibili_raw.json', 'w', encoding='utf-8', errors='ignore') as f:
        json.dump(videos, f, ensure_ascii=False, indent=2)
    
    md = format_markdown(videos)
    with open('E:/workspace/content-hunter/data/bilibili.md', 'w', encoding='utf-8', errors='ignore') as f:
        f.write(md)
    
    print(f"Saved {len(videos)} videos to bilibili.md")
