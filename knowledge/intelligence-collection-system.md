> **创建时间**：2026-05-28  
> **定位**：竞品情报、GEO行业、AI技术、市场消息、行业动态的自动化收集与报告系统

---

## 1. 🎯 这是什么

**情报收集系统** 是一套自动化情报采集与分析的工作流，通过 OpenClaw Cron 定时触发，使用多 Skill 协同收集各渠道信息，整理成 Markdown 报告后同步到知识库并推送到飞书群。

**解决的问题**：
- 竞品动态分散在 Facebook/Naver/Twitter 等多平台
- GEO 行业信息缺乏统一收集渠道
- AI 技术更新快，人工追踪效率低
- 市场/行业消息需要定期整理和回应

---

## 2. 📦 Skill 选型

### 核心 Skill

| 用途 | Skill | 版本 | 说明 |
|------|-------|------|------|
| 🤖 AI情报 | `ai-pulse` | 1.0.0 | 面向中文用户的AI情报站，每日简报/早报/午报/晚报 |
| 🕷️ 多平台爬虫 | `crawl4ai-skill` | 1.0.10 | AI驱动的网页抓取，Facebook/Naver/Twitter |
| 🎯 GEO垂直搜索 | `anysearch` | 1.0.2 | Agent专用搜索基础设施，GEO垂直领域覆盖 |
| 🔍 通用搜索 | `multi-search-engine` | 2.1.3 | 16个搜索引擎，多源检索 |
| 📊 竞品分析 | `admapix` | 1.0.29 | 广告情报、应用分析、竞品监控 |
| 📚 前沿研究 | `harness-research` | 1.0.0 | AI Agent前沿论文追踪，自动结构化分析 |
| 🔄 自进化引擎 | `harness-evolve` | 1.0.0 | 消费研究日志，系统自检，架构优化 |

### 辅助 Skill

| 用途 | Skill | 说明 |
|------|-------|------|
| 📝 飞书推送 | `feishu-doc` | 直接调飞书 Open API 创建文档 |
| 🧠 知识库同步 | knowledge-base/compile.py | Zilliz Cloud + ChromaDB 双写 |
| 🔍 内容总结 | `summarize` | 网页/PDF/YouTube 总结 |

---

## 3. 🏗️ 系统架构

```
┌────────────────────────────────────────────────────────────────────────┐
│                        情报收集系统                                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────────────────┐   │
│  │  OpenClaw   │───▶│   Cron       │───▶│  Isolated Sub-agent   │   │
│  │   定时调度   │    │  定时触发    │    │   (情报收集执行)       │   │
│  └──────────────┘    └──────────────┘    └────────────────────────┘   │
│                                                      │                  │
│          ┌───────────────────────────────────────────┤                  │
│          ▼                   ▼                   ▼                      │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────────────────┐   │
│  │   ai-pulse  │    │  crawl4ai    │    │      anysearch        │   │
│  │  每日AI简报  │    │ Facebook/    │    │   GEO垂直领域搜索      │   │
│  │  早/午/晚报  │    │ Twitter/Naver│    │   美团/清华/厂商      │   │
│  └──────────────┘    └──────────────┘    └────────────────────────┘   │
│                                                      │                  │
│                              ┌────────────────────────┤                  │
│                              ▼                        ▼                  │
│                    ┌──────────────────┐    ┌────────────────────────┐   │
│                    │  Multi-search    │    │      admapix          │   │
│                    │   Engine         │    │     竞品广告分析      │   │
│                    │  16搜索引擎      │    │                       │   │
│                    └──────────────────┘    └────────────────────────┘   │
│                                    │                                   │
│                                    ▼                                   │
│                    ┌─────────────────────────────────────────┐         │
│                    │         情报聚合与分析                    │         │
│                    │   (harness-research 结构化处理)          │         │
│                    └─────────────────────────────────────────┘         │
│                                    │                                   │
│           ┌────────────────────────┼────────────────────────┐          │
│           ▼                        ▼                        ▼          │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐   │
│  │  Markdown    │         │  知识库       │         │   飞书群     │   │
│  │  报告文档     │         │ Zilliz Cloud/Chroma│         │   推送报告    │   │
│  └──────────────┘         └──────────────┘         └──────────────┘   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 📋 收集任务清单

### 4.1 每日任务

| 时间 | 任务 | 数据源 | 工具 | 输出 |
|------|------|--------|------|------|
| 08:00 | AI早报 | ai-pulse | ai-pulse skill | 知识库 + 飞书群 |
| 12:00 | GEO动态 | 美团/清华/厂商 | anysearch | 知识库 |
| 14:00 | 社交媒体 | Facebook/Twitter | crawl4ai-skill | 知识库 |
| 18:00 | AI晚报+市场 | ai-pulse + admapix | ai-pulse + multi-search | 飞书群 |

### 4.2 每周任务

| 时间 | 任务 | 说明 |
|------|------|------|
| 周五 18:00 | 竞品周报 | 全方位汇总，GEO分析，趋势判断 |
| 周一 09:00 | 周回顾 | 上周情报回顾，重点跟进 |

### 4.3 收集范围

| 类别 | 关键词/来源 |
|------|-------------|
| 🏢 竞品情报 | 竞品动态、功能更新、价格策略 |
| 🌐 GEO相关 | GEO滥用/黑名单、美团GEO、清华GEO、生成式引擎优化 |
| 🤖 AI技术 | Agent、RAG、搜索、工具更新、MCP |
| 📊 市场消息 | ChatGPT广告、AI变现、商业化 |
| 📰 行业消息 | 方法论分享、内部分享、趋势分析 |

---

## 5. 🚀 部署步骤

### Step 1: 安装所需 Skills

```bash
# 进入 OpenClaw CLI 执行
openclaw skills install ai-pulse
openclaw skills install crawl4ai-skill
openclaw skills install anysearch
openclaw skills install admapix
openclaw skills install harness-research
openclaw skills install harness-evolve
```

**安全扫描（必须）**：
```bash
openclaw skills scan ai-pulse
openclaw skills scan crawl4ai-skill
openclaw skills scan anysearch
# 检查结果为 LOW 风险才继续安装
```

### Step 2: 创建情报收集脚本

创建 `E:\workspace\scripts\intelligence_collector.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情报收集系统 - 主收集程序
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# ========== 配置 ==========
OUTPUT_DIR = Path(__file__).parent.parent / "douyin-knowledge" / "intelligence"
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")
API_KEY_ANYSEARCH = os.environ.get("ANYSEARCH_API_KEY", "")

# 收集源配置
SOURCES = {
    "ai_news": {
        "name": "AI情报",
        "keywords": ["AI Agent", "RAG", "搜索", "GEO", "MCP"],
        "platform": "ai-pulse"
    },
    "geo_vertical": {
        "name": "GEO行业",
        "keywords": ["GEO黑名单", "美团GEO", "清华大学GEO", "生成式引擎优化", "GEO滥用"],
        "platform": "anysearch"
    },
    "competitor": {
        "name": "竞品动态",
        "keywords": ["AI搜索", "Perplexity", "Gemini", "Claude"],
        "platform": "multi-search-engine"
    },
    "social_media": {
        "name": "社交媒体",
        "platforms": ["facebook", "twitter"],
        "keywords": ["AI", "GEO", "search"]
    }
}

def run_command(cmd, timeout=120):
    """执行 shell 命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, 
            text=True, timeout=timeout, encoding='utf-8'
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", -1

def collect_ai_news():
    """收集AI情报（ai-pulse）"""
    # 使用 ai-pulse skill 获取每日简报
    cmd = 'opencli ai-pulse daily'
    stdout, stderr, code = run_command(cmd, timeout=60)
    return {"source": "ai-pulse", "content": stdout, "status": "ok" if code == 0 else "error"}

def collect_geo_news():
    """收集GEO行业垂直搜索（anysearch）"""
    results = []
    for keyword in SOURCES["geo_vertical"]["keywords"]:
        cmd = f'opencli anysearch search "{keyword}" --max_results 5'
        stdout, stderr, code = run_command(cmd, timeout=30)
        if code == 0:
            results.append({"keyword": keyword, "results": stdout})
    return {"source": "anysearch", "content": results}

def collect_social_media():
    """收集社交媒体（crawl4ai）"""
    # Facebook AI 群组
    fb_cmd = 'opencli crawl4ai facebook --query "AI GEO" --limit 10'
    # Twitter AI 话题
    tw_cmd = 'opencli crawl4ai twitter --query "AI GEO search" --limit 10'
    return {"source": "social_media", "status": "pending"}

def generate_report(data):
    """生成 Markdown 报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"""# 情报收集报告 - {timestamp}

## 今日摘要

## AI技术动态

## GEO行业动态

## 竞品情报

## 社交媒体热点

---
*由 OpenClaw 情报收集系统自动生成*
"""
    return report

def save_report(report, category="daily"):
    """保存报告到知识库"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{timestamp}_{category}.md"
    filepath = OUTPUT_DIR / filename
    filepath.write_text(report, encoding='utf-8')
    return filepath

def main():
    print(f"🕵️ 情报收集系统启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 收集 AI 情报
    print("📡 收集AI情报...")
    ai_data = collect_ai_news()
    
    # 2. 收集 GEO 垂直搜索
    print("🎯 收集GEO行业动态...")
    geo_data = collect_geo_news()
    
    # 3. 收集社交媒体
    print("🐦 收集社交媒体...")
    social_data = collect_social_media()
    
    # 4. 生成报告
    print("📝 生成报告...")
    report = generate_report({"ai": ai_data, "geo": geo_data, "social": social_data})
    
    # 5. 保存到知识库
    filepath = save_report(report)
    print(f"✅ 报告已保存: {filepath}")
    
    return {"status": "ok", "report": str(filepath)}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

### Step 3: 创建飞书推送脚本

创建 `E:\workspace\scripts\feishu_intelligence_report.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书情报报告推送
直接调飞书 Open API，避免 SIGKILL 问题
"""

import requests
import json
from datetime import datetime

APP_ID = "cli_a9324982073a1bc8"
APP_SECRET = "2tOQnQmwk2bHOUAHPsHCjfcv4zLreFWE"
BASE_URL = "https://open.feishu.cn/open-apis"

def get_token():
    resp = requests.post(f"{BASE_URL}/auth/v3/tenant_access_token/internal", json={
        "app_id": APP_ID, "app_secret": APP_SECRET
    }, timeout=10)
    return resp.json().get("tenant_access_token")

def create_doc(token, title):
    resp = requests.post(f"{BASE_URL}/docx/v1/documents", 
        headers={"Authorization": f"Bearer {token}"},
        json={"title": title}, timeout=10)
    return resp.json()

def add_blocks(token, doc_token, blocks):
    resp = requests.post(
        f"{BASE_URL}/docx/v1/documents/{doc_token}/blocks/{doc_token}/children",
        headers={"Authorization": f"Bearer {token}"},
        json={"children": blocks, "index": -1}, timeout=10)
    return resp.json()

def text_block(text):
    return {"block_type": 2, "text": {"elements": [{"text_run": {"content": text}}], "style": {}}}

def heading_block(text, level=1):
    block_types = {1: 3, 2: 4, 3: 5}
    return {f"block_type": block_types[level], f"heading{level}": {"elements": [{"text_run": {"content": text}}], "style": {}}}

def divider_block():
    return {"block_type": 22, "divider": {}}

def send_to_feishu(title, content_blocks):
    """创建飞书文档并返回链接"""
    token = get_token()
    doc = create_doc(token, title)
    doc_token = doc.get("data", {}).get("document", {}).get("document_id")
    if doc_token:
        add_blocks(token, doc_token, content_blocks)
        return f"https://feishu.cn/docx/{doc_token}"
    return None

def build_report_blocks(report_content):
    """构建报告内容块"""
    blocks = [
        heading_block("📊 情报收集报告", 1),
        text_block(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"),
        divider_block(),
    ]
    # 解析报告内容并添加blocks
    for line in report_content.split('\n'):
        if line.startswith('## '):
            blocks.append(heading_block(line[3:], 2))
        elif line.startswith('### '):
            blocks.append(heading_block(line[4:], 3))
        elif line.strip():
            blocks.append(text_block(line))
    return blocks

def main(report_file, title):
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = build_report_blocks(content)
    url = send_to_feishu(title, blocks)
    
    return {"status": "ok", "url": url} if url else {"status": "error"}

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: feishu_intelligence_report.py <report_file> <title>")
        sys.exit(1)
    result = main(sys.argv[1], sys.argv[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

### Step 4: 配置 Cron 定时任务

```bash
# 每日 08:00 AI早报收集
openclaw cron create \
  --name "情报收集-AI早报" \
  --schedule "0 8 * * * @ Asia/Shanghai" \
  --agent-id main \
  --timeout 300 \
  --mode isolated \
  --delivery-mode none \
  --message "执行 E:\workspace\scripts\intelligence_collector.py 收集AI早报并推送飞书"

# 每日 12:00 GEO行业动态
openclaw cron create \
  --name "情报收集-GEO动态" \
  --schedule "0 12 * * * @ Asia/Shanghai" \
  --agent-id main \
  --timeout 300 \
  --mode isolated \
  --delivery-mode none \
  --message "使用 anysearch 收集GEO行业垂直搜索结果"

# 每日 18:00 晚间报告
openclaw cron create \
  --name "情报收集-晚间报告" \
  --schedule "0 18 * * * @ Asia/Shanghai" \
  --agent-id main \
  --timeout 300 \
  --mode isolated \
  --delivery-mode none \
  --message "生成当日情报汇总报告并推送到飞书群"

# 周五 18:00 竞品周报
openclaw cron create \
  --name "情报收集-竞品周报" \
  --schedule "0 18 * * 5 @ Asia/Shanghai" \
  --agent-id main \
  --timeout 600 \
  --mode isolated \
  --delivery-mode none \
  --message "生成竞品周报，包含GEO/AI技术/市场动态全面分析"
```

---

## 6. 🔧 调教指南

### 6.1 关键词调教

根据需求，调整 `intelligence_collector.py` 中的关键词：

```python
SOURCES = {
    "ai_news": {
        "name": "AI情报",
        "keywords": [
            "AI Agent", "RAG", "搜索", "GEO", "MCP",
            "Perplexity", "Claude", "Gemini", "ChatGPT"
        ],
        "exclude": ["广告", "推广"]  # 排除噪音
    },
    "geo_vertical": {
        "name": "GEO行业",
        "keywords": [
            "GEO黑名单", "美团GEO", "清华大学GEO", 
            "生成式引擎优化", "GEO滥用",
            "GEO服务商", "搜索引擎优化"
        ],
        "sources": ["36kr", "zhihu", "twitter"]
    },
    "competitor": {
        "name": "竞品动态",
        "keywords": [
            "AI搜索竞品", "Perplexity更新", 
            "AI工具新功能", "AI定价策略"
        ]
    }
}
```

### 6.2 来源平台调教

```python
PLATFORMS = {
    "facebook": {
        "enabled": True,
        "groups": ["AI Marketing", "GEO SEO", "AI Tools"],
        "crawl4ai_params": {"limit": 20, "sort": "recent"}
    },
    "twitter": {
        "enabled": True,
        "hashtags": ["#AI", "#GEO", "#AIMarketing"],
        "crawl4ai_params": {"limit": 30}
    },
    "naver": {
        "enabled": True,
        "cafes": ["互联网营销", "AI技术"],
        "crawl4ai_params": {"limit": 15}
    }
}
```

### 6.3 报告格式调教

根据习惯，调整报告格式：

```markdown
# 📊 [日期] 情报收集报告

## 🎯 今日重点
- [重要情报1]
- [重要情报2]

## 🏢 竞品动态
### 产品更新
### 价格策略

## 🌐 GEO行业
### 技术动态
### 风险预警（滥用/黑名单）

## 🤖 AI技术
### 新工具/新功能
### 技术趋势

## 📰 市场消息
### 商业化动态
### 行业活动

## 💡 潜在机会
- [机会点1]

## ⚠️ 潜在威胁
- [威胁点1]

---
*由 OpenClaw 情报收集系统自动生成 | 整理：2026-05-28*
```

---

## 7. 📁 输出结构

```
workspace\
├── facebook-knowledge\
│   └── intelligence\           # 情报收集目录
│       ├── 2026-05-28_daily.md
│       ├── 2026-05-28_geo.md
│       ├── 2026-05-28_competitor.md
│       └── 2026-05-28_weekly.md   # 周报
├── twitter-knowledge\
│   └── intelligence\           # 情报收集目录
│       ├── 2026-05-28_daily.md
│       ├── 2026-05-28_geo.md
│       ├── 2026-05-28_competitor.md
│       └── 2026-05-28_weekly.md   # 周报
├── knowledge\
│   └── intelligence-collection-system.md  # 本文档
└── scripts\
    ├── intelligence_collector.py     # 收集主程序
    └── feishu_intelligence_report.py # 飞书推送
```

---

## 8. ✅ 优点

- **多源覆盖**：使用 crawl4ai 来针对 Facebook/Twitter/Naver/知乎/36kr/InfoQ 全渠道
- **自动化高**：Cron 定时触发，无需人工干预
- **垂直深入**：anysearch 支持 GEO 等垂直领域深度搜索
- **格式规范**：统一 Markdown 格式，便于后续分析
- **双端存储**：知识库（Zilliz Cloud/ChromaDB）+ 飞书文档

## 8.5 📊 方案对比

### 方案一：纯 OpenClaw Cron + Sub-agent

| 维度 | 评分 | 说明 |
|------|------|------|
| 部署复杂度 | ⭐⭐ | 直接使用现有基础设施，无需额外安装 |
| 收集能力 | ⭐⭐⭐⭐ | opencli + anysearch + multi-search 组合覆盖广 |
| 社交媒体 | ⭐⭐⭐ | crawl4ai 支持 Facebook/Twitter/Naver |
| 成本 | ⭐⭐⭐⭐⭐ | 免费为主，仅 anysearch 可能需要 API Key |
| 维护成本 | ⭐⭐⭐ | 需要自己写脚本，但逻辑清晰 |
| 可靠性 | ⭐⭐⭐⭐ | Cron 稳定，SIGKILL 已绕过 |

**适用场景**：预算有限，愿意投入时间配置的中型团队

**核心命令**：
```bash
openclaw cron create --name "情报收集" --schedule "0 8 * * *" --agent-id main
```

---

### 方案二：Harness Agent 框架

| 维度 | 评分 | 说明 |
|------|------|------|
| 部署复杂度 | ⭐⭐⭐⭐ | 需要安装配置 harness-engineering 系列 |
| 收集能力 | ⭐⭐⭐⭐⭐ | harness-research + 自进化能力，最强 |
| 社交媒体 | ⭐⭐⭐⭐ | 多 agent 协作，覆盖更全面 |
| 成本 | ⭐⭐⭐ | 需要 harness 相关 skill 配合 |
| 维护成本 | ⭐⭐⭐⭐⭐ | harness-evolve 自动优化，几乎免维护 |
| 可靠性 | ⭐⭐⭐⭐ | 自进化引擎持续改进 |

**适用场景**：大型团队，追求长期自动化优化的企业

**核心 Skill**：
- `harness-research` - 前沿论文追踪
- `harness-evolve` - 自进化引擎
- `harness-engineering` - 工程治理

**推荐指数**：⭐⭐⭐⭐（4星）

---

### 方案三：混合方案（推荐 ✅）

| 维度 | 评分 | 说明 |
|------|------|------|
| 部署复杂度 | ⭐⭐⭐ | 介于纯 OpenClaw 和纯 Harness 之间 |
| 收集能力 | ⭐⭐⭐⭐⭐ | OpenClaw 收集 + Harness 研究，最强组合 |
| 社交媒体 | ⭐⭐⭐⭐ | OpenClaw 的 opencli/crawl4ai |
| 成本 | ⭐⭐⭐⭐ | 主要免费，仅 anysearch 可能需要 Key |
| 维护成本 | ⭐⭐⭐⭐ | OpenClaw 日常 + Harness 周优化 |
| 可靠性 | ⭐⭐⭐⭐⭐ | 双重保障，最稳定 |

**适用场景**：追求效果最大化，愿意适度投入的企业

**核心架构**：
```
OpenClaw Cron (定时收集)
    ↓
OpenClaw Sub-agent (执行收集)
    ↓
ai-pulse + crawl4ai + anysearch + multi-search
    ↓
Markdown 报告 → 知识库 + 飞书群
    ↓
Harness (周回顾 + 优化建议)
```

**推荐指数**：⭐⭐⭐⭐⭐（5星）✅

---

### 三方案对比总结

| 对比项 | 方案一：纯OpenClaw | 方案二：纯Harness | 方案三：混合方案 ✅ |
|--------|-------------------|-------------------|-------------------|
| **部署速度** | 快 | 慢 | 中 |
| **初始成本** | 低 | 高 | 中 |
| **收集深度** | 深 | 深 | 最深 |
| **自动化程度** | 高 | 最高 | 最高 |
| **维护工作量** | 中 | 低 | 低 |
| **扩展性** | 中 | 高 | 高 |
| **适合规模** | 小/中 | 中/大 | 中/大 |
| **推荐指数** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**最终推荐**：
- **小型团队/个人**：方案一（纯 OpenClaw），快速上手
- **中大型团队**：方案三（混合方案），效果最佳
- **研究导向团队**：方案二 + harness-research，最强研究能力

## 9. ❌ 缺点

- **需要 API Key**：anysearch、ai-pulse 可能需要付费 Key
- **社交媒体限制**：Facebook/Naver 可能需要登录态
- **报告质量依赖**：关键词配置需要持续优化

## 10. 🎬 使用场景

1. **每日晨会**：08:00 推送 AI 早报，了解最新动态
2. **竞品监控**：GEO 行业动态实时追踪
3. **客户回应**：社交媒体热点快速响应
4. **周报素材**：周五自动生成竞品周报

---

## 11. 🔧 运行依赖环境

- Python 3.8+
- OpenClaw CLI
- Chrome 浏览器（crawl4ai 需要）
- 网络访问：Facebook/Twitter/Naver/知乎/36kr

## 12. 🚀 部署注意点

### 12.1 API Key 配置

```bash
# .env 配置
ANYSEARCH_API_KEY=your_key_here
AI_PULSE_API_KEY=your_key_here
FEISHU_WEBHOOK=your_webhook_here
```

### 12.2 权限要求

- 飞书文档创建权限
- 知识库写入权限
- 社交媒体爬取（遵守平台 TOS）

### 12.3 调优建议

1. **初期**：先手动测试各数据源，确保可访问
2. **中期**：根据实际噪音调整关键词
3. **后期**：结合 harness-evolve 实现自动优化

---

## 13. 🕳️ 避坑指南

| 坑 | 解决方案 |
|------|---------|
| 飞书 SIGKILL | 直接调飞书 API，不走 sync_feishu.py |
| 社交媒体登录态 | 使用 crawl4ai 的 cookie 模式 |
| 报告格式混乱 | 统一使用 Markdown 模板 |
| 关键词噪音 | 添加 exclude 列表过滤 |
| API 限流 | 添加延时，合理分配请求 |

---

## 14. 📊 总结

**部署推荐指数**：⭐⭐⭐⭐⭐（5星）

**适用性**：
- ✅ 竞品情报收集 → 非常适合
- ✅ GEO 行业追踪 → 非常适合
- ✅ AI 技术动态 → 非常适合
- ✅ 社交媒体监控 → 比较适合
- ⚠️ 需要一定配置工作

**核心价值**：
1. **省时间**：自动化收集，每天省 2-3 小时人工
2. **覆盖全**：多源整合，比单一来源更全面
3. **可追溯**：知识库存档，可随时检索历史
4. **易行动**：格式规范，直接可用于客户回应

---

*本文档 最后更新：2026-05-28*
