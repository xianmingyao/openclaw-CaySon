"""
抖音AI内容抓取 - 头条/抖音热榜 + 多关键词覆盖
"""
import re
import os
import time
import requests
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
PC_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"

HEADERS = {
    "User-Agent": PC_UA,
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

DATE_STR = datetime.now().strftime("%Y-%m-%d")
NOW_STR = datetime.now().strftime("%Y-%m-%d %H:%M")

def clean_title(title):
    if not title:
        return "未知标题"
    title = re.sub(r'<[^>]+>', '', title)
    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    return title.strip()

def is_ai_related(title):
    ai_kws = [
        'ai', 'chatgpt', 'gpt', '大模型', 'llm', '深度学习', '机器学习',
        '神经网络', 'openai', '文心', '通义', 'kimi', '豆包', 'deepseek', 'gemini',
        'copilot', 'midjourney', 'diffusion', 'aigc', 'agent', '智能体', '生成式',
        'prompt', '提示词', '开源模型', 'sora', 'cursor', 'claude',
        '数字人', 'ai工具', 'ai应用', 'ai助手', 'ai创作', 'ai学习', 'ai教程',
        'langchain', 'rag', 'embedding', '向量', '微调', '部署', '推理',
        'python', '编程', '开发', '算法', '算力', 'gpu', '人工智能',
        '自动化', '机器人', '科技', '技术', 'ai绘画', 'ai视频', 'ai数码',
        '智能', '自动化', '算力', 'AI', 'ChatGPT', 'DeepSeek'
    ]
    text = (title or '').lower()
    return any(kw.lower() in text for kw in ai_kws)

def get_existing_titles(filepath):
    titles = set()
    if not os.path.exists(filepath):
        return titles
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    for m in re.finditer(r'标题[：:]\s*(.{5,100})', content):
        titles.add(m.group(1).strip())
    for m in re.finditer(r'\|\s*\d+\s*\|\s*([^|]{5,100})\s*\|', content):
        titles.add(m.group(1).strip())
    return titles

def get_existing_count(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    rows = re.findall(r'\|\s*\d+\s*\|', content)
    return max(0, len(rows) - 2)

def get_toutiao_hot():
    """头条热榜 - 包含大量AI科技内容"""
    all_items = []
    
    try:
        url = "https://www.toutiao.com/hot-event/hot-board?origin=hot_board&pd=article&activeList=hotboard_roll&channel=video&cate=21&streamCid=4001"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        
        if data.get("code") == 0:
            items = data.get("data", [])
            for item in items:
                title = item.get("Title", item.get("title", ""))
                if is_ai_related(title):
                    all_items.append({
                        'title': clean_title(title),
                        'url': item.get("article_url", item.get("url", "")),
                        'author': item.get("user_info", {}).get("name", "头条号"),
                        'like': item.get("digg_count", "未知"),
                        'keyword': '头条热榜AI',
                    })
            print(f"  头条热榜: {len(items)} 条, AI相关: {len(all_items)} 条")
    except Exception as e:
        print(f"  头条热榜失败: {e}")
    
    # 尝试头条视频热榜
    try:
        url2 = "https://www.toutiao.com/api/pc/feed/?category=video_news&utm_source=toutiao&max_behot_time=0&tag_video=1&频繁"
        resp2 = requests.get(url2, headers=HEADERS, timeout=10)
        data2 = resp2.json()
        print(f"  头条视频API: code={data2.get('code')}")
    except Exception as e:
        print(f"  头条视频API失败: {e}")
    
    return all_items

def get_douyin_toutiao_search():
    """通过头条搜索获取抖音相关内容"""
    all_items = []
    seen = set()
    
    keywords = [
        "AI人工智能教程", "ChatGPT技巧", "大模型应用", "AI工具推荐",
        "DeepSeek教程", "AI绘画教学", "AI视频制作", "AI编程",
        "AIGC创作", "AI助手使用", "开源大模型", "AI科技数码"
    ]
    
    for kw in keywords:
        if len(all_items) >= 50:
            break
        
        try:
            # 头条搜索API
            url = f"https://so.toutiao.com/search?keyword={requests.utils.quote(kw)}&pd=video"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.encoding = 'utf-8'
            html = resp.text
            
            # 提取视频标题和链接
            items = re.findall(
                r'<a[^>]+href="([^"]+)"[^>]*class="[^"]*video[^"]*"[^>]*>([^<]{10,200})<',
                html, re.I
            )
            for link, title in items:
                if 'douyin' in link.lower() and link not in seen:
                    seen.add(link)
                    all_items.append({
                        'title': clean_title(title) or kw,
                        'url': link,
                        'author': '抖音',
                        'like': '未知',
                        'keyword': kw,
                    })
            
            # 也从普通搜索结果提取
            items2 = re.findall(
                r'<a[^>]+href="([^"]*douyin[^"]*)"[^>]*>([^<]{5,100})<',
                html, re.I
            )
            for link, title in items2:
                if link not in seen:
                    seen.add(link)
                    all_items.append({
                        'title': clean_title(title) or kw,
                        'url': link,
                        'author': '抖音',
                        'like': '未知',
                        'keyword': kw,
                    })
            
            print(f"  [头条搜索:{kw[:15]}] 发现 {len(items)} 条")
        except Exception as e:
            print(f"  [头条搜索:{kw[:15]}] 错误 {e}")
        
        time.sleep(0.3)
    
    return all_items

def get_wanghong_search():
    """网红搜索 - 多平台聚合搜索"""
    all_items = []
    
    # 尝试不同的搜索引擎
    search_urls = [
        # 夸克搜索
        ("quark", "https://quark.sm.cn/s?q={}&type=video"),
        # 神马搜索
        ("shenma", "https://m.sm.cn/s?q={}&from=searchList&token=smcv"),
    ]
    
    keywords = [
        "抖音AI人工智能教程", "抖音ChatGPT技巧", "抖音大模型应用",
        "抖音DeepSeek教程", "抖音AI绘画"
    ]
    
    for name, template in search_urls:
        for kw in keywords:
            if len(all_items) >= 30:
                break
            
            try:
                url = template.format(requests.utils.quote(kw))
                resp = requests.get(url, headers=HEADERS, timeout=10)
                resp.encoding = 'utf-8'
                html = resp.text
                
                # 提取链接
                links = re.findall(r'href="(https?://[^"]*douyin[^"]*)"', html, re.I)
                for link in links[:3]:
                    if 'douyin.com' in link.lower():
                        all_items.append({
                            'title': kw,
                            'url': link,
                            'author': '抖音',
                            'like': '未知',
                            'keyword': kw,
                        })
                
                print(f"  [{name}:{kw[:15]}] {len(links)} 链接")
            except Exception as e:
                print(f"  [{name}:{kw[:15]}] 错误 {e}")
            
            time.sleep(0.3)
    
    return all_items

def scrape_douyin():
    filepath = os.path.join(DATA_DIR, f"douyin-ai-{DATE_STR}.md")
    existing_titles = get_existing_titles(filepath)
    existing_count = get_existing_count(filepath)
    
    print(f"\n========== 抖音 AI内容抓取 ==========")
    print(f"现有: {existing_count} 条, 已去重: {len(existing_titles)} 个")
    
    all_items = []
    
    # 方法1: 头条热榜
    items1 = get_toutiao_hot()
    all_items.extend(items1)
    
    # 方法2: 头条抖音搜索
    items2 = get_douyin_toutiao_search()
    all_items.extend(items2)
    
    # 方法3: 其他搜索引擎
    items3 = get_wanghong_search()
    all_items.extend(items3)
    
    # 去重
    seen_urls = {}
    unique_items = []
    for item in all_items:
        url = item['url']
        if url not in seen_urls:
            seen_urls[url] = True
            unique_items.append(item)
    
    print(f"\n去重后: {len(unique_items)} 条")
    
    # 过滤AI相关
    ai_items = [item for item in unique_items if is_ai_related(item['title'])]
    other_items = [item for item in unique_items if not is_ai_related(item['title'])]
    print(f"AI相关: {len(ai_items)} 条, 其他: {len(other_items)} 条")
    
    target_items = ai_items[:100]
    if len(target_items) < 100:
        target_items.extend(other_items[:100 - len(target_items)])
    target_items = target_items[:100]
    
    if not target_items:
        print("[WARN] 没有新内容")
        return 0
    
    lines = []
    lines.append(f"\n\n---\n\n## 【追加批次】抖音AI内容 {NOW_STR}")
    lines.append(f"本批次: {len(target_items)} 条\n")
    lines.append("\n### 抖音/头条 AI热门视频\n")
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
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(result)
    
    print(f"[DONE] 抖音: 追加 {new_count} 条")
    return new_count

if __name__ == "__main__":
    count = scrape_douyin()
    print(f"\n最终新增: {count} 条")
