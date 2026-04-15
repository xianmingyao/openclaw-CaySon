"""
上传今日学习内容到Milvus云端
"""
import sys
sys.path.insert(0, 'E:/workspace/scripts')

from mem0_dual_write import init_mem0, init_milvus, add_memory

memory_client = init_mem0()
milvus_client = init_milvus()

# 今日学习内容
memories = [
    "2026-04-15 技术热点：web-access skill安装，支持CDP Proxy联网增强",
    "OPC CLI开源项目：xiaotianfotos/OPC，TTS/ASR/剪口播/特效字幕，本地多模态模型能力",
    "fireworks-tech-graph：Claude Code Skill，中文描述生成SVG+PNG架构图，2.4k Stars，7种风格14种UML图",
    "PRD-Writer Skill：PRD写作+原型生成，两步写作法+三视角诊断+五大盲区补全",
    "OpenClaw vs Hermes对比五维度：工程重心/Skill/记忆/安全/场景，OpenClaw管入口秩序，Hermes管执行经验",
    "AI周报第439集4月12日：Claude Mythos、Claude Managed Agents、GLM-5.1、HappyHorse-1.0、ACE-Step-1.5-xl、Vanast",
    "Hermes行为准则升级：Skill自动沉淀机制，目录结构knowledge/skills/shared/ningsk/anti-patterns",
    "clawflows：OpenClaw Superpowers，1.5k Stars，强大预建Agent工作流"
]

print(f"开始上传 {len(memories)} 条记忆到Milvus...")

for i, text in enumerate(memories, 1):
    result = add_memory(memory_client, milvus_client, text)
    print(f"{i}. ✅ {result}")

print(f"\n✅ 成功上传 {len(memories)} 条记忆到云端Milvus！")
