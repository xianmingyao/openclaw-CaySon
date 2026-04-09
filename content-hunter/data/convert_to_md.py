#!/usr/bin/env python3
"""从JSON转换为MD格式"""
import json
import os

DATA_DIR = r"E:\workspace\content-hunter\data"

# B站
input_file = os.path.join(DATA_DIR, 'bilibili_ai_100.json')
output_file = os.path.join(DATA_DIR, 'bilibili.md')

with open(input_file, 'r', encoding='utf-8') as f:
    items = json.load(f)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# B站AI技术热门内容\n\n")
    f.write(f"抓取时间: 2026-04-09\n")
    f.write(f"数据来源: bilibili_ai_100.json\n\n")
    
    for i, item in enumerate(items):
        title = item.get('title', '未知标题')
        author = item.get('author', '未知UP')
        views = item.get('view', 0)
        danmaku = item.get('danmaku', 0)
        likes = item.get('like', 0)
        coins = item.get('coin', 0)
        favs = item.get('favorite', 0)
        duration = item.get('duration', '未知')
        bvid = item.get('bvid', '')
        desc = item.get('desc', '')
        
        if desc:
            summary = desc[:200] if len(desc) > 200 else desc
        else:
            summary = f"B站AI技术视频，UP主{author}，播放{views}"
        
        f.write(f"### 第{i+1}条\n")
        f.write(f"- 标题: {title}\n")
        f.write(f"- UP主: {author}\n")
        f.write(f"- 播放: {views}\n")
        f.write(f"- 弹幕: {danmaku}\n")
        f.write(f"- 点赞: {likes}\n")
        f.write(f"- 投币: {coins}\n")
        f.write(f"- 收藏: {favs}\n")
        f.write(f"- 时长: {duration}\n")
        f.write(f"- BV号: {bvid}\n")
        f.write(f"- 内容总结: {summary}\n")
        f.write('\n')

print(f"B站: 写入 {len(items)} 条到 {output_file}")

# 抖音 - 检查raw文件
douyin_input = os.path.join(DATA_DIR, 'douyin_raw_1775696874698.json')
douyin_output = os.path.join(DATA_DIR, 'douyin.md')

if os.path.exists(douyin_input):
    with open(douyin_input, 'r', encoding='utf-8') as f:
        douyin_data = json.load(f)
    
    print(f"抖音raw数据条数: {len(douyin_data) if isinstance(douyin_data, list) else 'not a list, keys: ' + str(list(douyin_data.keys())[:5])}")
    
    if isinstance(douyin_data, list):
        # 过滤AI相关内容
        ai_keywords = ['ai', '人工智能', 'chatgpt', '大模型', '机器学习', '深度学习',
                       'aigc', 'llm', 'gpt', '文心一言', '通义千问', 'kimi', '豆包',
                       'claude', 'gemini', 'sora', 'openai', 'ai绘画', 'ai视频',
                       'ai工具', 'ai应用', 'deepseek']
        
        ai_items = []
        for item in douyin_data:
            title = str(item.get('title', item.get('desc', '')))
            is_ai = any(kw.lower() in title.lower() for kw in ai_keywords)
            if is_ai:
                ai_items.append(item)
                if len(ai_items) >= 100:
                    break
        
        if ai_items:
            with open(douyin_output, 'w', encoding='utf-8') as f:
                f.write("# 抖音AI技术热门内容\n\n")
                f.write(f"抓取时间: 2026-04-09\n")
                f.write(f"数据来源: douyin_raw_1775696874698.json\n\n")
                
                for i, item in enumerate(ai_items):
                    title = item.get('title', item.get('desc', '未知标题'))
                    author = item.get('author', item.get('nickname', '未知'))
                    likes = item.get('likes', item.get('digg_count', 0))
                    tags = item.get('topics', item.get('tags', []))
                    video_id = item.get('video_id', item.get('aweme_id', ''))
                    
                    tag_str = ' '.join([f'#{t}' for t in tags[:10]]) if tags else ''
                    
                    summary = title[:200] if len(title) > 200 else title
                    
                    f.write(f"### 第{i+1}条\n")
                    f.write(f"- 标题: {title}\n")
                    f.write(f"- 作者: @{author}\n")
                    f.write(f"- 点赞: {likes}\n")
                    f.write(f"- 话题: {tag_str}\n")
                    f.write(f"- 内容总结: {summary}\n")
                    f.write('\n')
            
            print(f"抖音: 写入 {len(ai_items)} 条AI内容到 {douyin_output}")
        else:
            print(f"抖音raw中没有找到AI相关内容，共{len(douyin_data)}条")
else:
    print(f"抖音raw文件不存在: {douyin_input}")
