# OpenClaw 可观测性 & Trace 系统：基于 LangChain 三层学习

> 研究日期：2026-04-08
> 理论支撑：LangChain 三层学习框架 + Karpathy 知识库工作流

---

## 1. 🎯 核心理念

### Trace 是三层学习的共同原料

```
Trace（执行轨迹）
    ↓
┌─────────────┐
│ Model 层    │ → 从 Trace 学习模式，更新权重
├─────────────┤
│ Harness 层  │ → 从 Trace 优化执行方式
├─────────────┤
│ Context 层  │ → 从 Trace 调整运行时配置
└─────────────┘
```

**可观测性 = 基础设施**

---

## 2. 📊 OpenClaw Trace 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     OpenClaw Agent                              │
│                                                                 │
│  ┌─────────────┐                                               │
│  │   User      │  ←→  Message                                  │
│  └─────────────┘                                               │
│         ↓                                                      │
│  ┌─────────────┐                                               │
│  │  Context    │ ←→ Skills + Memory                           │
│  └─────────────┘                                               │
│         ↓                                                      │
│  ┌─────────────┐                                               │
│  │  Harness    │ ←→ Prompt + Tools + Workflow                 │
│  └─────────────┘                                               │
│         ↓                                                      │
│  ┌─────────────┐                                               │
│  │   Model     │ ←→ LLM API                                   │
│  └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Trace Collector                             │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Message │  │   Tool   │  │  Memory  │  │   Skill  │      │
│  │   Log    │  │   Log    │  │   Log    │  │   Log    │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Trace Storage                               │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│  │  SQLite  │  │  LanceDB │  │  Milvus   │                    │
│  │ (本地)   │  │ (向量)   │  │ (云端)   │                    │
│  └──────────┘  └──────────┘  └──────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Analysis & Learning                          │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│  │  Model    │  │ Harness  │  │ Context   │                   │
│  │  Layer    │  │  Layer   │  │   Layer   │                   │
│  └──────────┘  └──────────┘  └──────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 📝 Trace 日志结构

### 3.1 基础 Trace Event

```json
{
  "event_id": "uuid",
  "timestamp": "2026-04-08T08:00:00Z",
  "session_id": "session-uuid",
  "event_type": "message|tool_call|memory_update|skill_invoked",
  "data": {
    "content": "...",
    "role": "user|assistant|system",
    "metadata": {}
  }
}
```

### 3.2 Tool Call Trace

```json
{
  "event_id": "uuid",
  "event_type": "tool_call",
  "timestamp": "2026-04-08T08:00:00Z",
  "data": {
    "tool_name": "file-read",
    "tool_input": {
      "path": "E:/workspace/test.md"
    },
    "tool_output": {
      "content": "..."
    },
    "duration_ms": 150,
    "success": true,
    "error": null
  }
}
```

### 3.3 Skill Invocation Trace

```json
{
  "event_id": "uuid",
  "event_type": "skill_invoked",
  "timestamp": "2026-04-08T08:00:00Z",
  "data": {
    "skill_name": "wiki-compiler",
    "trigger": "编译知识库",
    "instructions_used": ["..."],
    "tools_used": ["file-read", "file-write"],
    "duration_ms": 5000,
    "success": true,
    "output_summary": "编译完成，生成了 10 个概念"
  }
}
```

### 3.4 Memory Update Trace

```json
{
  "event_id": "uuid",
  "event_type": "memory_update",
  "timestamp": "2026-04-08T08:00:00Z",
  "data": {
    "memory_type": "vector|file|structured",
    "operation": "create|update|delete|search",
    "content": "...",
    "embedding": [...],
    "success": true
  }
}
```

---

## 4. 🔧 Trace 收集实现

### 4.1 Python 实现示例

```python
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Any

class TraceCollector:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traces (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)
        self.conn.commit()
    
    def log_event(
        self,
        session_id: str,
        event_type: str,
        data: dict
    ):
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO traces (event_id, timestamp, session_id, event_type, data)
            VALUES (?, ?, ?, ?, ?)
        """, (event_id, timestamp, session_id, event_type, json.dumps(data)))
        self.conn.commit()
        
        return event_id
    
    def log_tool_call(
        self,
        session_id: str,
        tool_name: str,
        tool_input: dict,
        tool_output: Any,
        duration_ms: int
    ):
        return self.log_event(session_id, "tool_call", {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_output": str(tool_output)[:1000],  # 截断
            "duration_ms": duration_ms,
            "success": True
        })
    
    def log_skill_invoked(
        self,
        session_id: str,
        skill_name: str,
        trigger: str,
        instructions: list,
        tools_used: list,
        duration_ms: int,
        output_summary: str
    ):
        return self.log_event(session_id, "skill_invoked", {
            "skill_name": skill_name,
            "trigger": trigger,
            "instructions_used": instructions,
            "tools_used": tools_used,
            "duration_ms": duration_ms,
            "success": True,
            "output_summary": output_summary
        })
```

---

## 5. 📊 Trace 分析实现

### 5.1 使用分析

```python
class TraceAnalyzer:
    def __init__(self, collector: TraceCollector):
        self.collector = collector
    
    def get_skill_stats(self, skill_name: str) -> dict:
        """获取 Skill 使用统计"""
        cursor = self.collector.conn.cursor()
        cursor.execute("""
            SELECT data FROM traces
            WHERE event_type = 'skill_invoked'
            AND data LIKE ?
        """, (f'%{skill_name}%',))
        
        results = cursor.fetchall()
        total = len(results)
        
        if total == 0:
            return {"total_invocations": 0}
        
        # 解析数据
        total_duration = 0
        success_count = 0
        for row in results:
            data = json.loads(row[0])
            total_duration += data.get("duration_ms", 0)
            if data.get("success"):
                success_count += 1
        
        return {
            "total_invocations": total,
            "success_rate": success_count / total,
            "avg_duration_ms": total_duration / total
        }
    
    def get_tool_usage(self) -> dict:
        """获取工具使用统计"""
        cursor = self.collector.conn.cursor()
        cursor.execute("""
            SELECT data FROM traces
            WHERE event_type = 'tool_call'
        """)
        
        tool_counts = {}
        for row in cursor.fetchall():
            data = json.loads(row[0])
            tool_name = data.get("tool_name", "unknown")
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        
        return tool_counts
    
    def get_failure_patterns(self) -> list:
        """分析失败模式"""
        cursor = self.collector.conn.cursor()
        cursor.execute("""
            SELECT data FROM traces
            WHERE event_type = 'tool_call'
            AND data LIKE '%"success": false%'
        """)
        
        failures = []
        for row in cursor.fetchall():
            data = json.loads(row[0])
            failures.append({
                "tool": data.get("tool_name"),
                "error": data.get("error")
            })
        
        return failures
```

---

## 6. 🔄 三层学习实现

### 6.1 Context 层学习

```python
def context_layer_learning(analyzer: TraceAnalyzer):
    """
    Context 层学习：根据 Trace 调整运行时配置
    """
    # 1. 分析成功案例
    successful_skills = analyzer.get_successful_skill_patterns()
    
    # 2. 调整 Skill 触发条件
    for skill, patterns in successful_skills.items():
        current_skill = load_skill(skill)
        # 如果某些触发词效果好，增加权重
        for pattern in patterns:
            current_skill.add_trigger(pattern, weight=1.5)
        save_skill(current_skill)
    
    # 3. 优化 Memory 策略
    memory_effectiveness = analyzer.get_memory_effectiveness()
    for memory_type, score in memory_effectiveness.items():
        if score < 0.7:
            # 调整 memory 配置
            adjust_memory_config(memory_type, {"retention": "aggressive"})
```

### 6.2 Harness 层学习

```python
def harness_layer_learning(analyzer: TraceAnalyzer):
    """
    Harness 层学习：根据 Trace 优化执行框架
    """
    # 1. 分析工具调用模式
    tool_patterns = analyzer.get_tool_call_patterns()
    
    # 2. 优化工具调用链
    for pattern in tool_patterns:
        if pattern.frequency > 100 and pattern.success_rate < 0.9:
            # 重试机制
            add_retry_logic(pattern.tool_name, max_retries=3)
        
        if pattern.avg_duration > 5000:
            # 异步化
            make_async(pattern.tool_name)
    
    # 3. 优化 Prompt
    low_quality_outputs = analyzer.get_low_quality_outputs()
    for output in low_quality_outputs:
        improve_prompt_for_context(output.context)
```

### 6.3 Model 层学习（未来方向）

```python
def model_layer_learning(analyzer: TraceAnalyzer):
    """
    Model 层学习：考虑微调（未来方向）
    
    注意：Model 层成本高、风险大，需谨慎
    """
    # 1. 收集高质量样本
    good_examples = analyzer.get_good_examples()
    
    # 2. 评估是否值得微调
    if len(good_examples) > 1000:
        # 准备微调数据集
        dataset = prepare_finetune_dataset(good_examples)
        # 评估微调成本和收益
        estimate = estimate_finetune_cost(dataset)
        if estimate.benefit > estimate.cost * 2:
            # 触发微调流程
            trigger_finetune(dataset)
```

---

## 7. 📊 可视化 Dashboard

### 7.1 关键指标

| 指标 | 说明 | 三层对应 |
|------|------|---------|
| Skill 使用率 | 哪些 Skill 被频繁使用 | Context |
| 工具调用成功率 | 工具是否正常工作 | Harness |
| 平均响应时间 | 系统性能 | Model |
| 失败模式 | 问题定位 | 三层通用 |
| Token 消耗 | 成本控制 | Model |

### 7.2 Dashboard 布局

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Trace Dashboard                 │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│   Today    │   7 Days   │   30 Days  │   All Time     │
├─────────────┴─────────────┴─────────────┴─────────────────┤
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐ │
│  │ Skill 使用排行  │  │ 工具调用成功率 │  │ 平均响应时间   │ │
│  │               │  │               │  │               │ │
│  │ 1. wiki-comp │  │   98.5%       │  │   1.2s        │ │
│  │ 2. coworker  │  │   ↑ 0.3%      │  │   ↓ 0.1s      │ │
│  │ 3. code-rev  │  │               │  │               │ │
│  └───────────────┘  └───────────────┘  └───────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              失败模式分析                              │  │
│  │                                                     │  │
│  │  file-read: 12%   →  优化路径处理                   │  │
│  │  web-fetch: 5%   →  增加重试                        │  │
│  │  exec: 8%        →  超时处理                         │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Token 消耗趋势                           │  │
│  │                                                     │  │
│  │  ▁▂▃▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█                        │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. 🛠️ 实施路径

### Phase 1: 基础追踪（1-2 周）

- [ ] Trace 数据模型设计
- [ ] SQLite 本地存储
- [ ] 基础日志 API
- [ ] 简单 Dashboard

### Phase 2: 分析能力（2-3 周）

- [ ] 统计分析模块
- [ ] 模式识别
- [ ] 失败告警
- [ ] 性能监控

### Phase 3: 学习优化（3-4 周）

- [ ] Context 层自动优化
- [ ] Harness 层改进建议
- [ ] Model 层评估框架
- [ ] 自动化调优

---

## 9. 📊 总结

| 维度 | 评分 |
|------|------|
| 技术完整性 | ⭐⭐⭐⭐ |
| 可实施性 | ⭐⭐⭐ |
| 学习价值 | ⭐⭐⭐⭐⭐ |

### 一句话总结
> **Trace 是三层学习的共同原料，可观测性是 Agent 进化的基础设施。记录 Trace，分析 Trace，从 Trace 中学习。**

### 行动清单

- [ ] 设计 Trace 数据模型
- [ ] 实现 TraceCollector
- [ ] 开发 TraceAnalyzer
- [ ] 构建 Dashboard
- [ ] 实现 Context 层自动优化
- [ ] 设计 Harness 层改进建议
