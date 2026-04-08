#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传2026-04-08下午Skills安装记忆到云端Milvus
"""
import sys
sys.path.insert(0, 'E:/workspace/scripts')
from mem0_dual_write import init_mem0, init_milvus, add_memory

# Skills安装研究成果
TODAY_MEMORIES = [
    {
        "category": "Skills_Installed",
        "memory": """2026-04-08 Skills安装记录（AI干货局6个必备Skill）
已安装4个：
1.react-best-practices：Vercel官方React性能优化，57条规则，3.6k stars
2.remotion-video-toolkit：Remotion视频框架最佳实践，16k stars，动画/字幕/图表
3.superdesign：专家级前端设计指南，28.2k stars，beautiful modern UIs
4.mobile：移动端应用开发，1.6k stars，lifecycle/offline/platform conventions

未安装（ClawHub限流）：
5.azure-ai：Azure AI服务集成（未找到对应Skill）
6.frontend-design-pro：前端设计规范中文版（限流）

当前已安装Skills共9个：agent-reach/anspire-web-search/mobile/react-best-practices/remotion-video-toolkit/superdesign/windows-control/frontend-design/ui-design"""
    },
    {
        "category": "Skills_Installed",
        "memory": """2026-04-08 今日抖音研究Skills清单
AI干货局6个必备Skill：
- React性能优化（react-best-practices）✅
- Web设计规范自动审查（待查）
- 前端设计指南（Anthropic出品）
- Remotion视频框架最佳实践（remotion-video-toolkit）✅
- Azure AI服务集成（待查）
- 移动端UI生成（mobile）✅

AI内容工厂6个邪修Skill：
- 社区（需求对齐）
- Canva design（商业信息图）
- Front end design（superdesign）✅
- Docx（Word处理）
- XLSX（Excel处理）
- Humanizer（去AI味）

Agent-Reach（16.3k stars）：
- 已从v1.1.0升级到v1.4.0
- 支持17个平台：网页/YouTube/RSS/全网搜索/GitHub/Twitter/小红书/抖音/Reddit/LinkedIn/微信公众号/微博/V2EX/雪球/小宇宙播客
- 完全免费，MIT License"""
    }
]

def main():
    print("=" * 60)
    print("上传2026-04-08 Skills安装记忆到云端")
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
