#!/usr/bin/env python3
"""B站AI内容追加抓取 - 2026-04-09"""
import os, re, json
from datetime import datetime
from playwright.sync_api import sync_playwright

DATA_DIR = r"E:\workspace\content-hunter\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "bilibili-ai.md")
os.makedirs(DATA_DIR, exist_ok=True)

AI_KEYWORDS = [
    'AI', '人工智能', '机器学习', '深度学习', '神经网络', '大模型',
    'LLM', 'ChatGPT', 'GPT', 'AIGC', 'AGI', '编程', '代码', 'Python',
    'JavaScript', 'TensorFlow', 'PyTorch', 'OpenAI', 'Claude', 'DeepSeek',
    'Gemma', 'Gemini', 'Copilot', 'Cursor', 'V0', 'Midjourney', 'Sora',
    'StableDiffusion', 'Llama', 'Grok', '豆包', 'Kimi', '通义千问',
    '文心一言', '智谱AI', '讯飞星火', '华为盘古', '自动驾驶', '机器人',
    '具身智能', 'Agent', 'RAG', '向量数据库', '嵌入', 'embedding',
    'LangChain', 'LangGraph', 'RAG', '微调', 'fine-tune', '推理模型',
    'o1', 'o3', 'GPT-4', 'GPT-5', '多模态', 'VLA', '扩散模型', 'VAE',
    '强化学习', 'RLHF', 'DPO', '模型训练', '数据科学', '算法工程师',
    'AI创业', 'AI产品', 'AI投资', 'AI监管', 'AI安全', '对齐', '可解释AI'
]

def is_ai_related(title):
    title_lower = title.lower()
    for kw in AI_KEYWORDS:
        if kw.lower() in title_lower:
            return True
    return False

def scrape_bilibili_search():
    """通过Playwright抓B站搜索结果"""
    all_results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        keywords = ['AI人工智能', '大模型', 'ChatGPT', 'AIGC', '深度学习']
        
        for kw in keywords:
            print(f"  搜索: {kw}")
            page.goto(f"https://search.bilibili.com/all?keyword={kw}&type=video", 
                     wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(3000)
            
            # 向下滚动加载更多
            for _ in range(3):
                page.evaluate('window.scrollBy(0, 800)')
                page.wait_for_timeout(1000)
            
            # 提取视频标题和链接
            cards = page.query_selector_all('.video-item,.bili-video-card,.video-list-item')
            print(f"    找到 {len(cards)} 个卡片")
            
            for card in cards:
                try:
                    # 尝试多种选择器
                    title = ''
                    for sel in ['a.title', '.title', 'a', '[class*="title"]', '.bili-video-card__info--title']:
                        el = card.query_selector(sel)
                        if el:
                            title = el.inner_text().strip()
                            break
                    
                    if not title or len(title) < 5:
                        continue
                    if not is_ai_related(title):
                        continue
                    
                    # 获取作者
                    author = ''
                    for sel in ['.up-name', '.author', '[class*="up"]', '.bili-video-card__info--author']:
                        el = card.query_selector(sel)
                        if el:
                            author = el.inner_text().strip()
                            break
                    
                    # 获取播放量
                    stats = ''
                    for sel in ['.stat', '[class*="stat"]', '.bili-video-card__info--stats']:
                        el = card.query_selector(sel)
                        if el:
                            stats = el.inner_text().strip()
                            break
                    
                    # 获取链接
                    link = ''
                    link_el = card.query_selector('a')
                    if link_el:
                        href = link_el.get_attribute('href')
                        if href:
                            if href.startswith('//'):
                                link = 'https:' + href
                            elif href.startswith('/'):
                                link = 'https://www.bilibili.com' + href
                            else:
                                link = href
                    
                    all_results.append({
                        'title': title[:200],
                        'author': author,
                        'stats': stats,
                        'link': link,
                        'keyword': kw,
                        'platform': 'bilibili'
                    })
                except Exception as e:
                    continue
        
        browser.close()
    
    return all_results

def scrape_bilibili_knowledge_rank():
    """抓B站知识区排行榜"""
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        page = browser.new_page()
        
        # 尝试知识区排行榜
        print("  抓取B站知识区排行...")
        page.goto('https://www.bilibili.com/v/popular/rank/knowledge',
                 wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(3000)
        
        for _ in range(5):
            page.evaluate('window.scrollBy(0, 600)')
            page.wait_for_timeout(800)
        
        # 提取内容
        items = page.query_selector_all('li, .rank-item, .video-item')
        print(f"    找到 {len(items)} 个条目")
        
        for item in items:
            try:
                # 获取标题
                title = ''
                for sel in ['a.title', '.title', '.video-title', '[class*="title"]']:
                    el = item.query_selector(sel)
                    if el:
                        title = el.inner_text().strip()
                        break
                
                if not title or len(title) < 10:
                    continue
                if not is_ai_related(title):
                    continue
                
                # 获取作者
                author = ''
                for sel in ['.up-name', '.author', '.up', '[class*="up-name"]']:
                    el = item.query_selector(sel)
                    if el:
                        author = el.inner_text().strip()
                        break
                
                # 获取统计数据
                stats = ''
                stat_els = item.query_selector_all('.stat span, .stats, [class*="stat"]')
                stats = ' '.join([s.inner_text().strip() for s in stat_els if s.inner_text().strip()])
                
                results.append({
                    'title': title[:200],
                    'author': author,
                    'stats': stats,
                    'link': '',
                    'keyword': '知识区排行',
                    'platform': 'bilibili'
                })
            except Exception as e:
                continue
        
        browser.close()
    
    return results

def deduplicate(existing_file, new_results):
    """基于标题去重"""
    existing_titles = set()
    if os.path.exists(existing_file):
        with open(existing_file, encoding='utf-8') as f:
            content = f.read()
        # 提取所有已存在的标题
        for line in content.split('\n'):
            m = re.search(r'第\d+条[:：]\s*\*\*([^*]+)\*\*', line)
            if m:
                existing_titles.add(m.group(1).strip()[:80])
    
    deduped = []
    for r in new_results:
        title_short = r['title'][:80]
        if title_short not in existing_titles:
            existing_titles.add(title_short)
            deduped.append(r)
    
    return deduped

if __name__ == '__main__':
    print("=== B站AI内容追加抓取 2026-04-09 ===")
    
    # 抓取
    print("\n[1] 抓取B站搜索结果...")
    search_results = scrape_bilibili_search()
    print(f"    搜索抓到 {len(search_results)} 条")
    
    print("\n[2] 抓取B站知识区排行...")
    rank_results = scrape_bilibili_knowledge_rank()
    print(f"    排行抓到 {len(rank_results)} 条")
    
    # 合并
    all_new = search_results + rank_results
    print(f"\n总共抓到 {len(all_new)} 条")
    
    # 去重
    deduped = deduplicate(OUTPUT_FILE, all_new)
    print(f"去重后 {len(deduped)} 条（排除已存在于文件中的标题）")
    
    if not deduped:
        print("没有新内容要追加")
    else:
        # 追加写入
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n\n## B站AI内容追加批次 — {timestamp}\n")
            f.write(f"本批次新增: {len(deduped)} 条\n\n")
            
            for i, r in enumerate(deduped, 1):
                f.write(f"### 第{i}条\n")
                f.write(f"- 标题: {r['title']}\n")
                f.write(f"- UP主: {r['author'] or '未知'}\n")
                f.write(f"- 播放数据: {r['stats'] or '未知'}\n")
                f.write(f"- 来源关键词: {r['keyword']}\n")
                if r['link']:
                    f.write(f"- 链接: {r['link']}\n")
                f.write(f"- 抓取时间: {timestamp}\n")
                f.write("\n")
        
        print(f"\n✅ 已追加 {len(deduped)} 条到: {OUTPUT_FILE}")
        
        # 统计
        with open(OUTPUT_FILE, encoding='utf-8') as f:
            content = f.read()
        items = re.findall(r'### 第\d+条', content)
        print(f"文件现在共 {len(items)} 条内容")
