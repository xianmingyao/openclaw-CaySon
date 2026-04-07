#!/usr/bin/env python3
"""
内容捕手 - 抖音+B站 AI技术热门内容抓取
每平台100条，追加到现有md文件
"""
import json
import re
import time
import requests
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter-data\data"
BILIBILI_FILE = f"{DATA_DIR}\\bilibili.md"
DOUYIN_FILE = f"{DATA_DIR}\\douyin.md"

HEADERS_BILIBILI = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
}

HEADERS_DOUYIN = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Referer": "https://www.douyin.com/",
    "Accept": "application/json, text/plain, */*",
}

# ========== B站抓取 ==========
def get_bilibili_items():
    """从B站科技分区排行榜API获取"""
    items = []
    
    # 科技数码分区 rid=36
    url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=36"
    resp = requests.get(url, headers=HEADERS_BILIBILI, timeout=15)
    data = resp.json()
    
    if data["code"] != 0:
        print(f"B站API错误: {data['message']}")
        return []
    
    items = data["data"]["list"]
    print(f"B站获取到 {len(items)} 条")
    return items

def get_bilibili_ai_search():
    """B站搜索AI相关内容"""
    items = []
    keywords = ["AI", "人工智能", "ChatGPT", "大模型", "LLM", "AI绘画", "AI生成"]
    
    for kw in keywords[:3]:  # 限制搜索次数
        url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={kw}&order=totalrank&duration=0&page=1&ps=20"
        try:
            resp = requests.get(url, headers=HEADERS_BILIBILI, timeout=10)
            d = resp.json()
            if d.get("code") == 0:
                result = d.get("data", {}).get("result", [])
                for v in result:
                    if isinstance(v, dict) and v.get("bvid"):
                        v["_search_kw"] = kw
                        items.append(v)
                print(f"B站搜索'{kw}': {len(result)} 条")
        except Exception as e:
            print(f"B站搜索'{kw}'失败: {e}")
        time.sleep(0.5)
    
    return items

def format_bilibili_item(item, number, is_search=False):
    """格式化B站条目"""
    if is_search:
        title = item.get("title", "").replace("<em class=\"keyword\">","").replace("</em>","")
        author = item.get("author", "未知")
        bvid = item.get("bvid", "")
        link = f"https://www.bilibili.com/video/{bvid}"
        desc = item.get("description", "")
        view = item.get("play", 0)
        like = item.get("like", 0)
        duration = item.get("duration", 0)
        tags = []
        danmaku = 0
        coin = 0
        fav = 0
    else:
        title = item.get("title", "").strip()
        author = item.get("owner", {}).get("name", "未知")
        bvid = item.get("bvid", "")
        link = f"https://www.bilibili.com/video/{bvid}"
        desc = item.get("desc", "")
        stat = item.get("stat", {})
        view = stat.get("view", 0)
        like = stat.get("like", 0)
        danmaku = stat.get("danmaku", 0)
        coin = stat.get("coin", 0)
        fav = stat.get("favorite", 0)
        duration = item.get("duration", 0)
        tags = [t["tag_name"] for t in item.get("tags", [])[:5]]
    
    return f"""## 第{number}条
- 标题 / Title: {title}
- UP主 / UP: {author}
- 播放 / Views: {view}
- 弹幕 / Danmaku: {danmaku}
- 点赞 / Likes: {like}
- 投币 / Coins: {coin}
- 收藏 / Favs: {fav}
- 时长 / Duration: {duration}秒
- 话题 / Tags: {' / '.join(tags)}
- 内容总结 / Summary: {desc[:200] if desc else 'B站热门视频'}
- 链接 / URL: {link}"""

# ========== 抖音抓取 ==========
def get_douyin_items():
    """获取抖音AI相关热门内容 - 搜索API"""
    all_items = []
    
    # 关键词搜索
    keywords = ["AI人工智能", "人工智能技术", "大模型", "AI工具", "AI应用"]
    
    for kw in keywords:
        url = f"https://www.douyin.com/aweme/v1/web/search/item/?keyword={kw}&count=20&offset=0"
        try:
            resp = requests.get(url, headers=HEADERS_DOUYIN, timeout=10, allow_redirects=False)
            print(f"抖音搜索'{kw}': HTTP {resp.status_code}")
            if resp.status_code == 200:
                try:
                    d = resp.json()
                    if d.get("status_code") == 0:
                        items = d.get("item_list", [])
                        all_items.extend(items)
                        print(f"  -> 获取 {len(items)} 条")
                except Exception as e:
                    print(f"  -> 解析失败: {e}")
        except Exception as e:
            print(f"抖音搜索'{kw}'失败: {e}")
        time.sleep(1)
    
    return all_items

def get_douyin_by_web():
    """通过网页HTML解析抖音热门"""
    items = []
    url = "https://www.douyin.com/discover?modal_id=735432"
    try:
        resp = requests.get(url, headers=HEADERS_DOUYIN, timeout=10)
        print(f"抖音网页: HTTP {resp.status_code}, 长度 {len(resp.text)}")
        # 从HTML中提取视频数据
        patterns = [
            r'"aweme_id":"(\d+)".*?"desc":"([^"]+)".*?"nickname":"([^"]+)"',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, resp.text)
            print(f"  模式匹配: {len(matches)} 条")
    except Exception as e:
        print(f"抖音网页解析失败: {e}")
    return items

def format_douyin_item(item, number):
    """格式化抖音条目"""
    desc = item.get("desc", "").strip()
    author = item.get("author", {})
    if isinstance(author, dict):
        author_name = author.get("nickname", "未知")
    else:
        author_name = str(author)
    
    aweme_id = item.get("aweme_id", "")
    link = f"https://www.douyin.com/video/{aweme_id}"
    
    stat = item.get("statistics", {})
    digg = stat.get("digg_count", 0)
    comment = stat.get("comment_count", 0)
    share = stat.get("share_count", 0)
    
    challenges = item.get("challenges", []) or []
    tags = [c.get("challenge_name", "") for c in challenges[:5] if isinstance(c, dict) and c.get("challenge_name")]
    
    return f"""## 第{number}条
- 标题 / Title: {desc if desc else f'抖音视频{aweme_id}'}
- 作者 / Author: @{author_name}
- 点赞 / Likes: {digg}
- 评论 / Comments: {comment}
- 分享 / Shares: {share}
- 话题 / Tags: {' '.join(['#'+t for t in tags if t])}
- 内容总结 / Summary: {desc[:200] if desc else '抖音热门视频'}
- 链接 / URL: {link}"""

# ========== 辅助函数 ==========
def get_existing_count(filepath):
    """读取文件中现有的最大编号"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        matches = re.findall(r"^## 第(\d+)条", content, re.MULTILINE)
        if matches:
            return max(int(m) for m in matches)
    except:
        pass
    return 0

def append_items(filepath, items, formatter_func, platform_name):
    """追加条目到文件"""
    existing = get_existing_count(filepath)
    print(f"现有 {platform_name} 数据: {existing} 条")
    
    # 去重：新条目只添加aweme_id/bvid不在现有文件中的
    existing_ids = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        if platform_name == "B站":
            existing_ids = set(re.findall(r'BV\w+', content))
        else:
            existing_ids = set(re.findall(r'https://www\.douyin\.com/video/(\d+)', content))
    except:
        pass
    
    added = 0
    with open(filepath, "a", encoding="utf-8") as f:
        for item in items:
            item_id = ""
            if platform_name == "B站":
                item_id = item.get("bvid", "")
            else:
                item_id = item.get("aweme_id", "")
            
            if item_id and item_id in existing_ids:
                continue
            
            number = existing + added + 1
            formatted = formatter_func(item, number)
            f.write("\n" + formatted + "\n")
            added += 1
            if added >= 100:
                break
    
    print(f"{platform_name}新增 {added} 条 (编号 {existing+1} ~ {existing+added})")
    return added

# ========== 主程序 ==========
def main():
    print(f"=== 内容捕手抓取 {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    
    # B站科技分区
    print("\n--- B站科技分区 ---")
    b_items = get_bilibili_items()
    if b_items:
        append_items(BILIBILI_FILE, b_items, format_bilibili_item, "B站")
    else:
        print("B站抓取失败")
    
    # B站AI搜索补充
    print("\n--- B站AI搜索补充 ---")
    b_search = get_bilibili_ai_search()
    if b_search:
        append_items(BILIBILI_FILE, b_search, lambda item, n: format_bilibili_item(item, n, True), "B站搜索")
    
    # 抖音
    print("\n--- 抖音 ---")
    d_items = get_douyin_items()
    if d_items:
        append_items(DOUYIN_FILE, d_items, format_douyin_item, "抖音")
    else:
        print("抖音搜索失败，尝试网页解析...")
        d_items = get_douyin_by_web()
        if d_items:
            append_items(DOUYIN_FILE, d_items, format_douyin_item, "抖音网页")
    
    # 最终统计
    print("\n--- 最终统计 ---")
    b_count = get_existing_count(BILIBILI_FILE)
    d_count = get_existing_count(DOUYIN_FILE)
    print(f"B站总计: {b_count} 条")
    print(f"抖音总计: {d_count} 条")
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
