#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sakana AI / Fugu 监控脚本
监控目标：
1. Sakana AI 官方博客 (https://sakana.ai/blog/)
2. arXiv 新论文 (Sakana AI 相关)
3. Hacker News 提及
4. GitHub 开源动态
"""
import sys
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlencode, quote

import urllib.request
import urllib.error

# 配置
WORKSPACE = Path(r"E:\workspace")
REPORT_DIR = WORKSPACE / "knowledge" / "sakana-fugu-monitor"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = REPORT_DIR / "monitor.log"

CST = timezone(timedelta(hours=8))
TIMEOUT = 15  # 每个请求 15 秒

KEYWORDS = [
    "Sakana AI", "SakanaAI", "Sakana Labs",
    "Fugu", "Fugu model", "Fugu-MT",
    "Trinity", "Conductor",
    "David Ha", "Llion Jones",  # 创始人
    "swarm intelligence model", "collective intelligence model",
    "model orchestration RL", "model composition"
]

SOURCES = {
    "blog": "https://sakana.ai/blog/",
    "arxiv_sakana": "https://arxiv.org/search/?searchtype=author&query=Sakana+AI",
    "arxiv_fugu": "https://arxiv.org/search/?searchtype=all&query=Fugu+model+Sakana",
    "hackernews": "https://hn.algolia.com/api/v1/search?query=Sakana+AI&tags=story",
    "github": "https://api.github.com/orgs/SakanaAI/repos",
}

def log(msg):
    ts = datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def fetch(url, headers=None):
    req = urllib.request.Request(url, headers={
        "User-Agent": "CaySon-Monitor/1.0",
        "Accept": "application/json,text/html",
        **(headers or {})
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, f"ERROR: {e}"

def check_blog():
    """抓取 Sakana AI 博客 - 解析 /slug/ 格式的博客文章 URL"""
    log("📰 检查 Sakana AI 博客...")
    code, html = fetch(SOURCES["blog"])
    if code != 200:
        return [{"source": "blog", "status": code, "error": html[:200]}]
    
    # 解析所有 <a> 标签，相对路径且非分类标签
    pattern = r'<a[^>]+href="(/[^"]+)"[^>]*>(.*?)</a>'
    matches = re.findall(pattern, html, re.DOTALL)
    
    items = []
    seen = set()
    for url, content in matches:
        # 过滤分类标签和导航
        if '?label=' in url or url in ('/', '/blog/') or len(url) < 3:
            continue
        # 清理 HTML 标签
        content_clean = re.sub(r'<[^>]+>', '', content)
        content_clean = re.sub(r'\s+', ' ', content_clean).strip()
        # 过滤掉 "read more" 之类
        if not content_clean or len(content_clean) < 5 or content_clean.lower() in ('read more', 'see more'):
            continue
        if content_clean in seen:
            continue
        seen.add(content_clean)
        items.append({
            "source": "blog",
            "title": content_clean,
            "url": f"https://sakana.ai{url}",
        })
    
    log(f"  找到 {len(items)} 篇博客")
    return items[:15]  # 最多 15 篇

def check_arxiv():
    """检查 arXiv Sakana AI 相关新论文"""
    log("📚 检查 arXiv 论文...")
    results = []
    
    # 搜索 Sakana AI
    code, html = fetch(SOURCES["arxiv_sakana"])
    if code == 200:
        # 提取论文标题
        title_pattern = r'<p class="title is-5 mathjax">\s*([^<]+?)\s*</p>'
        titles = re.findall(title_pattern, html)
        for t in titles[:5]:
            t = t.strip().replace("\n", " ")
            results.append({"source": "arxiv-sakana", "title": t, "url": SOURCES["arxiv_sakana"]})
    
    # 搜索 Fugu
    code, html = fetch(SOURCES["arxiv_fugu"])
    if code == 200:
        title_pattern = r'<p class="title is-5 mathjax">\s*([^<]+?)\s*</p>'
        titles = re.findall(title_pattern, html)
        for t in titles[:5]:
            t = t.strip().replace("\n", " ")
            results.append({"source": "arxiv-fugu", "title": t, "url": SOURCES["arxiv_fugu"]})
    
    log(f"  找到 {len(results)} 篇相关论文")
    return results

def check_hackernews():
    """检查 Hacker News"""
    log("🟠 检查 Hacker News...")
    code, body = fetch(SOURCES["hackernews"])
    if code != 200:
        return [{"source": "hn", "status": code, "error": body[:200]}]
    
    try:
        data = json.loads(body)
    except Exception as e:
        return [{"source": "hn", "error": f"parse error: {e}"}]
    
    items = []
    for hit in data.get("hits", [])[:10]:
        items.append({
            "source": "hackernews",
            "title": hit.get("title", ""),
            "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
            "points": hit.get("points", 0),
            "comments": hit.get("num_comments", 0),
            "created_at": hit.get("created_at", ""),
        })
    
    log(f"  找到 {len(items)} 条 HN 提及")
    return items

def check_github():
    """检查 Sakana AI GitHub 仓库"""
    log("💻 检查 GitHub...")
    code, body = fetch(SOURCES["github"], headers={"Accept": "application/vnd.github+json"})
    if code != 200:
        return [{"source": "github", "status": code, "error": body[:200]}]
    
    try:
        repos = json.loads(body)
    except Exception as e:
        return [{"source": "github", "error": f"parse error: {e}"}]
    
    items = []
    for repo in repos[:10]:
        items.append({
            "source": "github",
            "name": repo.get("full_name", ""),
            "description": repo.get("description", ""),
            "url": repo.get("html_url", ""),
            "stars": repo.get("stargazers_count", 0),
            "updated_at": repo.get("updated_at", ""),
        })
    
    log(f"  找到 {len(items)} 个仓库")
    return items

def main():
    log("=" * 60)
    log("🚀 Sakana AI / Fugu 监控启动")
    log("=" * 60)
    
    all_items = []
    all_items.extend(check_blog())
    all_items.extend(check_arxiv())
    all_items.extend(check_hackernews())
    all_items.extend(check_github())
    
    # 生成报告
    ts = datetime.now(CST).strftime("%Y%m%d_%H%M")
    report_path = REPORT_DIR / f"report_{ts}.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Sakana AI / Fugu 监控报告\n\n")
        f.write(f"**生成时间**: {datetime.now(CST).strftime('%Y-%m-%d %H:%M:%S')} (CST)\n")
        f.write(f"**总条目数**: {len(all_items)}\n\n")
        f.write("---\n\n")
        
        # 按 source 分组
        by_source = {}
        for item in all_items:
            src = item.get("source", "unknown")
            by_source.setdefault(src, []).append(item)
        
        # 中文标签映射
        source_cn = {
            "blog": "📰 官方博客",
            "arxiv-sakana": "📚 arXiv - Sakana AI",
            "arxiv-fugu": "📚 arXiv - Fugu",
            "hackernews": "🟠 Hacker News",
            "github": "💻 GitHub 仓库",
            "hn": "🟠 Hacker News",
        }
        
        for src in ["blog", "arxiv-sakana", "arxiv-fugu", "hackernews", "github", "hn"]:
            items = by_source.get(src, [])
            if not items:
                continue
            f.write(f"## {source_cn.get(src, src)}\n\n")
            for item in items:
                if "error" in item:
                    f.write(f"⚠️ 错误: {item.get('error', 'unknown')}\n\n")
                elif "status" in item:
                    f.write(f"⚠️ HTTP {item['status']}\n\n")
                else:
                    title = item.get("title") or item.get("name", "无标题")
                    url = item.get("url", "#")
                    desc = item.get("description", "")
                    extra = ""
                    if "stars" in item:
                        extra = f" ⭐{item['stars']}"
                    if "points" in item:
                        extra = f" 🔥{item['points']} 💬{item['comments']}"
                    f.write(f"- [{title}]({url}){extra}\n")
                    if desc:
                        f.write(f"  {desc}\n")
            f.write("\n")
    
    log(f"✅ 报告已生成: {report_path}")
    log(f"   总条目: {len(all_items)}")
    
    # 摘要输出（用于 cron 推送）
    print()
    print("=" * 50)
    print("📊 本次扫描摘要")
    print("=" * 50)
    by_source_count = {}
    for item in all_items:
        src = item.get("source", "unknown")
        by_source_count[src] = by_source_count.get(src, 0) + 1
    for src, count in by_source_count.items():
        print(f"  {source_cn.get(src, src)}: {count}")
    print(f"\n  报告文件: {report_path}")

if __name__ == "__main__":
    main()
