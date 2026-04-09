"""
抖音热搜 + 上升热点抓取 - 追加100条
"""
import requests
import re
import os
import time
import json
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"

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

def fetch_douyin_hot():
    """获取抖音热搜数据"""
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
    headers = {
        "User-Agent": PC_UA,
        "Referer": "https://www.douyin.com/",
    }
    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "detail_list": "1",
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"API请求失败: {e}")
        return {}

def collect_douyin_100(existing_count):
    """抓取抖音热搜100条"""
    print(f"[抖音] 从第{existing_count+1}条开始抓取...")
    
    data = fetch_douyin_hot()
    
    # 保存原始JSON（更新）
    json_path = os.path.join(DATA_DIR, "douyin_response.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  已保存原始数据到 douyin_response.json")
    
    word_list = data.get("data", {}).get("word_list", [])
    trending_list = data.get("data", {}).get("trending_list", [])
    
    print(f"  热搜词: {len(word_list)} 条")
    print(f"  上升热点: {len(trending_list)} 条")
    
    # AI关键词过滤
    ai_keywords = [
        "AI", "ChatGPT", "DeepSeek", "GPT", "AIGC", "人工智能", "大模型", "LLM",
        "文生图", "AI绘画", "AI视频", "AI助手", "AI工具", "AI教程", "AI写作",
        "Midjourney", "Sora", "Gemini", "Copilot", "Claude", "Grok", "豆包",
        "Kimi", "智谱", "讯飞", "百度AI", "阿里AI", "腾讯AI", "华为AI",
        "机器学习", "深度学习", "神经网络", "自动驾驶", "智能音箱", "人脸识别",
        "ChatGPT", "OpenAI", "LLM", "RAG", "Agent", "AGI", "AIPC", "AI手机",
        "AI芯片", "AI服务器", "Diffusion", "Transformer", "StableDiffusion",
        "提示词", "Prompt", "智能体", "AI办公", "AI教育", "AI医疗", "AI客服",
        "AI写真", "AI配音", "AI翻译", "AI音乐", "AI编程", "AI建模", "AI游戏"
    ]
    
    all_items = []
    seen = set()
    
    # 处理热搜词
    for word in word_list:
        if len(all_items) >= 100:
            break
        try:
            word_text = word.get("word", "")
            word_schema = word.get("schema", "")
            hot_value = word.get("hot_value", 0)
            label = word.get("label", "")
            
            # 检查是否AI相关
            is_ai = any(kw.lower() in word_text.lower() for kw in ai_keywords)
            
            if is_ai:
                key = word_text
                if key in seen:
                    continue
                seen.add(key)
                
                hot_str = format_hot_value(hot_value)
                idx = existing_count + len(all_items) + 1
                item = f"""
### 第{idx}条
- 话题: {word_text}
- 热度: {hot_str}
- 相关视频: {label or '未知'}
- 话题: #上升热点 #抖音 #热搜 #AI
- 内容总结: 抖音热搜话题「{word_text}」，热度值{hot_str}
"""
                all_items.append(item)
        except Exception as e:
            continue
    
    # 处理上升热点
    for trend in trending_list:
        if len(all_items) >= 100:
            break
        try:
            trend_word = trend.get("word", "")
            trend_schema = trend.get("schema", "")
            hot_value = trend.get("hot_value", 0)
            
            # 检查是否AI相关
            is_ai = any(kw.lower() in trend_word.lower() for kw in ai_keywords)
            
            if is_ai:
                key = trend_word
                if key in seen:
                    continue
                seen.add(key)
                
                hot_str = format_hot_value(hot_value)
                idx = existing_count + len(all_items) + 1
                item = f"""
### 第{idx}条
- 话题: {trend_word}
- 热度: {hot_str}
- 相关视频: 上升热点
- 话题: #上升热点 #抖音 #热搜 #AI
- 内容总结: 抖音上升热点话题「{trend_word}」，热度值{hot_str}
"""
                all_items.append(item)
        except Exception as e:
            continue
    
    # 如果AI热搜不够，补充通用热搜
    for word in word_list:
        if len(all_items) >= 100:
            break
        try:
            word_text = word.get("word", "")
            hot_value = word.get("hot_value", 0)
            label = word.get("label", "")
            
            key = word_text
            if key in seen:
                continue
            seen.add(key)
            
            hot_str = format_hot_value(hot_value)
            idx = existing_count + len(all_items) + 1
            item = f"""
### 第{idx}条
- 话题: {word_text}
- 热度: {hot_str}
- 相关视频: {label or '未知'}
- 话题: #抖音 #热搜
- 内容总结: 抖音热搜话题「{word_text}」，热度值{hot_str}
"""
            all_items.append(item)
        except Exception as e:
            continue
    
    # 追加保存
    filepath = os.path.join(DATA_DIR, "douyin.md")
    content = "\n".join(all_items)
    save_append(filepath, content)
    print(f"[抖音] 追加 {len(all_items)} 条完成 (总: {existing_count + len(all_items)})")

if __name__ == "__main__":
    douyin_path = os.path.join(DATA_DIR, "douyin.md")
    existing = count_items(douyin_path)
    print(f"当前: 抖音 {existing} 条")
    
    collect_douyin_100(existing)
    
    new_count = count_items(douyin_path)
    print(f"结果: 抖音 {new_count} 条 (+{new_count - existing})")
