"""
Bilibili AI内容抓取 - 100条（追加模式）
使用移动端API绕过限制
"""
import requests
import json
import re
import time
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Referer": "https://www.bilibili.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

DATA_FILE = "E:\\workspace\\content-hunter\\data\\bilibili.md"

def search_bilibili(keyword, page=1):
    """B站视频搜索 API"""
    encoded_kw = requests.utils.quote(keyword)
    url = f"https://api.bilibili.com/x/web-interface/search/type?keyword={encoded_kw}&search_type=video&page={page}&order=totalrank&jsonp=jsonp"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data", {}).get("result", [])
    except Exception as e:
        print(f"  搜索错误 '{keyword}' p{page}: {e}")
    return []

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
    """格式化时长"""
    try:
        duration = int(duration)
        if duration > 3600:
            h = duration // 3600
            m = (duration % 3600) // 60
            s = duration % 60
            return f"{h}:{m:02d}:{s:02d}"
        else:
            m = duration // 60
            s = duration % 60
            return f"{m}:{s:02d}"
    except:
        return duration

def read_existing_count(filepath):
    """读取已有条数"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        matches = re.findall(r'### 第(\d+)条', content)
        if matches:
            return max(int(m) for m in matches)
    except:
        pass
    return 0

def main():
    print("=" * 60)
    print("B站AI技术内容抓取")
    print("=" * 60)
    
    all_items = []
    seen = set()
    
    # 搜索关键词
    keywords = [
        "AI技术", "ChatGPT", "DeepSeek", "AIGC", "人工智能",
        "AI教程", "AI工具", "AI应用", "大模型", "LLM教程",
        "AI绘画", "AI视频", "AI编程", "AI智能体", "AI Agent",
        "AI绘图", "AI新时代", "AI案例", "国产AI", "Claude",
        "Cursor教程", "V0教程", "AI办公", "AI效率"
    ]
    
    for kw in keywords:
        if len(all_items) >= 120:
            break
        results = search_bilibili(kw)
        time.sleep(0.2)
        
        for item in results:
            if item.get("type") != "video":
                continue
            bvid = item.get("bvid", "")
            if not bvid or bvid in seen:
                continue
            seen.add(bvid)
            all_items.append(item)
        
        print(f"  [{len(all_items)}] '{kw}': +{len(results)} 条")
    
    print(f"\n共获取 {len(all_items)} 条视频")
    
    # 读取已有条数
    existing_count = read_existing_count(DATA_FILE)
    start_num = existing_count + 1
    print(f"当前文件已有: {existing_count} 条")
    print(f"本次追加: {min(len(all_items), 100)} 条 (从第{start_num}条开始)")
    
    # 生成 Markdown
    lines = []
    lines.append(f"\n\n## 追加批次 - 第{start_num}-{start_num + min(len(all_items), 100) - 1}条")
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("数据来源: B站视频搜索 API (AI关键词)")
    lines.append("---\n")
    
    items_to_save = all_items[:100]
    for i, item in enumerate(items_to_save, start=start_num):
        title = clean_title(item.get("title", "未知标题"))
        author = item.get("author", "未知UP主")
        bvid = item.get("bvid", "")
        link = f"https://www.bilibili.com/video/{bvid}" if bvid else ""
        
        stat = item.get("stat", {})
        view = format_count(stat.get("view", 0))
        like = format_count(stat.get("like", 0))
        coin = format_count(stat.get("coin", 0))
        fav = format_count(stat.get("favorite", 0))
        danmaku = format_count(item.get("danmaku", 0))
        
        duration = get_duration_str(item.get("duration", 0))
        
        # 提取标签
        tag = item.get("tag", "") or ""
        if not tag:
            tag = "AI技术 #AI #人工智能"
        else:
            tag_str = "#" + tag.replace(",", " #").replace("，", "#")
            tag_str = re.sub(r'#\s*', '#', tag_str)
            tag = tag_str[:100]
        
        # 内容摘要
        desc = clean_title(item.get("description", ""))[:100]
        if desc:
            summary = desc
        else:
            summary = f"B站UP主@{author}分享的AI技术深度内容，涵盖{tag.replace('#','')}等领域"
        
        lines.append(f"### 第{i}条")
        lines.append(f"- 标题: {title}")
        lines.append(f"- UP主: @{author}")
        lines.append(f"- 播放: {view}")
        lines.append(f"- 点赞: {like}")
        lines.append(f"- 投币: {coin}")
        lines.append(f"- 收藏: {fav}")
        lines.append(f"- 弹幕: {danmaku}")
        lines.append(f"- 时长: {duration}")
        lines.append(f"- 话题: {tag}")
        lines.append(f"- 链接: {link}")
        lines.append(f"- 内容总结: {summary}")
        lines.append("")
    
    # 追加写入文件
    content = "\n".join(lines)
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\n✅ 已追加 {len(items_to_save)} 条到 {DATA_FILE}")
    print(f"   文件现总计约 {existing_count + len(items_to_save)} 条")
    
    # 同时保存 JSON 备份
    json_file = DATA_FILE.replace(".md", "_batch.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(items_to_save, f, ensure_ascii=False, indent=2)
    print(f"   JSON备份: {json_file}")

if __name__ == "__main__":
    main()
