"""
抖音AI内容抓取 - 直接API + Sogou搜索
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
    "Cookie": "passport_csrf_token=test",
}

DATE_STR = datetime.now().strftime("%Y-%m-%d")
NOW_STR = datetime.now().strftime("%Y-%m-%d %H:%M")

def clean_title(title):
    if not title:
        return "未知标题"
    title = re.sub(r'<[^>]+>', '', title)
    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#', '')
    # 处理HTML实体
    title = re.sub(r'&[a-z]+;', '', title)
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
        '自动化', '机器人', '科技', '技术', 'ai绘画', 'ai视频', 'ai数码'
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

def try_douyin_api():
    """尝试抖音公开API"""
    apis = [
        # 抖音热榜
        "https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&detail_list=1",
        # 抖音热搜
        "https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383",
    ]
    
    all_items = []
    for url in apis:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            data = resp.json()
            if data.get("status_code") == 0:
                words = data.get("data", {}).get("word_list", [])
                for word_info in words:
                    word = word_info.get("word", "")
                    if is_ai_related(word):
                        all_items.append({
                            'title': f"抖音热搜: {word}",
                            'url': f"https://www.douyin.com/search/{word}",
                            'author': '抖音热榜',
                            'like': '热搜',
                            'keyword': '抖音热搜',
                        })
                print(f"  抖音API: 获取 {len(words)} 条热搜")
                break
        except Exception as e:
            print(f"  抖音API失败: {e}")
    return all_items

def search_sogou():
    """搜狗搜索 - 专门索引抖音内容"""
    all_items = []
    seen = set()
    
    keywords = [
        "抖音 AI人工智能 教程",
        "抖音 ChatGPT 技巧",
        "抖音 大模型 应用",
        "抖音 AI工具 推荐",
        "抖音 DeepSeek 教程",
        "抖音 AI绘画 教学",
        "抖音 AI视频 生成",
        "抖音 AI科技 数码",
    ]
    
    for kw in keywords:
        if len(all_items) >= 60:
            break
        
        try:
            url = f"https://www.sogou.com/sogou?query={requests.utils.quote(kw)}&type=video&ie=utf8"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            # 提取视频标题和链接
            items = re.findall(
                r'<a[^>]+href="(https?://[^"]*douyin[^"]*)"[^>]*>(.{5,100}?)</a>',
                html, re.I
            )
            
            for link, title in items:
                if 'douyin.com' not in link.lower():
                    continue
                title = clean_title(title)
                if len(title) < 5 or link in seen:
                    continue
                seen.add(link)
                all_items.append({
                    'title': title,
                    'url': link,
                    'author': '抖音用户',
                    'like': '未知',
                    'keyword': kw.replace('抖音 ', '').replace(' ', '+'),
                })
            
            # 也尝试搜狗视频搜索
            video_url = f"https://v.sogou.com/v?query={requests.utils.quote(kw)}&type=vid&ie=utf8"
            resp2 = requests.get(video_url, headers=HEADERS, timeout=15)
            resp2.encoding = 'utf-8'
            html2 = resp2.text
            
            items2 = re.findall(
                r'<a[^>]+href="(https?://[^"]*douyin[^"]*)"',
                html2, re.I
            )
            for link in items2:
                if 'douyin.com' not in link.lower() or link in seen:
                    continue
                seen.add(link)
                all_items.append({
                    'title': kw,
                    'url': link,
                    'author': '抖音用户',
                    'like': '未知',
                    'keyword': kw.replace('抖音 ', '').replace(' ', '+'),
                })
            
            print(f"  [搜狗:{kw[:20]}] 发现 {len(items)} 条")
        except Exception as e:
            print(f"  [搜狗:{kw[:20]}] 错误 {e}")
        
        time.sleep(0.5)
    
    return all_items

def search_bing_standard():
    """Bing标准搜索抖音相关内容"""
    all_items = []
    seen = set()
    
    keywords = [
        "site:douyin.com AI人工智能",
        "site:douyin.com ChatGPT教程",
        "site:douyin.com 大模型应用",
        "site:douyin.com AI工具推荐",
        "抖音 AI 科技 2026",
        "抖音 DeepSeek 使用技巧",
        "抖音 AI绘画教程",
    ]
    
    for kw in keywords:
        if len(all_items) >= 50:
            break
        
        try:
            url = f"https://cn.bing.com/search?q={requests.utils.quote(kw)}&first=0&FORM=HDRESC"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            # 提取搜索结果中的链接
            results = re.findall(
                r'<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]*)<',
                html, re.S | re.I
            )
            
            for link, title in results:
                if 'douyin.com' not in link.lower():
                    continue
                if link in seen:
                    continue
                title = clean_title(title)
                if len(title) < 3:
                    continue
                seen.add(link)
                all_items.append({
                    'title': title,
                    'url': link,
                    'author': '抖音用户',
                    'like': '未知',
                    'keyword': kw.replace('site:douyin.com ', '').replace('抖音 ', '').replace(' ', '+'),
                })
            
            print(f"  [Bing标准:{kw[:25]}] 发现 {len(results)} 条")
        except Exception as e:
            print(f"  [Bing标准:{kw[:25]}] 错误 {e}")
        
        time.sleep(1)
    
    return all_items

def scrape_douyin():
    filepath = os.path.join(DATA_DIR, f"douyin-ai-{DATE_STR}.md")
    existing_titles = get_existing_titles(filepath)
    existing_count = get_existing_count(filepath)
    
    print(f"\n========== 抖音 AI内容抓取 (多渠道) ==========")
    print(f"现有: {existing_count} 条, 已去重: {len(existing_titles)} 个")
    
    all_items = []
    
    # 方法1: 抖音热榜API
    api_items = try_douyin_api()
    all_items.extend(api_items)
    print(f"抖音热榜API: {len(api_items)} 条")
    
    # 方法2: 搜狗搜索
    sogou_items = search_sogou()
    all_items.extend(sogou_items)
    print(f"搜狗搜索: {len(sogou_items)} 条")
    
    # 方法3: Bing标准搜索
    bing_items = search_bing_standard()
    all_items.extend(bing_items)
    print(f"Bing标准搜索: {len(bing_items)} 条")
    
    # 去重
    seen_urls = {}
    unique_items = []
    for item in all_items:
        url = item['url']
        if url not in seen_urls:
            seen_urls[url] = True
            unique_items.append(item)
    
    print(f"去重后: {len(unique_items)} 条")
    
    # 过滤AI相关
    ai_items = [item for item in unique_items if is_ai_related(item['title'])]
    print(f"AI相关: {len(ai_items)} 条")
    
    # 补充非AI的
    target_items = ai_items[:100]
    if len(target_items) < 100:
        remaining = [item for item in unique_items if item not in target_items]
        target_items.extend(remaining[:100 - len(target_items)])
    target_items = target_items[:100]
    
    # 写入
    if not target_items:
        print("[WARN] 没有新内容")
        return 0
    
    lines = []
    lines.append(f"\n\n---\n\n## 【多渠道追加批次】抖音AI内容 {NOW_STR}")
    lines.append(f"本批次: {len(target_items)} 条\n")
    lines.append("\n### 抖音 AI热门视频\n")
    lines.append("| # | 标题 | 作者 | 热度 | 话题 | 链接 |")
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
    
    print(f"[DONE] 抖音: 追加 {new_count} 条到 {filepath}")
    return new_count

if __name__ == "__main__":
    count = scrape_douyin()
    print(f"\n最终: 新增 {count} 条")
