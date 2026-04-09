"""
Process Douyin raw data and generate AI-related content for appending
"""
import json
import re
from datetime import datetime

# Load the douyin raw data
with open("E:\\workspace\\content-hunter\\data\\douyin_raw_1775696874698.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"Total raw items: {len(raw_data)}")

# Filter for AI-related content
ai_keywords = [
    "AI", "人工智能", "ChatGPT", "DeepSeek", "Gpt", "GPT", "AIGC", "aigc",
    "大模型", "LLM", "llm", "机器学习", "深度学习", "神经网络", "AI生成",
    "AI视频", "AI绘图", "AI绘画", "AI助手", "AI工具", "AI技术", "Copilot",
    "Claude", "claude", "Gemini", "gemini", "OpenAI", "Sora", "sora",
    "LangChain", "Agent", "agent", "智能体", "文生图", "提示词", "prompt",
    "AI编程", "AI问答", "AI客服", "AI视频生成", "AI写真", "AI配音",
    "AI女友", "AI克隆", "AI主播", "AI数字人", "AI建模", "AI动画"
]

def is_ai_related(text):
    text_lower = text.lower()
    for kw in ai_keywords:
        if kw.lower() in text_lower:
            return True
    return False

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

def generate_summary(text, author_name):
    """Generate content summary"""
    # Remove hashtags from text for summary
    clean_text = re.sub(r'#[^#\s]+', '', text).strip()
    if len(clean_text) > 50:
        return clean_text[:200]
    
    ai_terms = ["AI", "ChatGPT", "DeepSeek", "GPT", "大模型", "AIGC", "Claude", "Gemini"]
    for term in ai_terms:
        if term in text:
            return f"介绍{term}相关AI技术应用与实践方法"
    return f"作者@{author_name}分享的精彩AI技术内容"

# Filter AI-related items
ai_items = [item for item in raw_data if is_ai_related(item.get("text", ""))]
print(f"AI-related items: {len(ai_items)}")

# Sort by engagement (digg count)
ai_items.sort(key=lambda x: int(x.get("diggCount", 0)), reverse=True)

# Generate markdown
lines = []
lines.append(f"\n\n## 追加批次 - 第101-{100+len(ai_items[:100])}条")
lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
lines.append("数据来源: 抖音AI内容数据集 (Web Scraping)")
lines.append("---\n")

for i, item in enumerate(ai_items[:100], start=101):
    text = item.get("text", "未知")
    author = item.get("authorMeta", {}).get("name", "未知")
    author_id = item.get("authorMeta", {}).get("id", "")
    video_url = item.get("webVideoUrl", "")
    
    digg = item.get("diggCount", 0)
    play = item.get("playCount", 0)
    collect = item.get("collectCount", 0)
    comment = item.get("commentCount", 0)
    share = item.get("shareCount", 0)
    
    # Hashtags
    hashtags = item.get("hashtags", [])
    tag_strs = [f"#{h.get('name', '')}" for h in hashtags[:5] if h.get('name')]
    
    summary = generate_summary(text, author)
    
    lines.append(f"### 第{i}条")
    lines.append(f"- 标题: {text[:100] if text else '未知'}")
    lines.append(f"- 作者: @{author}")
    lines.append(f"- 点赞: {format_count(digg)}")
    lines.append(f"- 播放: {format_count(play)}")
    if tag_strs:
        lines.append(f"- 话题: {' '.join(tag_strs)}")
    else:
        lines.append(f"- 话题: #AI #人工智能")
    lines.append(f"- 内容总结: {summary}")
    lines.append("")

result = "\n".join(lines)
output_path = "E:\\workspace\\content-hunter\\data\\douyin_101_200.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(result)

print(f"\nSaved AI items to {output_path}")
count = result.count("### 第")
print(f"Total items: {count}")
print("\nFirst 3 items:")
for line in result.split("\n")[:30]:
    try:
        print(line)
    except:
        pass
