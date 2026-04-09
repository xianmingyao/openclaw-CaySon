"""
抖音 + B站 AI内容抓取 - 追加模式
每次运行追加100条到现有文件
"""
import json
import re
import os
import requests
import time
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"

# ─── 通用函数 ────────────────────────────────────────────────
def save_append(filepath, content):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

def extract_tags(text):
    """从文本中提取 #话题 标签"""
    tags = re.findall(r'#(\S+)', text)
    return " ".join(f"#{t}" for t in tags[:5])

# ─── 抖音抓取 ─────────────────────────────────────────────────
def scrape_douyin_search(keyword, start_offset=0, count=20):
    """调用抖音搜索API获取AI相关内容"""
    url = "https://www.douyin.com/aweme/v1/web/general/search/single/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
        "Cookie": ""
    }
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
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"抖音API请求失败: {e}")
        return {}

def parse_douyin_items(data, start_num):
    """解析抖音API返回的数据"""
    items = []
    aweme_list = data.get("aweme_list", [])
    for i, aweme in enumerate(aweme_list):
        try:
            desc = aweme.get("desc", "")
            author = aweme.get("author", {})
            statistics = aweme.get("statistics", {})
            challenges = aweme.get("challenges", [])
            
            author_name = author.get("nickname", "未知")
            likes = statistics.get("digg_count", 0)
            if likes >= 10000:
                likes_str = f"{likes/10000:.1f}万"
            else:
                likes_str = str(likes)
            
            # 提取标签
            tag_list = []
            for ch in challenges:
                tag_list.append(f"#{ch.get('cha_name', '')}")
            tags = " ".join(tag_list[:5]) if tag_list else ""
            
            # 内容总结
            summary = desc[:100] if desc else "暂无描述"
            
            item = f"""
### 第{start_num + i}条
- 标题: {desc if desc else '未知'}
- 作者: @{author_name}
- 点赞: {likes_str}
- 话题: {tags}
- 内容总结: {summary}
"""
            items.append(item)
        except Exception as e:
            print(f"解析视频项失败: {e}")
            continue
    return items

def collect_douyin_100(existing_count):
    """抓取抖音100条AI内容"""
    print(f"开始抓取抖音，从第{existing_count+1}条开始...")
    
    all_items = []
    keywords = ["AI", "人工智能", "ChatGPT", "大模型", "AI工具", "AI教程"]
    
    for kw in keywords:
        if len(all_items) >= 100:
            break
        print(f"  搜索关键词: {kw}")
        for offset in range(0, 60, 20):
            if len(all_items) >= 100:
                break
            data = scrape_douyin_search(kw, start_offset=offset)
            items = parse_douyin_items(data, existing_count + len(all_items) + 1)
            if not items:
                break
            all_items.extend(items)
            time.sleep(0.5)
    
    # 保存
    content = "\n".join(all_items[:100])
    save_append(os.path.join(DATA_DIR, "douyin.md"), content)
    print(f"抖音追加 {min(len(all_items), 100)} 条完成")

# ─── B站抓取 ─────────────────────────────────────────────────
def scrape_bilibili_search(keyword, page=1, page_size=20):
    """调用B站搜索API"""
    url = "https://api.bilibili.com/x/web-interface/search/type"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://search.bilibili.com/"
    }
    params = {
        "search_key": keyword,
        "page": page,
        "page_size": page_size,
        "order": "totalrank",
        "platform": "web",
        "channel": "video"
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"B站API请求失败: {e}")
        return {}

def parse_bilibili_items(data, start_num):
    """解析B站API返回的数据"""
    items = []
    result = data.get("data", {}).get("result", [])
    for i, video in enumerate(result):
        try:
            title = video.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", "")
            author = video.get("author", "未知")
            play = video.get("play", "0")
            video_review = video.get("video_review", "0")  # 弹幕
            favorites = video.get("favorites", "0")
            coins = video.get("coins", "0")
            like = video.get("like", "0")
            description = video.get("description", "")
            duration = video.get("duration", "00:00")
            bvid = video.get("bvid", "")
            link = f"https://www.bilibili.com/video/{bvid}"
            
            # 提取标签
            tag_match = video.get("tag", "")
            tags = " ".join([f"#{t}" for t in tag_match.split(",")[:5]]) if tag_match else ""
            
            summary = description[:100] if description else title[:100]
            
            item = f"""
### 第{start_num + i}条
- 标题: {title}
- UP主: @{author}
- 播放: {play}
- 弹幕: {video_review}
- 点赞: {like}
- 投币: {coins}
- 收藏: {favorites}
- 字幕: 无
- 时长: {duration}
- 话题: {tags}
- 链接: {link}
- 内容总结: {summary}
"""
            items.append(item)
        except Exception as e:
            print(f"解析B站视频项失败: {e}")
            continue
    return items

def collect_bilibili_100(existing_count):
    """抓取B站100条AI内容"""
    print(f"开始抓取B站，从第{existing_count+1}条开始...")
    
    all_items = []
    keywords = ["AI", "人工智能", "ChatGPT", "大模型", "AI教程", "AI工具"]
    
    for kw in keywords:
        if len(all_items) >= 100:
            break
        print(f"  搜索关键词: {kw}")
        for page in range(1, 6):
            if len(all_items) >= 100:
                break
            data = scrape_bilibili_search(kw, page=page)
            items = parse_bilibili_items(data, existing_count + len(all_items) + 1)
            if not items:
                break
            all_items.extend(items)
            time.sleep(0.5)
    
    # 保存
    content = "\n".join(all_items[:100])
    save_append(os.path.join(DATA_DIR, "bilibili.md"), content)
    print(f"B站追加 {min(len(all_items), 100)} 条完成")

# ─── 主流程 ─────────────────────────────────────────────────
if __name__ == "__main__":
    # 读取现有条数
    douyin_path = os.path.join(DATA_DIR, "douyin.md")
    bilibili_path = os.path.join(DATA_DIR, "bilibili.md")
    
    # 计算现有数量
    def count_items(filepath):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return len(re.findall(r'### 第\d+条', content))
        return 0
    
    douyin_count = count_items(douyin_path)
    bilibili_count = count_items(bilibili_path)
    
    print(f"当前: 抖音{douyin_count}条, B站{bilibili_count}条")
    
    # 追加抖音
    collect_douyin_100(douyin_count)
    
    # 追加B站
    collect_bilibili_100(bilibili_count)
    
    # 验证
    new_douyin = count_items(douyin_path)
    new_bilibili = count_items(bilibili_path)
    print(f"\n完成: 抖音{new_douyin}条 (+{new_douyin-douyin_count}), B站{new_bilibili}条 (+{new_bilibili-bilibili_count})")
