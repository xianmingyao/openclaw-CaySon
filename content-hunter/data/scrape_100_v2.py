"""
抖音 + B站 AI内容抓取 - 追加100条
使用正确的API + mobile UA
"""
import requests
import re
import os
import time
import json
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
DATA_DIR_UNIX = "E:/workspace/content-hunter/data"

MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def count_items(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r'### 第\d+条', content))

def save_append(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

def format_count(v):
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
    """清理B站标题中的HTML标签"""
    return re.sub(r'<[^>]+>', '', title)

def get_duration_str(duration):
    """格式化时长（秒-> MM:SS）"""
    try:
        seconds = int(duration)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
    except:
        return duration

# ═══════════════════════════════════════════════════════════════
#  抖音抓取
# ═══════════════════════════════════════════════════════════════
def scrape_douyin_keyword(keyword, start_offset=0, count=20):
    """抖音搜索API"""
    url = "https://www.douyin.com/aweme/v1/web/general/search/single/"
    params = {
        "keyword": keyword,
        "search_channel": "aweme_user_web",
        "search_source": "tab_search",
        "query_correct_type": "1",
        "is_filter_search": "0",
        "offset": start_offset,
        "count": count,
        "pc_client_type": "1",
        "version_code": "290100",
        "version_name": "29.1.0",
        "cookie_enabled": "true",
        "screen_width": "1920",
        "screen_height": "1080",
        "browser_language": "zh-CN",
        "browser_platform": "Win32",
        "browser_name": "Chrome",
        "browser_version": "120.0.0.0",
    }
    headers = {
        "User-Agent": PC_UA,
        "Referer": "https://www.douyin.com/",
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        return resp.json()
    except:
        return {}

def collect_douyin_100(existing_count):
    """抓取抖音100条"""
    print(f"[抖音] 从第{existing_count+1}条开始抓取...")
    
    keywords = ["AI", "人工智能", "ChatGPT", "大模型", "AI工具", "AI教程", "AI写作", "AI绘画", "AI视频", "AI应用"]
    
    all_items = []
    seen_titles = set()
    
    for kw in keywords:
        if len(all_items) >= 100:
            break
        print(f"  关键词: {kw}")
        
        for offset in range(0, 60, 20):
            if len(all_items) >= 100:
                break
            
            data = scrape_douyin_keyword(kw, start_offset=offset)
            aweme_list = data.get("aweme_list", [])
            
            if not aweme_list:
                continue
                
            for aweme in aweme_list:
                if len(all_items) >= 100:
                    break
                    
                try:
                    desc = aweme.get("desc", "")
                    author = aweme.get("author", {})
                    statistics = aweme.get("statistics", {})
                    challenges = aweme.get("challenges", [])
                    
                    author_name = author.get("nickname", "未知")
                    likes = statistics.get("digg_count", 0)
                    likes_str = format_count(likes)
                    
                    # 提取标签
                    tag_list = [f"#{ch.get('cha_name', '')}" for ch in challenges]
                    tags = " ".join(tag_list[:5])
                    
                    # 内容总结
                    summary = desc[:120] if desc else "暂无描述"
                    if not desc:
                        continue
                    if desc in seen_titles:
                        continue
                    seen_titles.add(desc)
                    
                    idx = existing_count + len(all_items) + 1
                    item = f"""
### 第{idx}条
- 标题: {desc}
- 作者: @{author_name}
- 点赞: {likes_str}
- 话题: {tags}
- 内容总结: {summary}
"""
                    all_items.append(item)
                except Exception as e:
                    continue
            
            time.sleep(0.3)
    
    # 追加保存
    filepath = os.path.join(DATA_DIR, "douyin.md")
    content = "\n".join(all_items)
    save_append(filepath, content)
    print(f"[抖音] 追加 {len(all_items)} 条完成 (总: {existing_count + len(all_items)})")

# ═══════════════════════════════════════════════════════════════
#  B站抓取
# ═══════════════════════════════════════════════════════════════
def scrape_bilibili_keyword(keyword, page=1):
    """B站视频搜索 API"""
    encoded_kw = requests.utils.quote(keyword)
    url = f"https://api.bilibili.com/x/web-interface/search/type?keyword={encoded_kw}&search_type=video&page={page}&order=totalrank&jsonp=jsonp"
    headers = {
        "User-Agent": MOBILE_UA,
        "Referer": "https://www.bilibili.com/",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        return resp.json()
    except:
        return {}

def collect_bilibili_100(existing_count):
    """抓取B站100条"""
    print(f"[B站] 从第{existing_count+1}条开始抓取...")
    
    keywords = ["AI", "人工智能", "ChatGPT", "大模型", "AI工具", "AI教程", "AI写作", "AI绘画", "AI视频", "AI应用"]
    
    all_items = []
    seen_titles = set()
    
    for kw in keywords:
        if len(all_items) >= 100:
            break
        print(f"  关键词: {kw}")
        
        for page in range(1, 8):
            if len(all_items) >= 100:
                break
            
            data = scrape_bilibili_keyword(kw, page=page)
            videos = data.get("data", {}).get("result", [])
            
            if not videos:
                break
            
            for v in videos:
                if len(all_items) >= 100:
                    break
                    
                try:
                    title = clean_title(v.get("title", ""))
                    author = v.get("author", "未知")
                    bvid = v.get("bvid", "")
                    link = f"https://www.bilibili.com/video/{bvid}"
                    
                    play = v.get("play", "0")
                    danmaku = v.get("video_review", "0")
                    like = v.get("like", "0")
                    coins = v.get("coins", "0")
                    favorites = v.get("favorites", "0")
                    duration = v.get("duration", "00:00")
                    description = v.get("description", "")
                    
                    play_str = format_count(play)
                    like_str = format_count(like)
                    coins_str = format_count(coins)
                    favorites_str = format_count(favorites)
                    danmaku_str = format_count(danmaku)
                    
                    summary = description[:120] if description else title[:120]
                    if not title:
                        continue
                    if title in seen_titles:
                        continue
                    seen_titles.add(title)
                    
                    idx = existing_count + len(all_items) + 1
                    item = f"""
### 第{idx}条
- 标题: {title}
- UP主: @{author}
- 播放: {play_str}
- 弹幕: {danmaku_str}
- 点赞: {like_str}
- 投币: {coins_str}
- 收藏: {favorites_str}
- 字幕: 无
- 时长: {duration}
- 话题: 
- 链接: {link}
- 内容总结: {summary}
"""
                    all_items.append(item)
                except Exception as e:
                    continue
            
            time.sleep(0.3)
    
    # 追加保存
    filepath = os.path.join(DATA_DIR, "bilibili.md")
    content = "\n".join(all_items)
    save_append(filepath, content)
    print(f"[B站] 追加 {len(all_items)} 条完成 (总: {existing_count + len(all_items)})")

# ═══════════════════════════════════════════════════════════════
#  主流程
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    douyin_path = os.path.join(DATA_DIR, "douyin.md")
    bilibili_path = os.path.join(DATA_DIR, "bilibili.md")
    
    douyin_count = count_items(douyin_path)
    bilibili_count = count_items(bilibili_path)
    
    print(f"当前状态: 抖音 {douyin_count} 条, B站 {bilibili_count} 条")
    print(f"目标: 各追加100条")
    print("=" * 50)
    
    # 抖音
    collect_douyin_100(douyin_count)
    
    # B站
    collect_bilibili_100(bilibili_count)
    
    # 验证
    new_douyin = count_items(douyin_path)
    new_bilibili = count_items(bilibili_path)
    print("=" * 50)
    print(f"完成: 抖音 {new_douyin} 条 (+{new_douyin-douyin_count})")
    print(f"完成: B站 {new_bilibili} 条 (+{new_bilibili-bilibili_count})")
