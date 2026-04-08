#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传今日研究记忆到云端Milvus
"""
import sys
sys.path.insert(0, 'E:/workspace/scripts')
from mem0_dual_write import init_mem0, init_milvus, add_memory

# 今日研究成果摘要
TODAY_MEMORIES = [
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 AI研究：awesome-design-md项目分析
项目VoltAgent/awesome-design-md，24.4k Stars，58个平台设计系统开源
核心理念：DESIGN.md格式让AI编程工具直接生成像素级UI
格式规范：9大章节（Visual Theme/Color Palette/Typography/Component Stylings/Layout/Depth/Do's/Responsive/Agent Prompt Guide）
与AI-Native SOP结合：阶段5定义DESIGN.md，阶段6 AI编程生成匹配UI
知识库文档：knowledge/awesome-design-md-analysis.md"""
    },
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 Karpathy知识库编译工作流
用LLM把论文/文章/代码编译成wiki知识库
三步曲：收集(raw/) → 编译(LLM) → 查询(直接答)
100篇/40万字规模下不需要RAG，LLM自维护索引
查询结果反哺wiki，知识越滚越大
工具：Obsidian Web Clipper
知识库文档：knowledge/karpathy-wiki-knowledge-base-workflow.md"""
    },
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 LangChain三层学习框架
Agent持续学习三层面：Model层(权重)/Harness层(执行框架)/Context层(运行时配置)
Trace是三层学习的共同原料，可观测性是基础设施
Context层：成本最低/速度最快/见效最快，OpenClaw的Skills就是Context层实现
Harness层：优化执行方式，更新快/粒度细
Model层：影响上限最高，但灾难性遗忘/成本高
神级类比：Model=引擎/Harness=底盘/Context=GPS导航
知识库文档：knowledge/agent-continual-learning-three-layers.md"""
    },
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 AI Agent知识管理统一框架
融合Karpathy工作流 + LangChain三层学习
统一框架：raw→wiki→query→Trace→可观测性→三层学习
Context层Skills = OpenClaw热更新能力，不改模型不改代码直接加Skill变强
Trace记录执行轨迹，是三层学习的共同原料
知识库文档：knowledge/ai-agent-knowledge-management-unified-framework.md"""
    },
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 OpenClaw Context层Skills设计
Skills = Context层可复用组件，包含instructions+tools+memory
Skill结构：name/description/version/instructions/tools/memory/triggers
核心Skill设计：knowledge-collector/wiki-compiler/knowledge-query/coworker
Skill生命周期：创建→安装→触发→执行→学习→优化
Context层 vs Harness层：Context更新快/风险低/粒度细，Harness更新慢/风险高/粒度粗
知识库文档：knowledge/openclaw-context-layer-skills-design.md"""
    },
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 OpenClaw可观测性Trace系统
Trace是三层学习的共同原料：Model层从Trace学模式/Harness层从Trace优化执行/Context层从Trace调整配置
Trace数据结构：event_id/timestamp/session_id/event_type/data
Trace类型：message/tool_call/skill_invoked/memory_update
分析实现：skill_stats/tool_usage/failure_patterns
三层学习实现：Context层自动优化/Harness层改进建议/Model层评估框架
知识库文档：knowledge/openclaw-observability-trace-system.md"""
    },
    {
        "category": "AI_Agent",
        "memory": """2026-04-08 Karpathy工作流OpenClaw实现
目录结构：raw/(原始资料)/wiki/(知识库)/workspace/(代码)
工具实现：Collector收集器/Compiler编译器/Query查询器
Collector：collect_from_url/collect_from_file/collect_github_repo
Compiler：LLM编译raw/生成概念文章和双向链接
Query：小规模(<100篇)直接加载context，大规模向量搜索召回
Skill封装：knowledge-workflow，支持收集/编译/查询三种模式
知识库文档：knowledge/karpathy-wiki-workflow-openclaw-implementation.md"""
    },
    {
        "category": "AI_Weekly",
        "memory": """2026-04-08 AI周报第439期（产品君）
本周主题：开源爆发+语音AI突破
重大新闻：
1.OpenAI内测GPT-Image-2（下一代生图）
2.OpenAI Project Stagecraft（工匠计划）
3.Google Gemma 4（最强开源小模型）
4.Anthropic发现Claude有170种情绪向量
5.阿里Qwen3.5-Omni（最强开源多模态）
6.Sakana AI Marlin（AI战略官）
7.微软MAI-Transcribe-1（最强语音识别）
8.LongCat-AudioDiT（最强声音克隆，开源）
9.OmniVoice（最强语音合成，开源）
10.同事.skill爆火（AI同事）
11.Medvi诞生（首个一人独角兽公司）
开源4个/语音AI 4个/OpenAI 2个/Agent 2个
知识库文档：knowledge/ai-weekly-report-2026-04-05.md"""
    },
    {
        "category": "Summary",
        "memory": """2026-04-08 研究成果总结
四个方向深度研究：
1.AI周报：11条重大新闻，开源+语音AI爆发
2.Context层Skills：OpenClaw热更新核心，Skills=instructions+tools+memory
3.Trace可观测性：三层学习共同原料，记录→分析→学习
4.Karpathy工作流：完整代码实现，Collector+Compiler+Query
四个方向的关联：AI周报(信息源)→Context层Skills(知识管理)→Trace系统(可观测性)→Karpathy工作流(落地实现)→持续学习(三层)
Git提交：4个文件，1740行新增
核心理念：记录Trace→分析Trace→从Trace中学习"""
    }
]

def main():
    print("=" * 60)
    print("上传今日研究记忆到云端")
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
