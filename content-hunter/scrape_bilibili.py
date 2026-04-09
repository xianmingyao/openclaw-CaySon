#!/usr/bin/env python3
"""B站AI内容抓取 - 使用Playwright"""
import os, json, re
from datetime import datetime
from playwright.sync_api import sync_playwright

DATA_DIR = r"E:\workspace\content-hunter\data"
os.makedirs(DATA_DIR, exist_ok=True)

def clean_html(text):
    """清理HTML实体"""
    entities = {'&amp;': '&', '&lt;': '<', '&gt;': '>', '&#32;': ' ', '&#39;': "'"}
    for k, v in entities.items():
        text = text.replace(k, v)
    return text

def scrape_bilibili_ai(keyword="AI人工智能", pages=5):
    """抓取B站AI相关内容"""
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        for page_num in range(1, pages + 1):
            print(f"  抓取第 {page_num}/{pages} 页...")
            url = f"https://search.bilibili.com/all?keyword={keyword}&page={page_num}&type=video"
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            
            # 提取视频卡片
            videos = page.query_selector_all('.video-item')
            if not videos:
                # 备选：查找更多选择器
                videos = page.query_selector_all('[class*="video-item"]')
                if not videos:
                    videos = page.query_selector_all('li, .bili-video-card')
            
            print(f"    找到 {len(videos)} 个元素")
            
            # 尝试提取文本内容
            page_text = page.inner_text('body')
            lines = [l.strip() for l in page_text.split('\n') if l.strip() and len(l.strip()) > 5]
            
            for i, line in enumerate(lines):
                # 过滤明显不是视频标题的行
                if any(skip in line for skip in ['登录', '注册', '下载', 'bilibili', 'Copyright', '沪ICP备', '隐私', '用户协议', '关于']):
                    continue
                if len(line) < 10:
                    continue
                # 检查是否有播放量/点赞等数字
                if re.search(r'[\d万]+', line):
                    results.append({
                        'title': line[:200],
                        'platform': 'bilibili',
                        'keyword': keyword,
                        'page': page_num,
                        'raw': line[:300]
                    })
        
        browser.close()
    
    return results

def scrape_bilibili_rank_ai():
    """从B站排行榜-知识分类抓AI内容"""
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        page = browser.new_page()
        
        # 知识分类排行
        print("  抓取B站知识分类排行榜...")
        page.goto('https://www.bilibili.com/v/popular/rank/knowledge', wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)
        
        # 提取排行榜内容
        items = page.query_selector_all('li')
        for item in items:
            try:
                title_el = item.query_selector('a.title, .title, [class*="title"]')
                author_el = item.query_selector('.author, [class*="author"], .up-name')
                stat_el = item.query_selector('.stat, [class*="stat"]')
                
                title = title_el.inner_text() if title_el else ''
                author = author_el.inner_text() if author_el else ''
                stats = stat_el.inner_text() if stat_el else ''
                
                if title and len(title) > 5:
                    # 检查是否与AI相关
                    ai_keywords = ['AI', '人工智能', '机器学习', '深度学习', '神经网络', '大模型', 'LLM', 'ChatGPT', 'GPT', 'AIGC', 'AGI', '算法', '编程', '代码', 'Python', '数据科学', 'LLM', 'Gemma', 'Claude', 'DeepSeek', 'OpenAI', 'Midjourney', 'Sora', 'StableDiffusion']
                    if any(kw.lower() in title.lower() for kw in ai_keywords):
                        results.append({
                            'title': title.strip(),
                            'author': author.strip(),
                            'stats': stats.strip(),
                            'platform': 'bilibili',
                            'category': 'knowledge_rank'
                        })
            except Exception as e:
                continue
        
        browser.close()
    
    return results

if __name__ == '__main__':
    print("=== B站AI内容抓取 ===")
    
    # 方法1: 从知识排行榜获取
    print("\n[方法1] 从B站知识排行榜获取...")
    rank_results = scrape_bilibili_rank_ai()
    print(f"  排行榜找到 {len(rank_results)} 条AI相关内容")
    
    # 方法2: 搜索方式
    print("\n[方法2] 从B站搜索获取...")
    search_results = scrape_bilibili_ai(pages=5)
    print(f"  搜索找到 {len(search_results)} 条结果")
    
    # 合并去重
    all_results = rank_results + search_results
    titles_seen = set()
    unique_results = []
    for r in all_results:
        title = r.get('title', '')[:50]
        if title and title not in titles_seen:
            titles_seen.add(title)
            unique_results.append(r)
    
    print(f"\n去重后共 {len(unique_results)} 条")
    
    # 写入文件（追加模式）
    output_file = os.path.join(DATA_DIR, 'bilibili-ai.md')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n## B站AI内容抓取报告 - {timestamp}\n")
        f.write(f"总计: {len(unique_results)} 条\n\n")
        for i, r in enumerate(unique_results, 1):
            f.write(f"{i}. **{r.get('title', 'N/A')}**\n")
            f.write(f"   - 作者: {r.get('author', 'N/A')}\n")
            f.write(f"   - 数据: {r.get('stats', 'N/A')}\n")
            f.write(f"   - 来源: {r.get('platform', 'bilibili')} | {r.get('category', 'search')}\n\n")
    
    print(f"\n✅ 已追加到: {output_file}")
