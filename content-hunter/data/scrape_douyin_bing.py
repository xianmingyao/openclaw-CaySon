"""
抖音AI内容抓取 - Bing普通搜索版
"""
import re
import os
import time
import requests
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

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
        t = m.group(1).strip()
        if t:
            titles.add(t)
    # 从表格第二列提取
    for m in re.finditer(r'\|\s*\d+\s*\|\s*([^|]{5,100})\s*\|', content):
        t = m.group(1).strip()
        if t:
            titles.add(t)
    return titles

def get_existing_count(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    rows = re.findall(r'\|\s*\d+\s*\|', content)
    return max(0, len(rows) - 2)

def search_bing_douyin():
    """Bing普通搜索抖音AI内容"""
    all_items = []
    seen_urls = set()
    
    # 搜索词组合
    search_queries = [
        "抖音 AI人工智能教程 2026",
        "抖音 ChatGPT技巧 大全",
        "抖音 大模型 应用演示",
        "抖音 AI工具 推荐 科技",
        "抖音 DeepSeek 使用教程",
        "抖音 AI绘画 Stable Diffusion",
        "抖音 AI视频生成 Sora",
        "抖音 AI编程 Cursor",
        "抖音 AI助手 使用技巧",
        "抖音 人工智能 科技数码",
        "抖音 AI数码产品 测评",
        "抖音 科技 AI技术",
    ]
    
    for kw in search_queries:
        if len(all_items) >= 80:
            break
        
        try:
            # 普通Bing搜索（非视频搜索）
            url = f"https://cn.bing.com/search?q={requests.utils.quote(kw)}&first=0&FORM=HDRESC"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            # 提取抖音链接
            # 匹配各种抖音URL格式
            douyin_patterns = [
                r'href="(https?://(?:www\.)?douyin\.com/(?:video|note)/\d+[^"]*)"',
                r'href="(https?://v\.douyin\.com/[a-zA-Z0-9]+)"',
                r'href="(https?://[^"]*douyin[^"]*video[^"]*\d{10,}[^"]*)"',
            ]
            
            for pattern in douyin_patterns:
                matches = re.findall(pattern, html, re.I)
                for m in matches:
                    if m in seen_urls:
                        continue
                    if 'douyin.com' not in m.lower():
                        continue
                    seen_urls.add(m)
            
            # 从搜索结果中提取标题和URL
            # Bing搜索结果中的条目格式
            results = re.findall(
                r'<li[^>]*class="[^"]*b_algo[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>([^<]*)<\/a>(.*?)<div[^>]*class="[^"]*b_desc[^"]*"[^>]*>(.*?)</li>',
                html, re.S | re.I
            )
            
            for link_url, link_text, desc in results:
                if len(all_items) >= 80:
                    break
                if 'douyin.com' not in link_url.lower():
                    continue
                if link_url in seen_urls:
                    continue
                
                title = clean_title(link_text)
                if len(title) < 5:
                    # 从描述中提取
                    desc_clean = re.sub(r'<[^>]+>', '', desc)
                    desc_clean = clean_title(desc_clean)
                    if len(desc_clean) > 10:
                        title = desc_clean[:80]
                
                if len(title) < 5:
                    continue
                
                seen_urls.add(link_url)
                all_items.append({
                    'title': title,
                    'url': link_url,
                    'author': '抖音用户',
                    'like': '未知',
                    'keyword': kw.replace('抖音 ', '').replace(' ', '+'),
                })
            
            # 也从普通URL提取
            for url_found in seen_urls:
                if len(all_items) >= 80:
                    break
                exists = any(item['url'] == url_found for item in all_items)
                if not exists and 'douyin.com' in url_found.lower():
                    # 尝试从URL猜测标题
                    all_items.append({
                        'title': f'抖音AI内容_{url_found[-20:]}',
                        'url': url_found,
                        'author': '抖音用户',
                        'like': '未知',
                        'keyword': kw.replace('抖音 ', '').replace(' ', '+'),
                    })
            
            print(f"  [{kw[:25]}]: 发现 {len(all_items)} 条")
            
        except Exception as e:
            print(f"  [{kw[:25]}]: 错误 {e}")
        
        time.sleep(1)
    
    return all_items

def search_baidu_douyin():
    """百度搜索抖音AI内容（备选）"""
    all_items = []
    seen_urls = set()
    
    keywords = [
        "抖音 AI教程 site:douyin.com",
        "ChatGPT 使用技巧 site:douyin.com",
        "大模型 应用 site:douyin.com",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    }
    
    for kw in keywords:
        if len(all_items) >= 40:
            break
        try:
            url = f"https://www.baidu.com/s?wd={requests.utils.quote(kw)}&rn=20"
            resp = requests.get(url, headers=headers, timeout=15)
            resp.encoding = 'utf-8'
            html = resp.text
            
            # 提取抖音链接
            matches = re.findall(r'href="(https?://[^"]*douyin[^"]*)"', html)
            for m in matches:
                if 'douyin.com' in m and m not in seen_urls:
                    seen_urls.add(m)
            
            # 提取标题
            titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.S)
            for title_block in titles[:20]:
                title = clean_title(title_block)
                if len(title) > 5:
                    for url in list(seen_urls)[:5]:
                        if url not in [item['url'] for item in all_items]:
                            all_items.append({
                                'title': title,
                                'url': url,
                                'author': '抖音用户',
                                'like': '未知',
                                'keyword': 'AI',
                            })
            
            print(f"  [百度:{kw[:20]}] 发现 {len(matches)} 链接")
        except Exception as e:
            print(f"  [百度:{kw[:20]}] 错误 {e}")
        
        time.sleep(1)
    
    return all_items

def scrape_douyin():
    filepath = os.path.join(DATA_DIR, f"douyin-ai-{DATE_STR}.md")
    existing_titles = get_existing_titles(filepath)
    existing_count = get_existing_count(filepath)
    
    print(f"\n========== 抖音 AI内容抓取 ==========")
    print(f"现有: {existing_count} 条")
    print(f"已有标题: {len(existing_titles)} 个")
    
    # Bing搜索
    items1 = search_bing_douyin()
    print(f"Bing搜索: {len(items1)} 条")
    
    # 百度搜索（备选）
    items2 = search_baidu_douyin()
    print(f"百度搜索: {len(items2)} 条")
    
    # 合并
    seen_urls = {}
    all_items = []
    for item in items1 + items2:
        url = item['url']
        if url not in seen_urls:
            seen_urls[url] = True
            all_items.append(item)
    
    print(f"去重合并: {len(all_items)} 条")
    
    # 过滤AI相关
    ai_items = [item for item in all_items if is_ai_related(item['title'])]
    print(f"AI相关: {len(ai_items)} 条")
    
    target_items = ai_items[:100]
    if len(target_items) < 100:
        target_items = target_items + [item for item in all_items if item not in target_items]
    target_items = target_items[:100]
    
    # 生成内容
    lines = []
    lines.append(f"\n\n---\n\n## 【Bing/百度搜索追加批次】抖音AI内容 {NOW_STR}")
    lines.append(f"本批次: {len(target_items)} 条\n")
    lines.append("\n### 抖音 AI热门视频\n")
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
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(result)
        print(f"[DONE] 抖音: 追加 {new_count} 条")
    else:
        print("[WARN] 抖音: 没有新内容")
    
    return new_count

if __name__ == "__main__":
    count = scrape_douyin()
    print(f"\n结果: {count} 条新内容")
