# -*- coding: utf-8 -*-
"""
内容捕手 - 百度搜索批量抓取抖音/B站AI内容
"""
import urllib.request
import urllib.parse
import re
import time
import os
import sys

# Fix stdout for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def baidu_search(query, num=20):
    """百度搜索，返回HTML"""
    q = urllib.parse.quote(query)
    url = f'https://www.baidu.com/s?wd={q}&rn={num}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.baidu.com/',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

def extract_baidu_results(html, domain):
    """从百度搜索结果HTML中提取标题+链接+摘要"""
    results = []
    # 百度搜索结果条目
    items = re.findall(r'<div class="result[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not items:
        items = re.findall(r'<div class="c-container[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    
    for item in items:
        # 链接
        link_match = re.search(r'href="(https?://[^"]+bilibili[^"]+)"', item)
        if not link_match:
            link_match = re.search(r'href="(https?://[^"]+douyin[^"]+)"', item)
        if not link_match:
            continue
        link = link_match.group(1)
        
        # 过滤域名
        if domain not in link:
            continue
        
        # 标题
        title_match = re.search(r'<h3[^>]*>(.*?)</h3>', item, re.DOTALL)
        if not title_match:
            title_match = re.search(r'<a[^>]*class="[^"]*t[^"]*"[^>]*>(.*?)</a>', item, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', title_match.group(1) if title_match else '').strip()
        
        # 摘要
        abs_match = re.search(r'<span class="[^"]*c-color-gray[^"]*"[^>]*>(.*?)</span>', item, re.DOTALL)
        if not abs_match:
            abs_match = re.search(r'<div class="[^"]*c-abstract[^"]*"[^>]*>(.*?)</div>', item, re.DOTALL)
        snippet = re.sub(r'<[^>]+>', '', abs_match.group(1) if abs_match else '').strip()
        
        if title and len(title) > 5:
            results.append({
                'title': title[:100],
                'url': link[:200],
                'snippet': snippet[:200]
            })
    
    return results

def main():
    data_dir = 'E:/workspace/content-hunter/data/'
    os.makedirs(data_dir, exist_ok=True)
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    
    all_douyin = []
    all_bilibili = []
    
    # 抖音搜索词
    douyin_queries = [
        'site:douyin.com AI人工智能 教程 2026',
        'site:douyin.com ChatGPT 使用技巧',
        'site:douyin.com AI绘画 教程',
        'site:douyin.com 大模型 LLM',
        'site:douyin.com AIGC 创作',
        'site:douyin.com AI工具 效率',
        'site:douyin.com 深度学习 教程',
        'site:douyin.com AI视频 Sora',
        'site:douyin.com 机器学习 入门',
        'site:douyin.com AI写作 技巧',
    ]
    
    # B站搜索词
    bilibili_queries = [
        'site:bilibili.com AI人工智能 教程 2026',
        'site:bilibili.com ChatGPT 使用教程',
        'site:bilibili.com stable diffusion AI绘画',
        'site:bilibili.com 大模型 LLM 教程',
        'site:bilibili.com AIGC 人工智能创作',
        'site:bilibili.com 深度学习 神经网络',
        'site:bilibili.com 机器学习 python',
        'site:bilibili.com AI视频生成 Sora',
        'site:bilibili.com AI绘画 Midjourney',
        'site:bilibili.com AI工具 效率提升',
    ]
    
    print('=' * 60)
    print('[1/2] 百度搜索: 抖音 AI内容')
    print('=' * 60)
    for q in douyin_queries:
        print(f'  [{q[:50]}...]', end=' ')
        html = baidu_search(q)
        if html.startswith('ERROR'):
            print(f'ERROR: {html}')
            continue
        items = extract_baidu_results(html, 'douyin.com')
        print(f'找到 {len(items)} 条')
        all_douyin.extend(items)
        time.sleep(1)
    
    print('\n' + '=' * 60)
    print('[2/2] 百度搜索: B站 AI内容')
    print('=' * 60)
    for q in bilibili_queries:
        print(f'  [{q[:50]}...]', end=' ')
        html = baidu_search(q)
        if html.startswith('ERROR'):
            print(f'ERROR: {html}')
            continue
        items = extract_baidu_results(html, 'bilibili.com')
        print(f'找到 {len(items)} 条')
        all_bilibili.extend(items)
        time.sleep(1)
    
    # 去重
    def dedup(items):
        seen = set()
        out = []
        for r in items:
            key = r['title'][:30]
            if key and key not in seen:
                seen.add(key)
                out.append(r)
        return out
    
    unique_dy = dedup(all_douyin)
    unique_bi = dedup(all_bilibili)
    
    print(f'\n抖音去重后: {len(unique_dy)} 条')
    print(f'B站去重后: {len(unique_bi)} 条')
    
    # 追加写入文件
    dy_file = os.path.join(data_dir, 'douyin.md')
    bi_file = os.path.join(data_dir, 'bilibili.md')
    
    with open(dy_file, 'a', encoding='utf-8') as f:
        f.write(f'\n\n## 抖音 AI技术热门内容 (百度搜索补充)\n')
        f.write(f'抓取时间: {ts}\n')
        f.write(f'数据来源: 百度 site:douyin.com 搜索\n\n')
        for i, r in enumerate(unique_dy[:100], 1):
            f.write(f'### 第{i}条\n')
            f.write(f'- 标题: {r["title"]}\n')
            f.write(f'- 链接: {r["url"]}\n')
            f.write(f'- 摘要: {r["snippet"]}\n')
            f.write(f'- 内容总结: 抖音平台AI相关热门教程与资讯\n\n')
    
    with open(bi_file, 'a', encoding='utf-8') as f:
        f.write(f'\n\n## B站 AI技术热门内容 (百度搜索补充)\n')
        f.write(f'抓取时间: {ts}\n')
        f.write(f'数据来源: 百度 site:bilibili.com 搜索\n\n')
        for i, r in enumerate(unique_bi[:100], 1):
            f.write(f'### 第{i}条\n')
            f.write(f'- 标题: {r["title"]}\n')
            f.write(f'- 链接: {r["url"]}\n')
            f.write(f'- 摘要: {r["snippet"]}\n')
            f.write(f'- 内容总结: B站AI技术热门教程与资讯\n\n')
    
    print(f'\n[DONE]')
    print(f'抖音: {len(unique_dy)} 条 -> {dy_file}')
    print(f'B站: {len(unique_bi)} 条 -> {bi_file}')

if __name__ == '__main__':
    main()
