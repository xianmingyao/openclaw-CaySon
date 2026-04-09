"""
Bing搜索 抓取抖音AI内容 - 纯HTTP解析版
不依赖yt-dlp，直接从Bing页面解析视频信息
"""
import re
import os
import time
import requests
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def count_items(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r'### 第\d+条', content))

def save_append(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

def is_ai_related(title):
    ai_kws = [
        'ai', 'chatgpt', 'gpt', '大模型', 'llm', '深度学习', '机器学习',
        '神经网络', 'openai', '文心', '通义', 'kimi', '豆包', 'deepseek', 'gemini',
        'copilot', 'midjourney', 'diffusion', 'aigc', 'agent', '智能体', '生成式',
        'prompt', '提示词', '开源模型', 'sora', 'runway', 'pika', 'cursor', 'claude',
        '数字人', 'ai工具', 'ai应用', 'ai助手', 'ai创作', 'ai学习', 'ai教程',
        'langchain', 'rag', 'embedding', '向量', '微调', '部署', '推理', 'token',
        'python', '编程', '开发', '算法', '算力', 'gpu', '人工智能', '智能化',
        '自动化', '机器人', '科技', '技术'
    ]
    text = title.lower()
    return any(kw.lower() in text for kw in ai_kws)

def search_bing_videos(keyword, pages=2):
    """从Bing视频搜索获取抖音视频信息"""
    all_items = []
    
    for page in range(pages):
        offset = page * 10
        url = f"https://cn.bing.com/videos/search?q={requests.utils.quote(keyword)}+site:douyin.com&first={offset}&FORM=HDRSC4"
        headers = {
            "User-Agent": PC_UA,
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            # 提取视频标题
            titles = re.findall(r'<a[^>]+href="([^"]+)"[^>]*class="[^"]*v-title[^"]*"[^>]*>([^<]+)<', html)
            if not titles:
                # 备选：提取所有链接中的标题
                titles = re.findall(r'data-vid="[^"]*"[^>]*>\s*<[^>]*title="([^"]+)"', html)
            
            # 提取视频时长
            durations = re.findall(r'"duration"\s*:\s*"([^"]+)"', html)
            
            # 提取视频URL
            video_urls = re.findall(r'href="(https?://[^"]*douyin\.com[^"]*)"', html)
            video_urls = list(dict.fromkeys(video_urls))
            
            # 提取缩略图旁的信息（播放量等）
            stats = re.findall(r'"viewCount"\s*:\s*"([^"]+)"', html)
            
            print(f"  Page {page+1}: found {len(video_urls)} URLs, {len(titles)} titles")
            
            for i, url in enumerate(video_urls):
                if len(all_items) >= 50:
                    break
                
                # 提取视频ID
                vid = re.search(r'/video/(\d+)', url)
                vid_str = vid.group(1) if vid else f"v{i}"
                
                # 从URL猜测标题
                title = keyword + " - 抖音视频"
                author = "抖音用户"
                duration = "未知"
                likes = "未知"
                
                # 尝试从HTML中找到对应信息
                # 有些Bing页面会在附近显示视频标题
                title_match = re.search(rf'douyin\.com[^\s"<>]*\s*([^<\n]+{re.escape(keyword)}[^\n<\s]*|{re.escape(keyword)}[^\n<\s]*)', html, re.I)
                
                # 直接从页面结构解析
                # 查找包含该URL附近的标题
                context_pattern = rf'href="{re.escape(url)}"[^>]*>.*?title="([^"]+)"'
                m = re.search(context_pattern, html, re.S)
                if m:
                    t = m.group(1).strip()
                    if t and len(t) > 3:
                        title = t
                
                # 时长 - 通常在URL附近
                vid_esc = re.escape(vid_str)
                dur_pattern = f'"{vid_esc}"[^}}]*?"duration"\\s*:\\s*"([^"]+)"'
                dm = re.search(dur_pattern, html)
                if dm:
                    duration = dm.group(1)
                
                if is_ai_related(title):
                    all_items.append({
                        "title": title,
                        "author": author,
                        "duration": duration,
                        "likes": likes,
                        "url": url,
                        "keyword": keyword
                    })
                    print(f"    + {title[:50]}")
            
        except Exception as e:
            print(f"  Page {page+1} error: {e}")
        
        time.sleep(1)
    
    return all_items

def main():
    NOW = datetime.now().strftime("%Y-%m-%d")
    douyin_path = os.path.join(DATA_DIR, "douyin.md")
    existing_count = count_items(douyin_path)
    
    # 读取已有标题
    seen_titles = set()
    if os.path.exists(douyin_path):
        with open(douyin_path, "r", encoding="utf-8") as f:
            for line in f:
                m = re.search(r'- 标题: (.+)', line)
                if m:
                    seen_titles.add(m.group(1).strip())
    
    print(f"Current: {existing_count} items")
    
    keywords = [
        "AI人工智能教程", "ChatGPT技巧", "大模型应用", "AI工具推荐",
        "AI绘画教学", "AI视频制作", "DeepSeek教程", "AIGC创作"
    ]
    
    all_new = []
    
    for kw in keywords:
        if len(all_new) >= 100:
            break
        print(f"\nKeyword: {kw}")
        items = search_bing_videos(kw, pages=2)
        
        for item in items:
            if len(all_new) >= 100:
                break
            title = item['title']
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
            idx = existing_count + len(all_new) + 1
            entry = f"""
### 第{idx}条
- 标题: {title}
- 作者: @{item['author']}
- 点赞: {item['likes']}
- 话题: #{item['keyword']} #AI #抖音
- 时长: {item['duration']}
- 链接: {item['url']}
- 内容总结: {title}
"""
            all_new.append(entry)
        
        time.sleep(1)
    
    if all_new:
        content = "\n".join(all_new)
        header = f"\n\n---\n\n## 抖音 AI内容追加批次 ({NOW} 13:00) - 新增 {len(all_new)} 条\n\n"
        save_append(douyin_path, header + content)
        print(f"\n[DONE] Douyin: {len(all_new)} items appended. Total: {existing_count + len(all_new)}")
    else:
        print("\n[WARN] No new items")

if __name__ == "__main__":
    main()
