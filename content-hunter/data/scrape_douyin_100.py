"""
抖音AI内容抓取 - 追加模式
处理已保存的 douyin_response.json (curl抓取的热榜数据)
"""
import json
import re
from datetime import datetime

DATA_DIR = "E:\\workspace\\content-hunter\\data\\"
DOUYIN_FILE = DATA_DIR + "douyin.md"
JSON_FILE = DATA_DIR + "douyin_response.json"

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

def format_hot_value(v):
    """格式化热度值"""
    try:
        v = int(v)
    except:
        v = 0
    if v >= 100000000:
        return f"{v/100000000:.1f}亿"
    elif v >= 10000:
        return f"{v/10000:.1f}万"
    elif v > 0:
        return str(v)
    return "未知"

def main():
    print("=" * 60)
    print("抖音AI内容抓取")
    print("=" * 60)
    
    # 读取JSON数据
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取JSON失败: {e}")
        return
    
    # 解析热搜词 + 上升热点
    word_list = data.get("data", {}).get("word_list", [])
    trending_list = data.get("data", {}).get("trending_list", [])
    
    all_topics = []
    
    # AI相关关键词
    ai_keywords = [
        "AI", "ChatGPT", "DeepSeek", "GPT", "AIGC", "人工智能", "大模型", "LLM",
        "机器学习", "深度学习", "神经网络", "AI生成", "AI视频", "AI绘图",
        "AI绘画", "AI助手", "AI工具", "AI技术", "Copilot", "Claude", "Gemini",
        "OpenAI", "Sora", "LangChain", "Agent", "智能体", "文生图", "提示词",
        "prompt", "AI编程", "AI问答", "AI视频生成", "AI教程", "国产AI",
        "AI产品", "AI应用", "AI圈", "AI行业", "AI时代", "硅基", "AI学习"
    ]
    
    # 处理热搜词
    for item in word_list:
        word = item.get("word", "")
        hot_value = item.get("hot_value", 0)
        video_count = item.get("video_count", 0)
        sentence_tag = item.get("sentence_tag", 0)
        position = item.get("position", 0)
        
        is_ai = any(kw.lower() in word.lower() for kw in ai_keywords)
        label = item.get("label", 0)
        label_desc = {
            0: "普通",
            1: "热", 2: "沸", 3: "爆",
            5: "新人", 8: "娱乐", 9: "社会",
            11: "赛事", 16: "美食"
        }.get(label, str(label))
        
        topic_type = "AI" if is_ai else "热门"
        if hot_value > 0:
            all_topics.append({
                "word": word,
                "hot_value": hot_value,
                "video_count": video_count,
                "position": position,
                "is_ai": is_ai,
                "topic_type": topic_type,
                "label_desc": label_desc
            })
    
    # 处理上升热点（更多样）
    for item in trending_list:
        word = item.get("word", "")
        hot_value = item.get("hot_value", 0) or 0
        video_count = item.get("video_count", 0)
        is_ai = any(kw.lower() in word.lower() for kw in ai_keywords)
        
        if word and not any(t["word"] == word for t in all_topics):
            topic_type = "AI" if is_ai else "上升热点"
            all_topics.append({
                "word": word,
                "hot_value": hot_value,
                "video_count": video_count,
                "position": 0,
                "is_ai": is_ai,
                "topic_type": topic_type,
                "label_desc": "上升热点"
            })
    
    print(f"获取热搜话题: {len(word_list)} 条")
    print(f"获取上升热点: {len(trending_list)} 条")
    print(f"合计话题: {len(all_topics)} 条")
    
    # AI话题优先
    ai_topics = [t for t in all_topics if t["is_ai"]]
    non_ai_topics = [t for t in all_topics if not t["is_ai"]]
    
    print(f"AI相关话题: {len(ai_topics)} 条")
    print(f"其他热门: {len(non_ai_topics)} 条")
    
    # 优先取AI话题，不够100条则补充其他热门
    selected = ai_topics[:100]
    if len(selected) < 100:
        remaining_needed = 100 - len(selected)
        # 找非AI话题中热度高的
        sorted_non_ai = sorted(non_ai_topics, key=lambda x: x["hot_value"], reverse=True)
        for t in sorted_non_ai:
            if len(selected) >= 100:
                break
            if t not in selected:
                selected.append(t)
    
    print(f"选中话题: {len(selected)} 条")
    
    # 读取已有条数
    existing_count = read_existing_count(DOUYIN_FILE)
    start_num = existing_count + 1
    print(f"当前文件已有: {existing_count} 条")
    print(f"本次追加: {min(len(selected), 100)} 条 (从第{start_num}条开始)")
    
    # 生成 Markdown
    lines = []
    lines.append(f"\n\n## 追加批次 - 第{start_num}-{start_num + min(len(selected), 100) - 1}条")
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("数据来源: 抖音热榜 API (移动端)")
    lines.append("---\n")
    
    items_to_save = selected[:100]
    for i, topic in enumerate(items_to_save, start=start_num):
        word = topic["word"]
        hot = format_hot_value(topic["hot_value"])
        videos = topic["video_count"]
        is_ai = topic["is_ai"]
        topic_type = topic["topic_type"]
        label = topic["label_desc"]
        
        tag = f"#{topic_type} #抖音 #热搜 #{label}"
        
        # 生成摘要
        if is_ai:
            summary = f"抖音热搜AI相关话题「{word}」，热度约{hot}，相关视频{videos}个"
        elif topic["hot_value"] > 0:
            summary = f"抖音热门话题「{word}」，热度约{hot}，相关视频{videos}个"
        else:
            summary = f"抖音上升热点话题「{word}」，相关视频{videos}个"
        
        lines.append(f"### 第{i}条")
        lines.append(f"- 话题: {word}")
        lines.append(f"- 热度值: {hot}")
        lines.append(f"- 相关视频: {videos} 个")
        lines.append(f"- 话题: {tag}")
        lines.append(f"- 内容总结: {summary}")
        lines.append("")
    
    # 追加写入文件
    content = "\n".join(lines)
    with open(DOUYIN_FILE, "a", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\n已追加 {len(items_to_save)} 条到 {DOUYIN_FILE}")
    print(f"文件现总计约 {existing_count + len(items_to_save)} 条")

if __name__ == "__main__":
    main()
