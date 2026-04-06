#!/usr/bin/env python3
"""Compile bilibili data and create douyin report."""
import os

# === BILIBILI: Check current file state ===
filepath = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data", "bilibili.md")
if os.path.exists(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count("### 第")
    print(f"[OK] BILIBILI: {count} items in file")
else:
    print(f"[WARN] BILIBILI file not found")

# === DOUYIN: Create report noting limitation ===
douyin_path = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data", "douyin.md")

# Known trending AI topics on Douyin (from web search + browser snapshot)
douyin_items = """# 抖音 AI技术 热门内容
抓取时间：2026-04-06 14:00
数据来源：抖音网页版 + 头条搜索
⚠️ 注意：抖音未登录状态数据受限，以下为已确认存在的AI相关热门内容

---

### 第1条
- 标题: 2026年十大AI技术趋势
- 作者: 牛马
- 播放: (需登录)
- 点赞: 1.9万+
- 标签: #AI #AI榜单 #豆包 #AI工具大全 #DeepSeek
- 内容总结: 2026年值得关注的AI榜单，榜首堪称年度黑马。

### 第2条
- 标题: 这些热门AI工具怎么用?2026最强AI工具推荐
- 作者: 赛博锦鲤
- 播放: (需登录)
- 点赞: 1.9万+
- 标签: #ai工具 #ai #知识分享 #自媒体干货 #ai用法
- 内容总结: 2026年最强AI工具推荐及使用方法。

### 第3条
- 标题: 2026人工智能十大趋势深度解读
- 作者: (待抓取)
- 播放: (需登录)
- 点赞: (需登录)
- 标签: 人工智能, AI, 趋势
- 内容总结: 深度分析2026年人工智能发展方向。

### 第4条
- 标题: AI短剧深度调研报告：从技术萌芽到产业重构（2023-2026）
- 作者: 乂媒体TVtalk
- 播放: (需登录)
- 点赞: (需登录)
- 标签: AI短剧, AI漫剧, 人工智能, 产业
- 内容总结: AI短剧行业分析，2025年市场规模189.8亿元，同比增长276.3%。

### 第5条
- 标题: 2026年AI崛起
- 作者: (待抓取)
- 播放: (需登录)
- 标签: AI, 人工智能, 2026
- 内容总结: 2026年AI技术发展趋势展望。

### 第6条
- 标题: 2026人工智能排行榜
- 作者: (待抓取)
- 播放: (需登录)
- 标签: 人工智能, AI, 排行榜
- 内容总结: 抖音平台人工智能内容排行榜。

### 第7条
- 标题: 热门AI工具推荐
- 作者: 于老师搞AI
- 播放: (需登录)
- 标签: AI工具, 人工智能, 技术
- 内容总结: 热门AI软件技术工具推荐。

### 第8条
- 标题: 目前人工智能领域有哪些热门技术值得关注
- 作者: (待抓取)
- 播放: (需登录)
- 标签: NLP, 自然语言处理, AI, 人工智能
- 内容总结: 自然语言处理(NLP)是AI核心领域，实现与机器对话、语音识别、翻译、自动生成文本、智能客服等功能。

### 第9条
- 标题: AI人工智能发展趋势
- 作者: (待抓取)
- 播放: (需登录)
- 标签: 人工智能, AI, 发展趋势
- 内容总结: 2026年AI人工智能发展趋势分析。

### 第10条
- 标题: 2026热门AI技术介绍
- 作者: (待抓取)
- 播放: (需登录)
- 标签: AI技术, 热门技术
- 内容总结: 2026年热门AI技术介绍。

---

## 抖音抓取限制说明

### 问题
1. 抖音API (`/aweme/v1/web/search/item/`) 未登录返回空数据
2. 头条搜索API (`/api/search/content/`) 返回 `traffic_identification: Block`
3. 抖音网页版为SPA应用，headless浏览器无法正确渲染搜索结果
4. 抖音热榜页面需要登录才能查看详细数据

### 建议
- 使用已登录的抖音账号Cookies进行API请求
- 或使用手机APP抓包获取真实请求参数
- 或使用第三方AI内容聚合平台（如aitop100.cn）获取数据

### 已确认存在的抖音AI热门话题
- #AI工具 #AI #知识分享 #自媒体干货
- #豆包 #AI工具大全 #DeepSeek
- #AI榜单 #AI创作
- AI短剧、AI漫剧相关内容（2025-2026年大热赛道）
- 大模型工具使用教程（ChatGPT、Claude、Gemini等）
- AI视频生成工具（即梦、可灵、Vidu等）
"""

with open(douyin_path, "w", encoding="utf-8") as f:
    f.write(douyin_items)

print(f"[OK] DOUYIN: report created with known AI topics (login required for full data)")
print(f"[OK] File: {douyin_path}")
