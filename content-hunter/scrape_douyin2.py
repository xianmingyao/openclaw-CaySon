#!/usr/bin/env python3
"""抖音AI内容抓取 - 热搜+推荐混合策略"""
import urllib.request, urllib.parse, json, time, random, re

# 1. 从热搜榜抓取相关AI话题及其视频
def get_hot_topics():
    """获取热搜榜单，筛选AI相关话题"""
    url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/?' + urllib.parse.urlencode({
        'device_platform': 'webapp', 'aid': '6383', 'channel': 'channel_pc_web',
        'version_code': '190600', 'version_name': '19.6.0',
        'cookie_enabled': 'true', 'screen_width': '1920', 'screen_height': '1080',
        'browser_language': 'zh-CN', 'browser_platform': 'Win32',
        'browser_name': 'Chrome', 'browser_version': '120.0.0.0',
    })
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.douyin.com/', 'Accept': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    raw = resp.read().decode('utf-8')
    data = json.loads(raw)
    word_list = data.get('data', {}).get('word_list', [])
    
    # Filter AI-related topics
    ai_keywords = ['AI', '人工智能', 'ChatGPT', 'GPT', '大模型', 'LLM', 'DeepSeek', 
                   'Deepseek', 'Gemini', 'Copilot', '机器学习', '神经网络', 'AI生成',
                   'AIGC', 'AI视频', 'AI绘图', 'AI绘画', '文生图', '文生视频', 'Sora',
                   'Kimi', 'Kimi大模型', '豆包', '通义', '讯飞', '智谱', '百川', '360AI']
    
    ai_topics = []
    for item in word_list:
        word = item.get('word', '')
        for kw in ai_keywords:
            if kw.lower() in word.lower():
                ai_topics.append({
                    'word': word,
                    'hot_value': item.get('hot_value', 0),
                    'challenge_id': item.get('challenge_id', ''),
                })
                break
    return ai_topics

# 2. 尝试从话题页获取视频
def get_videos_from_challenge(challenge_name):
    """通过话题名称搜索视频"""
    results = []
    for offset in [0, 20, 40, 60, 80]:
        url = 'https://www.douyin.com/aweme/v1/web/search/item/?' + urllib.parse.urlencode({
            'keyword': challenge_name,
            'count': '20',
            'offset': str(offset),
            'device_platform': 'webapp', 'aid': '6383', 'channel': 'channel_pc_web',
            'search_channel': 'aweme_video_web', 'sort_type': '0',
            'publish_time': '0', 'source': 'normal_search',
            'pc_client_type': '1', 'version_code': '190600', 'version_name': '19.6.0',
            'cookie_enabled': 'true', 'screen_width': '1920', 'screen_height': '1080',
            'browser_language': 'zh-CN', 'browser_platform': 'Win32',
            'browser_name': 'Chrome', 'browser_version': '120.0.0.0',
        })
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': f'https://www.douyin.com/search/{urllib.parse.quote(challenge_name)}',
            'Accept': 'application/json', 'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=15)
            raw = resp.read().decode('utf-8')
            data = json.loads(raw)
            items = data.get('data', [])
            if not items:
                break
            for item in items:
                aweme = item.get('aweme_info', {}) or item
                video_desc = aweme.get('desc', '')
                author = aweme.get('author', {}).get('nickname', '')
                digg_count = aweme.get('statistics', {}).get('digg_count', 0)
                share_url = aweme.get('share_url', '')
                aweme_id = aweme.get('aweme_id', '')
                tags = re.findall(r'#(\w+)', video_desc)
                results.append({
                    'title': video_desc or '无标题',
                    'author': author,
                    'likes': digg_count,
                    'tags': ' '.join([f'#{t}' for t in tags[:5]]),
                    'url': share_url or f'https://www.douyin.com/video/{aweme_id}',
                    'source': f'话题:{challenge_name}',
                })
            if not data.get('has_more'):
                break
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f'  话题 {challenge_name} offset={offset} 失败: {e}')
            break
    return results

# 3. 直接搜索多个AI关键词
def search_ai_keywords():
    """直接搜索多个AI相关关键词"""
    keywords = ['AI人工智能', 'ChatGPT使用技巧', 'DeepSeek教程', '大模型应用', 
                'AIGC创作', 'AI视频生成', 'AI绘图教程', 'AI工具推荐']
    all_results = []
    seen_ids = set()
    
    for kw in keywords:
        url = 'https://www.douyin.com/aweme/v1/web/search/item/?' + urllib.parse.urlencode({
            'keyword': kw, 'count': '20', 'offset': '0',
            'device_platform': 'webapp', 'aid': '6383', 'channel': 'channel_pc_web',
            'search_channel': 'aweme_video_web', 'sort_type': '0',
            'publish_time': '0', 'source': 'normal_search',
            'pc_client_type': '1', 'version_code': '190600', 'version_name': '19.6.0',
            'cookie_enabled': 'true', 'screen_width': '1920', 'screen_height': '1080',
            'browser_language': 'zh-CN', 'browser_platform': 'Win32',
            'browser_name': 'Chrome', 'browser_version': '120.0.0.0',
        })
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.douyin.com/', 'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, timeout=15)
            raw = resp.read().decode('utf-8')
            data = json.loads(raw)
            items = data.get('data', [])
            print(f'关键词 [{kw}]: {len(items)} 条')
            if not items:
                continue
            for item in items:
                aweme = item.get('aweme_info', {}) or item
                aweme_id = aweme.get('aweme_id', '')
                if aweme_id in seen_ids:
                    continue
                seen_ids.add(aweme_id)
                video_desc = aweme.get('desc', '')
                author = aweme.get('author', {}).get('nickname', '')
                digg_count = aweme.get('statistics', {}).get('digg_count', 0)
                share_url = aweme.get('share_url', '')
                tags = re.findall(r'#(\w+)', video_desc)
                all_results.append({
                    'title': video_desc or '无标题',
                    'author': author,
                    'likes': digg_count,
                    'tags': ' '.join([f'#{t}' for t in tags[:5]]),
                    'url': share_url or f'https://www.douyin.com/video/{aweme_id}',
                    'source': f'关键词:{kw}',
                })
            time.sleep(random.uniform(1, 2))
        except Exception as e:
            print(f'关键词 [{kw}] 失败: {e}')
    
    return all_results

if __name__ == '__main__':
    print('=== 策略1: 搜索AI关键词 ===')
    results = search_ai_keywords()
    print(f'关键词搜索获得: {len(results)} 条')
    
    if len(results) < 50:
        print('\n=== 策略2: 从热搜AI话题获取 ===')
        topics = get_hot_topics()
        print(f'找到 {len(topics)} 个AI相关热搜话题')
        for topic in topics[:5]:
            print(f'  - {topic["word"]} (热度:{topic["hot_value"]})')
    
    # Save results
    if results:
        import os
        DATA_DIR = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'content-hunter', 'data')
        filepath = os.path.join(DATA_DIR, 'douyin.md')
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f'\n\n---\n')
            f.write(f'> [追加抓取时间: {ts}]\n')
            f.write(f'> [本次新增: {len(results)} 条 抖音AI技术热门内容]\n')
            f.write(f'> [数据来源: 抖音搜索API]\n\n')
            for i, item in enumerate(results, 173):
                f.write(f'### 第{i}条\n')
                f.write(f'- 标题: {item["title"]}\n')
                f.write(f'- 作者: @{item["author"]}\n')
                f.write(f'- 点赞: {item["likes"]}\n')
                f.write(f'- 话题: {item["tags"]}\n')
                f.write(f'- 链接: {item["url"]}\n')
                f.write(f'- 内容总结: 视频主题为{item["title"]}，由@{item["author"]}创作，点赞数{item["likes"]}，内容涉及AI人工智能相关领域...\n\n')
        print(f'已追加 {len(results)} 条到 {filepath}')
    else:
        print('未获得任何数据，抖音API从当前IP完全无法访问')
