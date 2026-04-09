"""
抖音 + B站 AI热门内容抓取 - 追加到 md 文件
抓取时间: 2026-04-09 13:00
"""
import requests
import re
import os
import time
import json
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
NOW = datetime.now().strftime("%Y-%m-%d")

PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ============================================================
# 辅助函数
# ============================================================

def count_items(filepath):
    """统计已有条数"""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r'### 第\d+条', content))

def get_last_item_num(filepath):
    """获取最后一个条目的编号"""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    matches = re.findall(r'### 第(\d+)条', content)
    if not matches:
        return 0
    return max(int(m) for m in matches)

def append_content(filepath, content):
    """追加内容到文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

def format_views(v):
    """格式化播放量"""
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
    """判断是否AI相关"""
    ai_keywords = [
        'ai', '人工智能', 'AI', 'ChatGPT', 'GPT', '大模型', 'LLM',
        '深度学习', '机器学习', '神经网络', 'TensorFlow', 'PyTorch',
        'OpenAI', '文心', '通义', 'Kimi', '豆包', 'DeepSeek', 'Gemini',
        'Copilot', 'Midjourney', 'StableDiffusion', 'SD', '扩散模型',
        'Transformer', 'RAG', 'Agent', '智能体', 'AIGC', '生成式AI',
        'Prompt', '提示词', '本地部署', '开源模型', 'LLama', 'Mistral',
        '自动驾驶', '计算机视觉', 'NLP', '自然语言', '语音识别',
        'Diffusion', 'VAE', 'GAN', 'VAE', '视频生成', 'AI视频',
        'AI音乐', 'AI绘图', 'AI编程', 'Cursor', 'Claude', 'Claude3',
        'o1', 'o3', 'Grok', 'V2', 'V3', 'Sora', 'Runway', 'Pika',
        '数字人', '虚拟人', 'AI主播', 'AI助手', 'AI工具', 'AI应用',
        '算法', '算力', 'GPU', 'NPU', 'AI芯片', '神经网络',
        'Python', 'LangChain', 'LangGraph', '向量数据库', 'Embedding',
        'Embedding', 'RAG', '知识库', '检索增强', '微调', 'Fine-tuning',
        '开源', '部署', 'API', 'SDK', '炼丹', '模型权重', '推理',
        'token', '上下文', '长上下文', '多模态', 'VL', '视觉语言',
        '自动化', '机器人', 'ROS', '具身智能', 'Embodied'
    ]
    text = (title + author).lower()
    return any(kw.lower() in text for kw in ai_keywords)

# ============================================================
# B站 AI搜索抓取
# ============================================================

def fetch_bilibili_ai(count=100):
    """通过B站搜索API抓取AI相关内容"""
    items = []
    
    # B站搜索 API - 视频类型
    api_url = "https://api.bilibili.com/x/web-interface/search/type"
    
    keywords = ["AI人工智能", "ChatGPT", "大模型", "AIGC", "深度学习", "AI工具", "AI应用", "AI教程", "AI资讯", "AI数码"]
    
    headers = {
        "User-Agent": PC_UA,
        "Referer": "https://www.bilibili.com",
    }
    
    for keyword in keywords:
        if len(items) >= count:
            break
        print(f"  [B站] 搜索关键词: {keyword}")
        params = {
            "search_type": "video",
            "keyword": keyword,
            "page": 1,
            "pagesize": 20,
            "order": "totalrank",  # 综合排序
        }
        try:
            resp = requests.get(api_url, params=params, headers=headers, timeout=10)
            data = resp.json()
            if data.get("code") == 0:
                results = data.get("data", {}).get("result", [])
                for r in results:
                    if len(items) >= count:
                        break
                    title = r.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", "")
                    author = r.get("author", "")
                    play = r.get("play", "0")
                    video_review = r.get("video_review", "0")  # 弹幕数
                    duration = r.get("duration", "")
                    pubdate = r.get("pubdate", 0)
                    desc = r.get("description", "")
                    aid = r.get("aid", "")
                    bvid = r.get("bvid", "")
                    
                    # 格式化日期
                    date_str = "未知"
                    if pubdate:
                        try:
                            date_str = datetime.fromtimestamp(pubdate).strftime("%Y-%m-%d")
                        except:
                            pass
                    
                    # 格式化时长
                    if duration:
                        if ":" in str(duration):
                            dur = str(duration)
                        else:
                            try:
                                d = int(duration)
                                m = d // 60
                                s = d % 60
                                dur = f"{m}:{s:02d}"
                            except:
                                dur = duration
                    else:
                        dur = "未知"
                    
                    # 跳过非AI内容
                    if not is_ai_related(title, author):
                        continue
                    
                    items.append({
                        "platform": "B站",
                        "title": title,
                        "author": author,
                        "views": format_views(play),
                        "danmu": format_views(video_review),
                        "duration": dur,
                        "date": date_str,
                        "desc": desc[:100] if desc else "暂无描述",
                        "url": f"https://www.bilibili.com/video/{bvid}" if bvid else f"https://www.bilibili.com/video/av{aid}" if aid else "",
                        "keyword": keyword
                    })
                    print(f"    + {title[:40]} | {author} | {format_views(play)}播放")
            time.sleep(0.5)
        except Exception as e:
            print(f"    ! 错误: {e}")
            continue
    
    # 去重
    seen = set()
    deduped = []
    for item in items:
        key = item["title"]
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    
    print(f"  [B站] 共获取 {len(deduped)} 条AI相关内容")
    return deduped[:count]

# ============================================================
# 抖音 AI搜索 (通过搜索API)
# ============================================================

def fetch_douyin_ai(count=100):
    """通过抖音搜索抓取AI相关内容"""
    items = []
    
    keywords = [
        "AI人工智能", "ChatGPT", "大模型", "AIGC", "DeepSeek", 
        "AI工具", "AI教程", "AI科技", "人工智能应用", "AI数码",
        "AI创作", "AI助手", "豆包AI", "KimiAI", "AI应用"
    ]
    
    for keyword in keywords:
        if len(items) >= count:
            break
        print(f"  [抖音] 搜索关键词: {keyword}")
        
        # 抖音搜索 API
        url = "https://www.douyin.com/aweme/v1/web/search/item/"
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "keyword": keyword,
            "search_source": "normal_search",
            "query_correct_type": "1",
            "is_filter_search": "0",
            "from_group_id": "",
            "offset": "0",
            "count": "20",
        }
        headers = {
            "User-Agent": PC_UA,
            "Referer": "https://www.douyin.com/search/" + keyword,
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
                
                # 判断是否AI相关
                if not is_ai_related(desc, author):
                    continue
                
                # 格式化点赞
                digg_str = format_views(digg_count)
                
                # 生成话题标签
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
                    "likes": digg_str,
                    "topics": topics_str,
                    "duration": duration,
                    "comment": format_views(comment_count),
                    "collect": format_views(collect_count),
                    "share": format_views(share_count),
                    "url": f"https://www.douyin.com/video/{aweme_id}" if aweme_id else "",
                    "keyword": keyword
                })
                print(f"    + {desc[:40] if desc else '(无标题)'} | {author} | 👍{digg_str}")
            
            time.sleep(0.5)
        except Exception as e:
            print(f"    ! 错误: {e}")
            continue
    
    # 去重
    seen = set()
    deduped = []
    for item in items:
        key = item["title"]
        if key not in seen and key:
            seen.add(key)
            deduped.append(item)
    
    print(f"  [抖音] 共获取 {len(deduped)} 条AI相关内容")
    return deduped[:count]

# ============================================================
# 格式化输出
# ============================================================

def format_bilibili_md(items, start_num=1):
    """格式化B站条目为markdown"""
    lines = []
    for i, item in enumerate(items, start_num):
        lines.append(f"### 第{i}条")
        lines.append(f"- 标题: {item['title']}")
        lines.append(f"- 作者: {item['author']}")
        lines.append(f"- 播放: {item['views']}")
        lines.append(f"- 弹幕: {item['danmu']}")
        lines.append(f"- 时长: {item['duration']}")
        lines.append(f"- 日期: {item['date']}")
        lines.append(f"- 简介: {item['desc']}")
        lines.append(f"- 链接: {item['url']}")
        lines.append(f"- 来源关键词: {item['keyword']}")
        lines.append("")
    return "\n".join(lines)

def format_douyin_md(items, start_num=1):
    """格式化抖音条目为markdown"""
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

# ============================================================
# 主程序
# ============================================================

def main():
    print("=" * 60)
    print("内容捕手 - 抖音+B站 AI热门内容抓取")
    print(f"抓取时间: {NOW} 13:00")
    print("=" * 60)
    
    douyin_file = os.path.join(DATA_DIR, "douyin.md")
    bilibili_file = os.path.join(DATA_DIR, "bilibili.md")
    
    # 统计已有条数
    douyin_count = count_items(douyin_file)
    bilibili_count = count_items(bilibili_file)
    print(f"\n当前已有: 抖音 {douyin_count} 条 | B站 {bilibili_count} 条\n")
    
    # --- B站抓取 ---
    print("[1/2] 抓取B站AI内容...")
    bili_items = fetch_bilibili_ai(count=100)
    
    if bili_items:
        # 获取起始编号
        start_num = get_last_item_num(bilibili_file) + 1
        md_content = format_bilibili_md(bili_items, start_num)
        
        # 添加分隔头
        header = f"\n\n---\n\n## B站 AI内容追加批次 ({NOW} 13:00) - 新增 {len(bili_items)} 条\n\n"
        
        append_content(bilibili_file, header + md_content)
        print(f"  [OK] 已追加 {len(bili_items)} 条到 bilibili.md (从第{start_num}条开始)")
    else:
        print("  ! B站抓取失败或无可用数据")
    
    # --- 抖音抓取 ---
    print("\n[2/2] 抓取抖音AI内容...")
    douyin_items = fetch_douyin_ai(count=100)
    
    if douyin_items:
        start_num = get_last_item_num(douyin_file) + 1
        md_content = format_douyin_md(douyin_items, start_num)
        
        header = f"\n\n---\n\n## 抖音 AI内容追加批次 ({NOW} 13:00) - 新增 {len(douyin_items)} 条\n\n"
        
        append_content(douyin_file, header + md_content)
        print(f"  [OK] 已追加 {len(douyin_items)} 条到 douyin.md (从第{start_num}条开始)")
    else:
        print("  ! 抖音抓取失败或无可用数据")
    
    # 统计更新后总数
    new_douyin = count_items(douyin_file)
    new_bilibili = count_items(bilibili_file)
    print(f"\n更新后总计: 抖音 {new_douyin} 条 | B站 {new_bilibili} 条")
    print("=" * 60)
    print("抓取完成！")

if __name__ == "__main__":
    main()
