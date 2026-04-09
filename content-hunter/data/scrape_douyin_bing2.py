"""
Bing视频搜索 + yt-dlp 抓取抖音AI内容
"""
import re
import os
import time
import requests
import subprocess
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

def get_yt_dlp_info(link, retries=2):
    """用yt-dlp获取视频信息"""
    for attempt in range(retries):
        try:
            result = subprocess.run(
                ['yt-dlp', '--get-title', '--get-uploader', '--get-duration', 
                 '--no-warnings', '-J', link],
                capture_output=True, text=True, timeout=20,
                encoding='utf-8', errors='replace'
            )
            if result.returncode == 0 and result.stdout.strip():
                info = json.loads(result.stdout)
                title = info.get('title', '')
                author = info.get('uploader', '未知')
                dur = info.get('duration', 0)
                if dur:
                    m, s = divmod(int(dur), 60)
                    duration = f"{m}:{s:02d}"
                else:
                    duration = "未知"
                return title, author, duration
        except Exception as e:
            pass
        time.sleep(1)
    return None, '未知', '未知'

def search_bing_douyin(keyword, pages=3):
    """从Bing视频搜索获取抖音视频链接"""
    all_links = []
    
    for page in range(pages):
        offset = page * 10
        url = f"https://cn.bing.com/videos/search?q={requests.utils.quote(keyword)}+site:douyin.com&first={offset}&FORM=HDRSC4"
        headers = {
            "User-Agent": PC_UA,
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            # 提取所有douyin.com链接
            links = re.findall(r'href="(https?://[^"]*douyin\.com[^"]*)"', resp.text)
            links = list(dict.fromkeys(links))
            all_links.extend(links)
            print(f"  Page {page+1}: {len(links)} links found (total: {len(all_links)})")
        except Exception as e:
            print(f"  Page {page+1} error: {e}")
        time.sleep(0.5)
    
    return all_links

def is_ai_related(title, author=""):
    ai_kws = [
        'ai', '人工智能', 'chatgpt', 'gpt', '大模型', 'llm', '深度学习', '机器学习',
        '神经网络', 'openai', '文心', '通义', 'kimi', '豆包', 'deepseek', 'gemini',
        'copilot', 'midjourney', 'diffusion', 'aigc', 'agent', '智能体', '生成式',
        'prompt', '提示词', '开源模型', 'sora', 'runway', 'pika', 'cursor', 'claude',
        '数字人', 'ai工具', 'ai应用', 'ai助手', 'ai创作', 'ai学习', 'ai教程',
        'langchain', 'rag', 'embedding', '向量', '微调', '部署', '推理', 'token',
        '自动化', '机器人', 'python', '编程', '开发', '模型', '算法'
    ]
    text = (title + author).lower()
    return any(kw.lower() in text for kw in ai_kws)

def main():
    NOW = datetime.now().strftime("%Y-%m-%d")
    douyin_path = os.path.join(DATA_DIR, "douyin.md")
    existing_count = count_items(douyin_path)
    print(f"Current: {existing_count} items, starting from #{existing_count + 1}")
    
    # 读取已有标题避免重复
    seen_titles = set()
    if os.path.exists(douyin_path):
        with open(douyin_path, "r", encoding="utf-8") as f:
            for line in f:
                m = re.search(r'- 标题: (.+)', line)
                if m:
                    seen_titles.add(m.group(1).strip())
    
    keywords = [
        "AI人工智能教程", "ChatGPT使用技巧", "大模型应用案例", "AI工具推荐",
        "AI绘画教学", "AI视频制作", "AI数字人", "AI智能体", "DeepSeek教程",
        "AI编程技巧", "本地AI部署", "开源大模型", "AIGC创作", "AI自动化",
        "AI写作技巧", "AI数据分析"
    ]
    
    all_new = []
    
    for kw in keywords:
        if len(all_new) >= 100:
            break
        print(f"\nKeyword: {kw}")
        links = search_bing_douyin(kw, pages=2)
        
        for link in links:
            if len(all_new) >= 100:
                break
            
            # 用yt-dlp获取信息
            title, author, duration = get_yt_dlp_info(link)
            if title is None:
                continue
            
            # 跳过非AI内容
            if not is_ai_related(title, author):
                continue
            
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
            idx = existing_count + len(all_new) + 1
            entry = f"""
### 第{idx}条
- 标题: {title}
- 作者: @{author}
- 点赞: 未知
- 话题: #{kw}
- 时长: {duration}
- 链接: {link}
- 内容总结: {title}
"""
            all_new.append(entry)
            print(f"  + {title[:50]}")
        
        time.sleep(1)
    
    if all_new:
        content = "\n".join(all_new)
        header = f"\n\n---\n\n## 抖音 AI内容追加批次 ({NOW} 13:00) - 新增 {len(all_new)} 条\n\n"
        save_append(douyin_path, header + content)
        print(f"\n[DONE] Douyin: appended {len(all_new)} items")
        print(f"  Total now: {existing_count + len(all_new)} items")
    else:
        print("\n[WARN] No new items retrieved")

if __name__ == "__main__":
    main()
