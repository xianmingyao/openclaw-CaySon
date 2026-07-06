#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""添加 GitHub Trending 2026 Week20 到知识库"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from mem0_dual_write import init_mem0, init_milvus, add_memory, get_embedding

# ============ 内容 ============
content_blocks = [
    {
        "text": "GitHub一周热榜Top20 2026年第20周（2026年5月14日整理）来源：抖音@AI爆款/@数智AI日记/小红书JIED喵ai小王。完整榜单：#1 Ruflo 49757 stars多Agent协作开发团队；#2 UI-TARS-desktop 33524 stars字节跳动24小时虚拟助理；#3 PageIndex 30851 stars轻量级RAG不用向量数据库；#4 DeepSeek-TUI 26452 stars DeepSeek终端界面；#5 Anthropic Financial 21515 stars金融Agent；#6 9router 9352 stars字节跳动；#7 CloakBrowser 7863 stars反检测浏览器；#8 Local Deep Research 7373 stars本地深度研究。本周黑马：Obscura Rust无头浏览器21天冲至99k stars内存仅30MB加载85ms超越Chrome6倍。趋势信号：AI Agent团队协作爆发；浏览器自动化两极分化反检测vs轻量高速；字节跳动多点开花；RAG轻量化成刚需；DeepSeek生态持续爆发；本地化AI研究成新热点。",
        "metadata": {"source": "github-trending", "week": 20, "year": 2026}
    },
    {
        "text": "Ruflo GitHub 49757 stars 多Agent协作平台 本周+7088 stars 像一支开发团队分工干活 写代码测Bug写文档全自动化 标签全自动开发团队",
        "metadata": {"source": "github-trending", "project": "Ruflo", "stars": 49757}
    },
    {
        "text": "UI-TARS-desktop GitHub 33524 stars 字节跳动开源 24小时虚拟助理 AI直接看屏幕操作鼠标键盘 打开软件填表单整理文件全自动化 本周+3872 stars",
        "metadata": {"source": "github-trending", "project": "UI-TARS-desktop", "stars": 33524}
    },
    {
        "text": "PageIndex GitHub 30851 stars 本周+4351 stars 轻量级RAG方案 不用向量数据库 靠推理做文档索引 效果一样好部署轻十倍 从背字典变成理解文章",
        "metadata": {"source": "github-trending", "project": "PageIndex", "stars": 30851}
    },
    {
        "text": "Obscura Rust无头浏览器 GitHub 99k stars 21天即将破万 内存仅30MB（Chrome 200MB的15%） 加载仅85ms（Chrome 500ms的17%） AI Native AI Agent原生支持 爬虫圈硅谷刷屏 转发3353大于点赞1312",
        "metadata": {"source": "github-trending", "project": "Obscura", "stars": 9900}
    },
    {
        "text": "CloakBrowser GitHub 7863 stars 本周+5488 stars 反检测浏览器 隐身版Chrome 30项bot检测全部满分 爬虫自动化测试救星 直接替换Playwright",
        "metadata": {"source": "github-trending", "project": "CloakBrowser", "stars": 7863}
    },
    {
        "text": "DeepSeek-TUI GitHub 26452 stars DeepSeek终端用户界面 TUI工具 本周排名第4",
        "metadata": {"source": "github-trending", "project": "DeepSeek-TUI", "stars": 26452}
    },
    {
        "text": "awesome-gpt-image-2 GitHub新仓库 useneospark收集 GPT生成图像高质量提示词 多语言README日语韩语法语西班牙语 有汉化飞书文档",
        "metadata": {"source": "github-trending", "project": "awesome-gpt-image-2", "stars": 24}
    },
]

def main():
    print("=" * 60)
    print("添加 GitHub Trending 2026 Week20 到知识库")
    print("=" * 60)

    # 初始化
    print("\n[初始化] 连接数据库...")
    memory_client = init_mem0()
    milvus_client = init_milvus()
    print("[OK] 初始化成功\n")

    # 逐条添加
    for i, block in enumerate(content_blocks, 1):
        print(f"\n--- [{i}/{len(content_blocks)}] ---")
        add_memory(memory_client, milvus_client, block["text"], block.get("metadata"))

    print("\n" + "=" * 60)
    print(f"[完成] 成功添加 {len(content_blocks)} 条记忆")
    print("=" * 60)

if __name__ == "__main__":
    main()
