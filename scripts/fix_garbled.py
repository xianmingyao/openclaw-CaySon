# -*- coding: utf-8 -*-
"""修复知识库文件中的乱码"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = 'E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到乱码的位置
garbled_marker = '## 🕳️ 避坑指南'

if garbled_marker in content:
    idx = content.find(garbled_marker)
    print(f"Found marker at position {idx}")
    
    # 找到标记前的内容
    before = content[:idx]
    
    # 新的避坑指南内容（正确的）
    after = """*新增章节：2026-05-12（来源：抖音第67集）*

---

## 🕳️ 避坑指南

### 坑1：把本体做成数据仓库
> "知识库只能做资料查询，企业本体要做业务推理，Agent做动作执行。知识库解决的是信息不对称，本体解决的是业务语义统一。"

### 本体 vs 知识库：核心区别

| 对比项 | 仅有知识库 | 有本体 | 有Agent |
|--------|-----------|--------|---------|
| 坑1 | 经营分析靠人工 | AI能推理 | AI能执行+追踪 |
| 坑2 | 数据孤岛难打通 | 本体统一语义 | Agent自动执行 |
| 坑3 | 规则散落各处 | 本体沉淀规则 | Agent按规则执行 |

### 落地路径选择
```
阶段一：没有系统  →  阶段二：已有多个系统  →  阶段三：已有数仓/中台/BI
目标：数字化       →  目标：打破孤岛建本体  →  目标：语义化
Excel/手工          CRM/ERP/OA连接          现有数据→业务逻辑
```

### 技术栈全景图
```
Agent应用层：Dify / Coze / LangChain / LangGraph
推理调度层：大模型(LLM) + 提示词工程
本体层：Neo4j / NebulaGraph / TuGraph
数据治理层：ETL/ELT / 主数据管理(MDM)
底层数字化：协同办公(飞书/钉钉) / 业务系统 / 云服务器
```

### 底层能力总结
```
知识库(静) → 本体(动) → Agent(行)
 查资料     懂业务     能干活
```

*最后更新：2026-05-12（新增第67集7层架构内容）*
"""
    
    # 重建文件
    new_content = before + after
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"[OK] Fixed! New length: {len(new_content)} chars")
else:
    print("[WARN] Marker not found")
