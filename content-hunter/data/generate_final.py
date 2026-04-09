# -*- coding: utf-8 -*-
import codecs
import re

def read_file(path):
    """读取文件，尝试多种编码"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'utf-16']
    for enc in encodings:
        try:
            with codecs.open(path, 'r', encoding=enc, errors='ignore') as f:
                content = f.read()
                if len(content) > 100:
                    return content
        except:
            continue
    return ""

def extract_entries(content, min_title_len=5):
    """从内容中提取条目"""
    entries = []
    
    # 分割条目
    parts = re.split(r'(?=## )', content)
    
    for part in parts:
        if len(part) < 50:
            continue
            
        lines = part.split('\n')
        entry = {}
        
        for line in lines:
            line = line.strip()
            
            # 提取标题
            if '标题' in line and ':' in line:
                title = line.split(':', 1)[-1].strip()
                title = re.sub(r'^[-*]\s*', '', title)
                if len(title) > min_title_len:
                    entry['title'] = title[:100]
            
            # 提取作者
            if '@' in line:
                match = re.search(r'@([\w\u4e00-\u9fff_]+)', line)
                if match:
                    entry['author'] = '@' + match.group(1)
            
            # 提取点赞
            if '点赞' in line:
                match = re.search(r'点赞.*?(\d+\.?\d*[万]?)', line)
                if match:
                    entry['likes'] = match.group(1)
            
            # 提取话题
            if '#' in line:
                tags = re.findall(r'#\w+', line)
                if tags:
                    entry['tags'] = ' '.join(tags[:5])
            
            # 提取内容总结
            if '总结' in line and ':' in line:
                summary = line.split('总结', 1)[-1].replace(':', '').strip()
                if summary:
                    entry['summary'] = summary[:200]
        
        if 'title' in entry and len(entry.get('title', '')) > min_title_len:
            entries.append(entry)
    
    return entries

def format_bilibili_entry(i, e):
    """格式化B站条目"""
    return f"""
### 第{i}条
- 标题: {e.get('title', '未知标题')}
- UP主: {e.get('author', '@未知UP主')}
- 播放: {e.get('plays', '未知')}
- 弹幕: {e.get('danmu', '0')}
- 点赞: {e.get('likes', '未知')}
- 投币: {e.get('coins', '0')}
- 收藏: {e.get('favorite', '未知')}
- 字幕: {e.get('subtitle', '无')}
- 内容总结: {e.get('summary', '暂无简介')}"""

def format_douyin_entry(i, e):
    """格式化抖音条目"""
    return f"""
### 第{i}条
- 标题: {e.get('title', '未知标题')}
- 作者: {e.get('author', '@未知作者')}
- 点赞: {e.get('likes', '未知')}
- 话题: {e.get('tags', '#AI')}
- 内容总结: {e.get('summary', '暂无简介')}"""

# 读取B站数据
print("处理B站数据...")
bili_content = read_file('E:/workspace/content-hunter/data/douyin-ai-2026-04-08.md')
bili_entries = extract_entries(bili_content)

# 过滤AI相关内容
ai_keywords = ['AI', '人工智能', 'ChatGPT', '大模型', '机器学习', '深度学习', 'AIGC', 'LLM', '神经网络', 'GPT', 'Gemini', 'Claude']
ai_bili_entries = []
for e in bili_entries:
    title = e.get('title', '').lower()
    tags = e.get('tags', '').lower()
    if any(kw.lower() in title or kw.lower() in tags for kw in ai_keywords):
        ai_bili_entries.append(e)

print(f"找到 {len(ai_bili_entries)} 条AI相关B站数据")

# 生成B站Markdown
bili_md = "# B站AI技术热门内容\n\n抓取时间: 2026-04-09\n\n---\n\n"
for i, e in enumerate(ai_bili_entries[:100], 1):
    bili_md += format_bilibili_entry(i, e)

with codecs.open('E:/workspace/content-hunter/data/bilibili_final.md', 'w', encoding='utf-8') as f:
    f.write(bili_md)

print(f"写入 {min(100, len(ai_bili_entries))} 条B站数据到 bilibili_final.md")

# 读取抖音数据
print("\n处理抖音数据...")
douyin_content = read_file('E:/workspace/content-hunter/data/douyin-ai-2026-04-08.md')
douyin_entries = extract_entries(douyin_content)

# 过滤AI相关内容
ai_douyin_entries = []
for e in douyin_entries:
    title = e.get('title', '').lower()
    tags = e.get('tags', '').lower()
    if any(kw.lower() in title or kw.lower() in tags for kw in ai_keywords):
        ai_douyin_entries.append(e)

print(f"找到 {len(ai_douyin_entries)} 条AI相关抖音数据")

# 生成抖音Markdown
douyin_md = "# 抖音AI技术热门内容\n\n抓取时间: 2026-04-09\n\n---\n\n"
for i, e in enumerate(ai_douyin_entries[:100], 1):
    douyin_md += format_douyin_entry(i, e)

with codecs.open('E:/workspace/content-hunter/data/douyin_final.md', 'w', encoding='utf-8') as f:
    f.write(douyin_md)

print(f"写入 {min(100, len(ai_douyin_entries))} 条抖音数据到 douyin_final.md")
print("\n完成!")
