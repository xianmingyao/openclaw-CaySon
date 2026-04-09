"""
内容捕手 - 抖音+B站 AI内容抓取
每平台100条，追加到现有文件
"""
import re
import os
import time
import requests
import json
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

HEADERS = {
    "User-Agent": PC_UA,
    "Referer": "https://www.bilibili.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

NOW_STR = datetime.now().strftime("%Y-%m-%d %H:%M")
DATE_STR = datetime.now().strftime("%Y-%m-%d")

# ==================== 工具函数 ====================

def format_count(v):
    """格式化数字：1000 -> 1000, 10000 -> 1.0万, 100000000 -> 1.0亿"""
    try:
        v = int(v)
    except:
        v = 0
    if v >= 100000000:
        return f"{v/100000000:.1f}亿"
    elif v >= 10000:
        return f"{v/10000:.1f}万"
    return str(v)

def clean_title(title):
    """清理标题中的HTML标签"""
    if not title:
        return "未知标题"
    title = re.sub(r'<[^>]+>', '', title)
    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return title.strip()

def is_ai_related(title):
    """判断内容是否与AI相关"""
    ai_kws = [
        'ai', 'chatgpt', 'gpt', '大模型', 'llm', '深度学习', '机器学习',
        '神经网络', 'openai', '文心', '通义', 'kimi', '豆包', 'deepseek', 'gemini',
        'copilot', 'midjourney', 'diffusion', 'aigc', 'agent', '智能体', '生成式',
        'prompt', '提示词', '开源模型', 'sora', 'runway', 'pika', 'cursor', 'claude',
        '数字人', 'ai工具', 'ai应用', 'ai助手', 'ai创作', 'ai学习', 'ai教程',
        'langchain', 'rag', 'embedding', '向量', '微调', '部署', '推理', 'token',
        'python', '编程', '开发', '算法', '算力', 'gpu', '人工智能', '智能化',
        '自动化', '机器人', '科技', '技术', '自动化', 'ai绘画', 'ai视频',
        '人工智能', 'ai数码', '科技数码', '芯片', '算力', 'ai手机', 'ai电脑'
    ]
    text = (title or '').lower()
    return any(kw.lower() in text for kw in ai_kws)

def get_existing_titles(filepath):
    """读取已有文件的标题，用于去重"""
    titles = set()
    if not os.path.exists(filepath):
        return titles
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # 从表格中提取标题
    for m in re.finditer(r'\|\s*[^|]*?\s*\|\s*([^|]{5,100})\s*\|', content):
        t = m.group(1).strip()
        if t:
            titles.add(t)
    # 也从"标题:"字段提取
    for m in re.finditer(r'标题[：:]\s*(.{5,100})', content):
        t = m.group(1).strip()
        if t:
            titles.add(t)
    return titles

def get_existing_count(filepath):
    """获取已有条目数量（粗略）"""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # 数表格行数（粗略估计）
    rows = re.findall(r'\|.*\|.*\|', content)
    return max(0, len(rows) - 5)  # 减去表头等

def append_to_file(filepath, content):
    """追加内容到文件"""
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(content)

# ==================== B站抓取 ====================

def get_bilibili_ranking():
    """获取B站全站热榜"""
    apis = [
        ("https://api.bilibili.com/x/web-interface/ranking/v2?type=all&rid=36", "科技"),  # 科技区
        ("https://api.bilibili.com/x/web-interface/ranking/v2?type=all&rid=0", "全站"),    # 全站
    ]
    all_items = []
    for url, cat in apis:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            data = resp.json()
            if data.get("code") == 0:
                items = data.get("data", {}).get("list", [])
                for item in items:
                    item['_cat'] = cat
                all_items.extend(items)
                print(f"  [{cat}] 榜单: {len(items)} 条")
        except Exception as e:
            print(f"  [{cat}] 榜单 API 失败: {e}")
    return all_items

def get_bilibili_search():
    """通过B站搜索API获取AI相关视频"""
    keywords = [
        "AI人工智能", "ChatGPT", "大模型", "DeepSeek", "AIGC", "AI工具",
        "AI绘画", "AI视频", "AI编程", "AI教程", "AI数码", "AI应用",
        "机器学习", "神经网络", "开源模型", "AI科技"
    ]
    all_items = []
    seen_bvid = set()
    
    for kw in keywords:
        if len(all_items) >= 60:
            break
        url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={requests.utils.quote(kw)}&order=totalrank&page=1&pagesize=30"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            data = resp.json()
            if data.get("code") == 0:
                items = data.get("data", {}).get("result", [])
                for item in items:
                    bvid = item.get("bvid", "")
                    if bvid and bvid not in seen_bvid:
                        seen_bvid.add(bvid)
                        item['_cat'] = kw
                        all_items.append(item)
                print(f"  [搜索:{kw}] -> {len(items)} 条")
            else:
                print(f"  [搜索:{kw}] code={data.get('code')}")
        except Exception as e:
            print(f"  [搜索:{kw}] 失败: {e}")
        time.sleep(0.3)
    
    return all_items

def scrape_bilibili():
    """抓取B站AI内容"""
    print("\n========== B站 AI内容抓取 ==========")
    
    bilibili_file = os.path.join(DATA_DIR, f"bilibili-ai-{DATE_STR}.md")
    existing_titles = get_existing_titles(bilibili_file)
    existing_count = get_existing_count(bilibili_file)
    print(f"现有: {existing_count} 条 (基于表格行数)")
    print(f"已有标题去重集合: {len(existing_titles)} 个")
    
    # 获取数据
    ranking_items = get_bilibili_ranking()
    search_items = get_bilibili_search()
    
    # 合并去重
    seen_bvid = set()
    all_videos = []
    
    for v in ranking_items:
        bvid = v.get("bvid", "")
        if bvid and bvid not in seen_bvid:
            seen_bvid.add(bvid)
            all_videos.append(v)
    
    for v in search_items:
        bvid = v.get("bvid", "")
        if bvid and bvid not in seen_bvid:
            seen_bvid.add(bvid)
            all_videos.append(v)
    
    print(f"去重后合计: {len(all_videos)} 条视频")
    
    # 过滤AI相关内容
    ai_videos = []
    non_ai_videos = []
    for v in all_videos:
        title = clean_title(v.get("title", ""))
        if is_ai_related(title):
            ai_videos.append(v)
        else:
            non_ai_videos.append(v)
    
    print(f"AI相关: {len(ai_videos)} 条, 非AI: {len(non_ai_videos)} 条")
    
    # 优先取AI相关的，不够再从非AI中补充
    target_videos = ai_videos[:100]
    if len(target_videos) < 100:
        needed = 100 - len(target_videos)
        target_videos.extend(non_ai_videos[:needed])
    # 仍然不够100条则继续从ranking和search取
    if len(target_videos) < 100:
        all_remaining = [v for v in all_videos if v not in target_videos]
        target_videos.extend(all_remaining[:100 - len(target_videos)])
    
    target_videos = target_videos[:100]
    
    # 生成追加内容
    lines = []
    lines.append(f"\n\n---\n\n## 【追加批次】抖音+B站AI内容 14:00 追加\n")
    lines.append(f"追加时间: {NOW_STR}\n")
    lines.append(f"本批次: {len(target_videos)} 条\n")
    
    # B站表格
    lines.append(f"\n### B站 AI热门视频\n")
    lines.append("| # | 标题 | UP主 | 播放 | 点赞 | 弹幕 | 投币 | 收藏 | 日期 |")
    lines.append("|---|------|------|------|------|------|------|------|------|")
    
    start_idx = existing_count + 1
    for i, v in enumerate(target_videos, start=start_idx):
        title = clean_title(v.get("title", ""))
        # 跳过已存在的标题
        if title in existing_titles:
            continue
        
        author = v.get("owner", {}).get("name", v.get("author", "未知"))
        bvid = v.get("bvid", "")
        stat = v.get("stat", {})
        
        view = format_count(stat.get("view", 0))
        like = format_count(stat.get("like", 0))
        danmaku = format_count(stat.get("danmaku", 0))
        coin = format_count(stat.get("coin", 0))
        favorite = format_count(stat.get("favorite", 0))
        
        pubdate = v.get("pubdate", 0)
        if pubdate:
            try:
                date_str = datetime.fromtimestamp(pubdate).strftime("%Y-%m-%d")
            except:
                date_str = "未知"
        else:
            date_str = v.get("ctime", "")
            if date_str:
                try:
                    date_str = datetime.fromtimestamp(int(date_str)).strftime("%Y-%m-%d")
                except:
                    date_str = "未知"
            else:
                date_str = DATE_STR
        
        url = f"https://www.bilibili.com/video/{bvid}"
        
        lines.append(f"| {i} | {title} | @{author} | {view} | {like} | {danmaku} | {coin} | {favorite} | {date_str} |")
        existing_titles.add(title)  # 防止本批次重复
    
    result = "\n".join(lines)
    
    if len(target_videos) > 0:
        append_to_file(bilibili_file, result)
        print(f"[DONE] B站: 追加 {len(target_videos)} 条到 {bilibili_file}")
    else:
        print("[WARN] B站: 没有新内容可追加")
    
    return len(target_videos)

# ==================== 抖音抓取 ====================

def scrape_douyin():
    """通过Bing搜索抓取抖音AI内容"""
    print("\n========== 抖音 AI内容抓取 (Bing搜索) ==========")
    
    douyin_file = os.path.join(DATA_DIR, f"douyin-ai-{DATE_STR}.md")
    existing_titles = get_existing_titles(douyin_file)
    existing_count = get_existing_count(douyin_file)
    print(f"现有: {existing_count} 条")
    print(f"已有标题去重集合: {len(existing_titles)} 个")
    
    all_items = []
    
    # Bing搜索抖音AI相关内容
    keywords = [
        "site:douyin.com AI人工智能教程",
        "site:douyin.com ChatGPT技巧",
        "site:douyin.com 大模型应用",
        "site:douyin.com AI工具推荐",
        "site:douyin.com DeepSeek教程",
        "site:douyin.com AI绘画教学",
        "site:douyin.com AI视频制作",
        "抖音 AI科技 2026",
    ]
    
    seen_urls = set()
    
    for kw in keywords:
        if len(all_items) >= 80:
            break
        try:
            url = f"https://cn.bing.com/videos/search?q={requests.utils.quote(kw)}&FORM=HDRSC4"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            # 提取视频信息
            # 方式1: 从结构化数据提取
            items = re.findall(r'href="(https?://[^"]*douyin\.com[^"]*)"[^>]*>([^<]{10,200})<', html)
            for video_url, title in items:
                if 'douyin.com' not in video_url:
                    continue
                if video_url in seen_urls:
                    continue
                title = clean_title(title)
                if len(title) < 5:
                    continue
                seen_urls.add(video_url)
                all_items.append({
                    'title': title,
                    'url': video_url,
                    'author': '抖音用户',
                    'like': '未知',
                    'keyword': kw.replace('site:douyin.com ', '').replace(' ', '+'),
                })
            
            # 方式2: 从Bing视频结果提取
            items2 = re.findall(r'data-vid="[^"]*"[^>]*>.*?title="([^"]+)"[^>]*>.*?href="(https?://[^"]*douyin[^"]*)"', html, re.S)
            for title, video_url in items2:
                if video_url in seen_urls:
                    continue
                title = clean_title(title)
                if len(title) < 5:
                    continue
                seen_urls.add(video_url)
                all_items.append({
                    'title': title,
                    'url': video_url,
                    'author': '抖音用户',
                    'like': '未知',
                    'keyword': kw.replace('site:douyin.com ', '').replace(' ', '+'),
                })
            
            print(f"  [{kw[:30]}]: 发现 {len(items)} 条")
        except Exception as e:
            print(f"  [{kw[:30]}]: 失败 {e}")
        time.sleep(0.5)
    
    # 去重
    unique_items = []
    seen_titles_for_dedup = set()
    for item in all_items:
        t = item['title']
        if t not in seen_titles_for_dedup:
            seen_titles_for_dedup.add(t)
            unique_items.append(item)
    
    print(f"去重后: {len(unique_items)} 条")
    
    # 过滤AI相关内容
    ai_items = []
    for item in unique_items:
        if is_ai_related(item['title']):
            ai_items.append(item)
    
    print(f"AI相关: {len(ai_items)} 条")
    
    # 仍然不够100则补充
    target_items = ai_items[:100]
    if len(target_items) < 100:
        needed = 100 - len(target_items)
        for item in unique_items:
            if item not in target_items:
                target_items.append(item)
                if len(target_items) >= 100:
                    break
    
    target_items = target_items[:100]
    
    # 生成追加内容
    lines = []
    lines.append(f"\n\n---\n\n## 【追加批次】抖音+B站AI内容 14:00 追加\n")
    lines.append(f"追加时间: {NOW_STR}\n")
    lines.append(f"本批次: {len(target_items)} 条\n")
    
    # 抖音表格
    lines.append(f"\n### 抖音 AI热门视频\n")
    lines.append("| # | 标题 | 作者 | 点赞 | 话题 | 链接 |")
    lines.append("|---|------|------|------|------|------|")
    
    start_idx = existing_count + 1
    new_count = 0
    for i, item in enumerate(target_items, start=start_idx):
        title = item['title']
        if title in existing_titles:
            continue
        
        author = item.get('author', '抖音用户')
        like = item.get('like', '未知')
        keyword = item.get('keyword', 'AI')
        video_url = item.get('url', '')
        
        lines.append(f"| {i} | {title} | @{author} | {like} | #{keyword} | {video_url} |")
        existing_titles.add(title)
        new_count += 1
    
    result = "\n".join(lines)
    
    if new_count > 0:
        append_to_file(douyin_file, result)
        print(f"[DONE] 抖音: 追加 {new_count} 条到 {douyin_file}")
    else:
        print("[WARN] 抖音: 没有新内容可追加")
    
    return new_count

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("内容捕手 - 抖音+B站 AI内容抓取 (追加模式)")
    print(f"执行时间: {NOW_STR}")
    print("=" * 60)
    
    bilibili_count = scrape_bilibili()
    douyin_count = scrape_douyin()
    
    print("\n" + "=" * 60)
    print("抓取完成!")
    print(f"  B站新增: {bilibili_count} 条")
    print(f"  抖音新增: {douyin_count} 条")
    print(f"  目标文件:")
    print(f"    B站: bilibili-ai-{DATE_STR}.md")
    print(f"    抖音: douyin-ai-{DATE_STR}.md")
    print("=" * 60)
