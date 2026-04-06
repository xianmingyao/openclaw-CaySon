# -*- coding: utf-8 -*-
"""B站 AI人工智能 热门视频爬虫
通过B站官方API抓取搜索结果
"""
import requests, re, json, time, codecs, sys

# 确保控制台输出UTF-8
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
})

API_URL = 'https://api.bilibili.com/x/web-interface/search/type'
SEARCH_PARAMS = {
    'search_type': 'video',
    'keyword': 'AI人工智能',
    'order': 'totalrank',  # 综合排序
    'duration': 0,  # 全部时长
    'page_size': 30
}

def clean_html(text):
    """清理HTML标签和解码特殊字符"""
    if not text:
        return ''
    # 解码 \u003c \u003e 等
    text = re.sub(r'\\u003c([^>]+)\\u003e', r'<\1>', text)
    # 移除HTML标签
    text = re.sub('<[^>]+>', '', text)
    return text.strip()

def fetch_page(page_num):
    """抓取单页数据"""
    params = dict(SEARCH_PARAMS, page=page_num)
    for attempt in range(3):
        try:
            r = SESSION.get(API_URL, params=params, timeout=15)
            data = r.json()
            if data.get('code') == 0:
                return data['data']
            elif 'request was banned' in str(data.get('message', '')):
                print(f'  Page {page_num}: 请求被禁止，等待10秒...')
                time.sleep(10)
                continue
            else:
                print(f'  Page {page_num}: API错误 - {data.get("message")}')
                return None
        except Exception as e:
            print(f'  Page {page_num}: 网络错误 - {e}, 重试中...')
            time.sleep(3)
    return None

def parse_video(v, entry_num):
    """解析单个视频条目"""
    title = clean_html(v.get('title', ''))
    author = v.get('author', '')
    play = v.get('play', '0')
    danmaku = v.get('video_review', '0')
    like = v.get('like', '0')
    coin = v.get('coin', '0')
    fav = v.get('fav', '0')
    duration = v.get('duration', '')
    description = clean_html(v.get('description', ''))
    arcurl = v.get('arcurl', '')
    bvid = v.get('bvid', '')
    
    # 生成内容总结
    summary = generate_summary(title, description, author, play)
    
    # 检查字幕（有description说明有字幕）
    has_subtitle = '有' if description else '无'
    
    return f"""### 第{entry_num}条
- 标题: {title}
- UP主: {author}
- 播放: {play}
- 弹幕: {danmaku}
- 点赞: {like}
- 投币: {coin}
- 收藏: {fav}
- 字幕: {has_subtitle}
- 内容总结: {summary}
"""

def generate_summary(title, description, author, play):
    """生成内容总结"""
    parts = []
    if title:
        parts.append(f"视频标题为{title}")
    if description:
        # 取description前100字
        desc_short = description[:100] if len(description) > 100 else description
        parts.append(f"内容围绕{desc_short}")
    if author:
        parts.append(f"由UP主{author}创作")
    if play:
        parts.append(f"播放量达{play}次")
    
    summary = '，'.join(parts[:4])
    if len(summary) > 150:
        summary = summary[:147] + '...'
    return summary

def get_total_entries():
    """获取总条目数"""
    data = fetch_page(1)
    if data:
        return data.get('numResults', 0), data.get('numPages', 0)
    return 0, 0

def scrape_all(total_needed=100):
    """抓取指定数量的视频"""
    all_entries = []
    page = 1
    consecutive_errors = 0
    
    while len(all_entries) < total_needed:
        print(f'\n正在抓取第 {page} 页...')
        data = fetch_page(page)
        
        if data is None:
            consecutive_errors += 1
            if consecutive_errors >= 3:
                print('连续3页失败，停止抓取')
                break
            page += 1
            continue
        
        videos = data.get('result', [])
        if not videos:
            print(f'  第 {page} 页没有视频，停止')
            break
        
        consecutive_errors = 0
        num_pages = data.get('numPages', 1)
        print(f'  获取到 {len(videos)} 个视频，总共 {num_pages} 页')
        
        for v in videos:
            entry_num = 527 + len(all_entries)  # 从527开始（接续原有526条）
            entry = parse_video(v, entry_num)
            all_entries.append(entry)
            print(f'  [{len(all_entries)}] {clean_html(v.get("title", ""))[:40]}')
            
            if len(all_entries) >= total_needed:
                break
        
        if page >= num_pages:
            print(f'  已到达最后一页 ({num_pages})')
            break
        
        page += 1
        time.sleep(2)  # 礼貌性延迟
    
    return all_entries

if __name__ == '__main__':
    print('=' * 50)
    print('B站 AI人工智能 热门视频爬虫')
    print('=' * 50)
    
    # 获取总数
    print('\n正在获取搜索结果总数...')
    total, num_pages = get_total_entries()
    print(f'搜索结果总数: {total}, 总页数: {num_pages}')
    
    # 抓取100条
    entries = scrape_all(100)
    print(f'\n抓取完成! 共获取 {len(entries)} 条数据')
    
    # 输出前3条预览
    for e in entries[:3]:
        print('\n' + e[:200])
    
    # 保存到文件
    output_file = r'C:\Users\Administrator\.openclaw\workspace\content-hunter\data\bilibili.md'
    
    # 构建新内容
    new_header = """# B站 AI人工智能 热门内容
抓取时间：2026-04-06 18:38（追加）
数据来源：B站搜索AI人工智能（综合排序）
说明：数据来自B站热门内容追加抓取

---

"""
    new_content = new_header + '\n\n'.join(entries) + '\n'
    
    # 追加到文件
    with codecs.open(output_file, 'a', 'utf-8') as f:
        f.write('\n\n' + new_content)
    
    print(f'\n已追加到文件: {output_file}')
    print(f'新增条目数: {len(entries)}')
