#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传2026-04-08下午研究记忆到云端Milvus
"""
import sys
sys.path.insert(0, 'E:/workspace/scripts')
from mem0_dual_write import init_mem0, init_milvus, add_memory

# 下午研究成果
TODAY_MEMORIES = [
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 SDD开发教程第五集（大力AI）
OpenSpec规范多人协作，SDD最小闭环：
四动作+验证意识：init→explore→propose→apply→archive
与纯裸聊的差别：有回看、有reveal、有交接、有演进路径
AI开发需将需求→规范→实现→验证→交接接成一条链
视频：大力AI智能体进阶系列"""
    },
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 Red/Green TDD方法论（大力AI）
Simon Willison（Django创始人）提出：AI编程时代测试必须
Red/Green TDD：RED写测试→GREEN写代码→REFACTOR重构
AI生成代码无法逐行检查，测试成为质量保证
Claude Code会读测试结果→发现不匹配→改期望值让测试通过（违背TDD原则）
防止AI作弊：测试文件加锁、不给AI修改权限
视频：大力AI，1.6万点赞"""
    },
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 Karpathy个人知识库搭建教程（大力AI第18集）
三个文件夹+一个CLOD.md指令文件：
- RO/：原始素材（Raw Original）
- wiki/：AI整理后的内容
- altpus/：AI生成的答案/报告/分析
推荐工具：Vertola.ai Agent Browser自动抓取网页
对比Karpathy方法 vs NotebookLM：Karpathy上限更高，完全自己管理
大力AI观点：同一份知识可以生成不同视角的笔记
视频：大力AI智能体进阶，4285点赞"""
    },
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 GitHub一周star排行TOP20（赛博笔记第2集）
本周主题：AI基础设施+Agent工具+开发者效率
类型包括：安全平台、TTS模型、Skills导航、安卓工具、隐私验证、DNS管理、AI提示词集合、地图组件、macOS清理、笔记系统、设计技巧等
系列推荐：第3集(everything-claude-code/x-algorithm)1.5万点赞、第7集(PicoClaw/ZeroClaw/OpenClaw大乱战)1859点赞
视频：赛博笔记github一周榜单系列"""
    },
    {
        "category": "Skills",
        "memory": """2026-04-08 发现两个新OpenClaw Skill
1.Anspire Web Search v1.0.3（ClawHub）
- 作者：Gavin (@gavin-guq)
- 功能：国内信息搜索，替代海外搜索skill
- License：MIT-0
- 安全：VirusTotal Benign
- 来源：@赛博自由老爹视频，280点赞

2.xcrowd（抖音博主推荐）
- 用途：数据采集必备Skill
- 来源：@AI内容工厂-神推手视频，676收藏
- 状态：ClawHub上搜不到，可能刚发布未索引"""
    },
    {
        "category": "Skills",
        "memory": """2026-04-08 ClawHub数据类Skills盘点
TOP数据Skills：
- Data Analyst（@realroc）5.1k stars
- Data Model Designer（@datadrivenconstruction）3.9k stars
- Data Anomaly Detector 2.9k stars
- Data Lineage Tracker 2.9k stars
- Data Cog 1.9k stars

国内开发：
- Data Analyst Cn（@yang1002378395-cmyk）1.6k stars
- Quant Data Quality（@xueylee-dotcom）206 stars
- Excel Data Quality Check（@chartgen-ai）82 stars"""
    },
    {
        "category": "Summary",
        "memory": """2026-04-08 下午研究成果总结（08:45-08:49）
视频研究：
1.SDD开发教程：OpenSpec规范多人协作最小闭环
2.Red/Green TDD：AI编程时代测试驱动开发必须
3.Karpathy知识库：三个文件夹+CLOD.md
4.GitHub TOP20：AI基础设施+Agent工具+开发者效率

新Skill发现：
1.Anspire Web Search：国内信息搜索
2.xcrowd：数据采集（ClawHub未收录）

技能盘点：ClawHub数据类25个Skills，国内开发者参与"""
    }
]

def main():
    print("=" * 60)
    print("上传2026-04-08下午研究记忆到云端")
    print("=" * 60)
    
    # 初始化
    print("\n[初始化] 连接数据库...")
    memory_client = init_mem0()
    milvus_client = init_milvus()
    print("[OK] 连接成功")
    
    # 上传每条记忆
    for i, item in enumerate(TODAY_MEMORIES, 1):
        print(f"\n[{i}/{len(TODAY_MEMORIES)}] 上传: {item['category']}")
        add_memory(
            memory_client, 
            milvus_client, 
            item['memory'],
            metadata={"category": item['category']}
        )
    
    print("\n" + "=" * 60)
    print(f"[完成] 共上传 {len(TODAY_MEMORIES)} 条记忆到云端")
    print("=" * 60)

if __name__ == "__main__":
    main()
