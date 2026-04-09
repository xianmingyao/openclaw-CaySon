# -*- coding: utf-8 -*-
import subprocess
import json
import re
import time

def run_agent_command(cmd):
    """运行agent-browser命令并获取结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )
        return result.stdout
    except Exception as e:
        return str(e)

def get_page_snapshot():
    """获取当前页面快照"""
    output = run_agent_command('npx agent-browser snapshot 2>&1')
    return output

def parse_bilibili_results(snapshot):
    """解析B站搜索结果"""
    results = []
    
    # 匹配视频条目的正则表达式
    # 格式: 标题 | 播放量 | 弹幕 | 时长 或类似格式
    lines = snapshot.split('\n')
    
    current_item = {}
    for line in lines:
        line = line.strip()
        
        # 提取标题
        if 'heading' in line and ('AI' in line or '人工智能' in line or 'ChatGPT' in line or '大模型' in line):
            title_match = re.search(r'heading "[^"]*"\s*\[level=\d+,\s*ref=e\d+\]\s*\n?\s*(.+)', line)
            if title_match:
                current_item['title'] = title_match.group(1).strip()
        
        # 提取作者/UP主
        if '·' in line and 'ref=e' in line:
            author_match = re.search(r'([^\s·]+)\s*·\s*(\d{4}[-/]\d{2}[-/]\d{2}|\d+课时)', line)
            if author_match:
                current_item['author'] = author_match.group(1)
        
        # 提取播放量
        play_match = re.search(r'(\d+\.?\d*[万]?)\s*$', line)
        if play_match and 'image' not in line and 'generic' not in line:
            value = play_match.group(1)
            if '万' not in value and value.isdigit():
                if 'plays' not in current_item:
                    current_item['plays'] = value
    
    return results

def extract_video_info_from_snapshot(snapshot):
    """从页面快照提取视频信息"""
    videos = []
    
    # 分割快照为行
    lines = snapshot.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 查找包含AI相关关键词的标题行
        if ('AI' in line or '人工智能' in line or 'ChatGPT' in line or '大模型' in line or '机器学习' in line or '深度学习' in line) and ('heading' in line or 'ref=e' in line):
            # 提取标题
            title = ''
            if 'heading' in line:
                match = re.search(r'heading\s+"([^"]+)"', line)
                if match:
                    title = match.group(1)
            
            # 查找下一行中的作者信息
            author = ''
            plays = ''
            danmu = ''
            likes = ''
            
            for j in range(i+1, min(i+10, len(lines))):
                next_line = lines[j].strip()
                
                # 提取UP主
                if '·' in next_line and ('ref=e' in next_line or 'link' in next_line):
                    author_match = re.search(r'([^\s·]+)\s*·', next_line)
                    if author_match and not author:
                        author = author_match.group(1)
                
                # 提取播放量（在图片行后的统计信息）
                if re.search(r'\d+\.?\d*[万]?', next_line) and 'image' not in next_line:
                    stat_match = re.search(r'(\d+\.?\d*[万]?)', next_line)
                    if stat_match and not plays:
                        plays = stat_match.group(1)
                        # 检查是否有更多统计
                        stats = re.findall(r'(\d+\.?\d*[万]?)', next_line)
                        if len(stats) >= 2:
                            danmu = stats[1]
                        if len(stats) >= 3:
                            likes = stats[2]
                
                # 遇到下一个heading就停止
                if 'heading' in next_line:
                    break
            
            if title:
                videos.append({
                    'title': title,
                    'author': author,
                    'plays': plays,
                    'danmu': danmu,
                    'likes': likes
                })
        
        i += 1
    
    return videos

# 继续从上次结果中获取
print("Getting page snapshot...")
snapshot = get_page_snapshot()

# 保存快照用于调试
with open('E:/workspace/content-hunter/data/bilibili_snapshot.txt', 'w', encoding='utf-8') as f:
    f.write(snapshot)

print("Snapshot saved. Parsing...")

videos = extract_video_info_from_snapshot(snapshot)
print(f"Found {len(videos)} videos")

# 保存结果
with open('E:/workspace/content-hunter/data/bilibili_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(videos, f, ensure_ascii=False, indent=2)

print("Done!")
