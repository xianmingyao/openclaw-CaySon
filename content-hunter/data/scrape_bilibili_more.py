"""
B站追加抓取 - 补满100条
"""
import requests
import re
import os
import time

DATA_DIR = r"E:\workspace\content-hunter\data"
MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"

def count_items(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r'### 第\d+条', content))

def save_append(filepath, content):
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
    return re.sub(r'<[^>]+>', '', title)

def scrape_bilibili_keyword(keyword, page=1):
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

def main():
    bilibili_path = os.path.join(DATA_DIR, "bilibili.md")
    existing_count = count_items(bilibili_path)
    print(f"当前B站: {existing_count} 条")
    
    # 读取已有标题
    seen_titles = set()
    if os.path.exists(bilibili_path):
        with open(bilibili_path, "r", encoding="utf-8") as f:
            content = f.read()
        for t in re.findall(r'- 标题: (.+)', content):
            seen_titles.add(t.strip())
    
    keywords = ["AI大模型", "ChatGPT技巧", "AI工具推荐", "人工智能应用", "DeepSeek教程", "AI编程", "AI创作", "大模型解读", "AI Agent", "AI视频"]
    
    all_items = []
    
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
                    if not title or title in seen_titles:
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
- 话题: #{kw}
- 链接: {link}
- 内容总结: {summary}
"""
                    all_items.append(item)
                except:
                    continue
            
            time.sleep(0.3)
    
    if all_items:
        content = "\n".join(all_items)
        save_append(bilibili_path, content)
        print(f"B站追加 {len(all_items)} 条完成 (总: {existing_count + len(all_items)})")
    else:
        print("B站未能获取新内容")

if __name__ == "__main__":
    main()
