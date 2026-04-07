# B站数据提取脚本
# 从agent-browser的snapshot输出中提取视频信息
import re
import sys
from datetime import datetime

def parse_snapshot_to_items(snapshot_text):
    """从snapshot文本解析B站视频数据"""
    items = []
    
    # 匹配视频条目的模式 - 匹配每个视频块
    # 模式: heading "标题" + 后续信息
    lines = snapshot_text.split('\n')
    
    current_item = None
    for i, line in enumerate(lines):
        # 匹配视频标题行
        heading_match = re.search(r'heading "(.+?)" \[ref=e(\d+)\]', line)
        if heading_match:
            title = heading_match.group(1)
            ref = heading_match.group(2)
            
            # 跳过导航和固定元素
            if any(skip in title for skip in ['首页', '番剧', '直播', '游戏中心', '会员购', '漫画', '赛事', '综合', '视频', '番剧', '影视', '专栏', '用户', 'bilibili']):
                continue
            
            # UP主信息通常在后面的行中
            up_info = ""
            for j in range(i+1, min(i+10, len(lines))):
                up_match = re.search(r'link "(.+?) · (.+?)" \[ref=e\d+\]', lines[j])
                if up_match:
                    up_info = up_match.group(1)
                    date_info = up_match.group(2)
                    break
            
            # 查找播放量、弹幕、点赞
            views = likes = danmaku = "未获取"
            duration = ""
            
            # 在前后行中搜索统计数据
            for j in range(max(0, i-5), min(len(lines), i+5)):
                stat_match = re.search(r'StaticText "(.+?)"', lines[j])
                if stat_match:
                    val = stat_match.group(1)
                    if re.match(r'^[\d.]+万?$', val) or re.match(r'^\d+$', val):
                        if views == "未获取":
                            views = val
                        elif likes == "未获取":
                            likes = val
                        elif danmaku == "未获取":
                            danmaku = val
                
                # 时长
                dur_match = re.search(r'StaticText "(\d{2}:\d{2}(?::\d{2})?)"', lines[j])
                if dur_match:
                    duration = dur_match.group(1)
            
            # 如果标题中有时长信息
            duration_match = re.search(r'(\d{2}:\d{2}(?::\d{2})?)', title)
            if duration_match and not duration:
                duration = duration_match.group(1)
            
            # 从标题中提取播放量（如果有的话）
            stats_in_title = re.search(r'([\d.]+万?) ([\d.]+万?) (\d{2}:\d{2}(?::\d{2})?)', title)
            if stats_in_title:
                # 这是卡片视图格式: 播放 弹幕 时长
                pass  # 已经在前面获取
            
            items.append({
                'title': title,
                'up': up_info,
                'views': views,
                'likes': likes,
                'danmaku': danmaku,
                'duration': duration,
                'date': date_info if 'date_info' in dir() else ''
            })
    
    # 去重
    seen = set()
    unique_items = []
    for item in items:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_items.append(item)
    
    return unique_items

def format_bilibili_markdown(items, start_num=1):
    """格式化为markdown"""
    md = f"# B站 AI人工智能 热门内容\n"
    md += f"抓取时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    md += f"数据来源：B站搜索 AI人工智能（综合排序）\n\n"
    md += "---\n\n"
    
    for i, item in enumerate(items, start=start_num):
        md += f"### 第{i}条\n"
        md += f"- 标题: {item['title']}\n"
        md += f"- UP主: {item['up'] or '(未获取)'}\n"
        md += f"- 播放: {item['views']}\n"
        md += f"- 弹幕: {item['danmaku']}\n"
        md += f"- 点赞: {item['likes']}\n"
        md += f"- 时长: {item['duration'] or '(未获取)'}\n"
        md += f"- 内容简介: (待补充)\n\n"
    
    return md

if __name__ == "__main__":
    # 读取snapshot
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
    
    items = parse_snapshot_to_items(content)
    print(f"提取到 {len(items)} 条数据")
    
    md = format_bilibili_markdown(items)
    print(md)
