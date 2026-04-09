"""
抖音 AI热门内容抓取 - 修复版
"""
import requests
import re
import os
import time
import json
import urllib.parse
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def count_items(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r'### 第\d+条', content))

def get_last_item_num(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    matches = re.findall(r'### 第(\d+)条', content)
    return max(int(m) for m in matches) if matches else 0

def append_content(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

def format_views(v):
    try:
        v = int(v)
    except:
        v = 0
    if v >= 100000000:
        return f"{v/100000000:.1f}亿"
    elif v >= 10000:
        return f"{v/10000:.1f}万"
    elif v > 0:
        return str(v)
    return "未知"

def is_ai_related(title, author=""):
    ai_keywords = [
        'ai', '人工智能', 'AI', 'ChatGPT', 'GPT', '大模型', 'LLM',
        '深度学习', '机器学习', '神经网络', 'TensorFlow', 'PyTorch',
        'OpenAI', '文心', '通义', 'Kimi', '豆包', 'DeepSeek', 'Gemini',
        'Copilot', 'Midjourney', 'StableDiffusion', 'SD', '扩散模型',
        'Transformer', 'RAG', 'Agent', '智能体', 'AIGC', '生成式AI',
        'Prompt', '提示词', '本地部署', '开源模型', 'LLama', 'Mistral',
        '自动驾驶', '计算机视觉', 'NLP', '自然语言', '语音识别',
        'Diffusion', 'VAE', 'GAN', '视频生成', 'AI视频',
        'AI音乐', 'AI绘图', 'AI编程', 'Cursor', 'Claude', 'Claude3',
        'o1', 'o3', 'Grok', 'Sora', 'Runway', 'Pika',
        '数字人', '虚拟人', 'AI主播', 'AI助手', 'AI工具', 'AI应用',
        '算法', '算力', 'GPU', 'AI芯片', '神经网络',
        'Python', 'LangChain', 'LangGraph', '向量数据库', 'Embedding',
        'RAG', '知识库', '检索增强', '微调', 'Fine-tuning',
        '开源', '部署', 'API', 'SDK', '推理',
        'token', '上下文', '长上下文', '多模态', 'VL', '视觉语言',
        '自动化', '机器人', '具身智能', 'Embodied', 'AI学习'
    ]
    text = (title + author).lower()
    return any(kw.lower() in text for kw in ai_keywords)

def fetch_douyin_ai(count=100):
    items = []
    keywords = [
        "AI人工智能", "ChatGPT", "大模型", "AIGC", "DeepSeek",
        "AI工具", "AI教程", "AI科技", "人工智能应用", "AI数码",
        "AI创作", "AI助手", "豆包AI", "KimiAI", "AI应用"
    ]
    
    for keyword in keywords:
        if len(items) >= count:
            break
        print(f"  [Douyin] search: {keyword}")
        
        encoded_kw = urllib.parse.quote(keyword)
        url = "https://www.douyin.com/aweme/v1/web/search/item/"
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "keyword": keyword,
            "search_source": "normal_search",
            "query_correct_type": "1",
            "from_group_id": "",
            "offset": "0",
            "count": "20",
        }
        headers = {
            "User-Agent": PC_UA,
            "Referer": f"https://www.douyin.com/search/{encoded_kw}",
        }
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            data = resp.json()
            
            aweme_list = data.get("aweme_list", []) if isinstance(data, dict) else []
            
            for aweme in aweme_list:
                if len(items) >= count:
                    break
                    
                desc = aweme.get("desc", "")
                author = aweme.get("author", {}).get("nickname", "")
                digg_count = aweme.get("statistics", {}).get("digg_count", 0)
                collect_count = aweme.get("statistics", {}).get("collect_count", 0)
                share_count = aweme.get("statistics", {}).get("share_count", 0)
                comment_count = aweme.get("statistics", {}).get("comment_count", 0)
                aweme_id = aweme.get("aweme_id", "")
                
                video_duration = aweme.get("video", {}).get("duration", 0)
                if video_duration:
                    sec = video_duration // 1000
                    m = sec // 60
                    s = sec % 60
                    duration = f"{m}:{s:02d}"
                else:
                    duration = "未知"
                
                if not is_ai_related(desc, author):
                    continue
                
                hashtags = []
                text_extra = aweme.get("text_extra", []) or []
                for t in text_extra:
                    tag = t.get("hashtag_name", "")
                    if tag:
                        hashtags.append(f"#{tag}")
                topics_str = " ".join(hashtags[:5]) if hashtags else "#AI #人工智能"
                
                items.append({
                    "platform": "抖音",
                    "title": desc if desc else f"抖音视频_{aweme_id[:8]}",
                    "author": f"@{author}",
                    "likes": format_views(digg_count),
                    "topics": topics_str,
                    "duration": duration,
                    "comment": format_views(comment_count),
                    "collect": format_views(collect_count),
                    "share": format_views(share_count),
                    "url": f"https://www.douyin.com/video/{aweme_id}" if aweme_id else "",
                    "keyword": keyword
                })
                print(f"    + {desc[:40] if desc else '(no title)'} | {author} | {format_views(digg_count)}")
            
            time.sleep(0.5)
        except Exception as e:
            print(f"    ! Error: {e}")
            continue
    
    # Deduplicate
    seen = set()
    deduped = []
    for item in items:
        key = item["title"]
        if key not in seen and key:
            seen.add(key)
            deduped.append(item)
    
    print(f"  [Douyin] Total: {len(deduped)} items")
    return deduped[:count]

def format_douyin_md(items, start_num=1):
    lines = []
    for i, item in enumerate(items, start_num):
        lines.append(f"### 第{i}条")
        lines.append(f"- 标题: {item['title']}")
        lines.append(f"- 作者: {item['author']}")
        lines.append(f"- 点赞: {item['likes']}")
        lines.append(f"- 评论: {item['comment']}")
        lines.append(f"- 收藏: {item['collect']}")
        lines.append(f"- 转发: {item['share']}")
        lines.append(f"- 时长: {item['duration']}")
        lines.append(f"- 话题: {item['topics']}")
        lines.append(f"- 链接: {item['url']}")
        lines.append(f"- 来源关键词: {item['keyword']}")
        lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    NOW = datetime.now().strftime("%Y-%m-%d")
    print("=" * 50)
    print("Douyin AI Scraper - Starting...")
    print("=" * 50)
    
    douyin_file = os.path.join(DATA_DIR, "douyin.md")
    current = count_items(douyin_file)
    print(f"Current items: {current}")
    
    items = fetch_douyin_ai(count=100)
    
    if items:
        start_num = get_last_item_num(douyin_file) + 1
        md_content = format_douyin_md(items, start_num)
        header = f"\n\n---\n\n## 抖音 AI内容追加批次 ({NOW} 13:00) - 新增 {len(items)} 条\n\n"
        append_content(douyin_file, header + md_content)
        print(f"[OK] Appended {len(items)} to douyin.md (from item #{start_num})")
    else:
        print("! No data retrieved")
    
    final = count_items(douyin_file)
    print(f"Final count: {final}")
    print("Done!")
