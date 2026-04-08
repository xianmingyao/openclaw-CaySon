#!/usr/bin/env python3
"""
内容捕手 - 抖音&B站AI技术内容抓取
使用requests + BeautifulSoup 抓取搜索结果页面
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def clean_text(text):
    """清理文本"""
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_douyin_search(html):
    """解析抖音搜索结果页面"""
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    # 抖音搜索结果通常在script标签中以JSON形式存在
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and 'RENDER_DATA' in script.string:
            try:
                # 提取JSON数据
                match = re.search(r'"initialState"\s*:\s*(\{.*?})\s*</script>', script.string, re.DOTALL)
                if match:
                    data = json.loads(match.group(1))
                    # 遍历数据提取视频信息
                    if 'video' in str(data):
                        pass
            except:
                pass
    
    # 也尝试从页面DOM中提取
    video_items = soup.select('div[data-e2e="search-card-list"] ul li')
    if not video_items:
        video_items = soup.select('ul li[data-e2e]')
    
    return results

def fetch_douyin_ai():
    """抓取抖音AI技术内容"""
    results = []
    keywords = ['AI人工智能', 'ChatGPT', '大模型', 'AIGC', 'AI工具']
    
    for kw in keywords:
        url = f'https://www.douyin.com/search/{kw}?type=video'
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            print(f"[抖音] 搜索 '{kw}': 状态码={resp.status_code}")
            
            # 尝试从页面提取视频信息
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 提取SEO信息
            title_tags = soup.find_all('script', type='application/ld+json')
            for tag in title_tags:
                try:
                    data = json.loads(tag.string)
                    if data.get('@type') == 'ItemList':
                        for item in data.get('itemListElement', []):
                            results.append({
                                'platform': 'douyin',
                                'keyword': kw,
                                'title': item.get('name', ''),
                                'url': item.get('url', ''),
                                'description': item.get('description', ''),
                            })
                except:
                    pass
            
            # 从meta description提取
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                desc = meta_desc.get('content', '')
                if desc and '抖音' in desc:
                    print(f"  Meta描述: {desc[:100]}")
            
            time.sleep(1)
        except Exception as e:
            print(f"[抖音] 搜索 '{kw}' 出错: {e}")
    
    return results

def fetch_bilibili_ai():
    """抓取B站AI技术内容"""
    results = []
    keywords = ['AI人工智能', 'ChatGPT', '大模型', 'AIGC', 'LLM', '人工智能技术']
    
    for kw in keywords:
        url = f'https://search.bilibili.com/all?keyword={kw}&order=totalrank&duration=0&tids_1=0'
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            print(f"[B站] 搜索 '{kw}': 状态码={resp.status_code}")
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 尝试从script中提取数据
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('window.__INITIAL_STATE__' in script.string or 'window.__playinfo__' in script.string):
                    try:
                        # 提取JSON
                        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?})\s*;?\s*</script>', script.string, re.DOTALL)
                        if match:
                            data = json.loads(match.group(1))
                            print(f"  找到初始状态数据")
                    except Exception as e:
                        pass
            
            # 从video卡片提取
            video_cards = soup.select('.video-item-list .video-item a')
            if not video_cards:
                video_cards = soup.select('a[href*="/video/"]')
            
            for card in video_cards[:20]:
                title = clean_text(card.get('title', ''))
                href = card.get('href', '')
                if title and '/video/' in href:
                    results.append({
                        'platform': 'bilibili',
                        'keyword': kw,
                        'title': title,
                        'url': f'https://bilibili.com{href}' if href.startswith('/') else href,
                    })
            
            time.sleep(1)
        except Exception as e:
            print(f"[B站] 搜索 '{kw}' 出错: {e}")
    
    return results

def main():
    print("=" * 60)
    print("内容捕手 - AI技术热门内容抓取")
    print("=" * 60)
    
    # 抓取抖音
    print("\n[1/2] 正在抓取抖音AI技术内容...")
    douyin_results = fetch_douyin_ai()
    print(f"  抖音: 获得 {len(douyin_results)} 条结果")
    
    # 抓取B站
    print("\n[2/2] 正在抓取B站AI技术内容...")
    bilibili_results = fetch_bilibili_ai()
    print(f"  B站: 获得 {len(bilibili_results)} 条结果")
    
    # 保存结果
    output_dir = r'E:\workspace\content-hunter\data'
    os.makedirs(output_dir, exist_ok=True)
    
    # 抖音结果
    douyin_file = os.path.join(output_dir, 'douyin-ai.md')
    with open(douyin_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n# 抖音AI技术热门内容\n")
        f.write(f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for i, item in enumerate(douyin_results, 1):
            f.write(f"### 第{i}条\n")
            f.write(f"- 标题: {item.get('title', 'N/A')}\n")
            f.write(f"- 关键词: {item.get('keyword', 'N/A')}\n")
            f.write(f"- 链接: {item.get('url', 'N/A')}\n")
            f.write(f"- 内容总结: {item.get('description', '抖音视频内容')}\n\n")
    
    # B站结果
    bilibili_file = os.path.join(output_dir, 'bilibili-ai.md')
    with open(bilibili_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n# B站AI技术热门内容\n")
        f.write(f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        for i, item in enumerate(bilibili_results, 1):
            f.write(f"### 第{i}条\n")
            f.write(f"- 标题: {item.get('title', 'N/A')}\n")
            f.write(f"- 关键词: {item.get('keyword', 'N/A')}\n")
            f.write(f"- 链接: {item.get('url', 'N/A')}\n")
            f.write(f"- 内容总结: B站AI技术视频内容\n\n")
    
    print(f"\n结果已追加保存到:")
    print(f"  抖音: {douyin_file}")
    print(f"  B站: {bilibili_file}")
    
    return douyin_results, bilibili_results

if __name__ == '__main__':
    main()
