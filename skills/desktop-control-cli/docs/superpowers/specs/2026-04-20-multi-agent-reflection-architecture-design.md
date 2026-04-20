# 多 Agent 反思架构设计文档

**项目**: desktop-control-cli  
**主题**: 基于 OpenCrew LLM 的多 Agent 反思架构  
**日期**: 2026-04-20  
**版本**: 1.0  
**作者**: AI Assistant

---

## 1. 设计目标

| 问题 | 解决方案 | 预期效果 |
|------|---------|---------|
| 执行速度慢 | 本地模型 + 并行执行 + 批量处理 | **10x** 速度提升 |
| 图像识别偏差 | 专门的视觉 Agent + 位置缓存 | **95%** 准确率 |
| 上下文窗口浪费 | 分层 Agent + MCP 标准化接口 | **80%** Token 节省 |
| 缺乏错误恢复 | 实时反思 + plan-atc 闭环 | **99%** 可靠性 |
| 协作效率低 | MCP 事件驱动 + 主控 Agent 编排 | **3x** 并发能力 |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│          主控 Agent (MasterAgent - OpenCrew LLM)            │
│  - 模型: claude-sonnet-4-6 或 gpt-4-turbo                    │
│  - 职责: 任务分配、编排、状态规划、总结、反思              │
│  - 通过 MCP 调用子 Agent 工具                                 │
│  - 监听 MCP 事件，实时反思                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌───▼────┐
                    │   MCP   │  ← Model Context Protocol
                    │  Server │    （标准化工具接口 + 事件推送）
                    └───┬────┘
                         │
          ┌──────────────┼──────────────┬──────────────┐
          │              │              │              │
┌─────────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐ ┌───▼────────┐
│ 视觉 Agent     │ │ 执行 Agent│ │ 验证 Agent  │ │ 规划 Agent  │
│ (VisionAgent)  │ │(Executor) │ │ (Verifier)  │ │ (Planner)  │
│                │ │           │ │             │ │             │
│ - qwen3-vl:8b  │ │- UFO直接  │ │ - qwen2.5:7b │ │- llama3.1:8b│
│ - 暴露 MCP 工具 │ │- 暴露工具 │ │ - 暴露工具   │ │ - 暴露工具   │
└────────────────┘ └───────────┘ └─────────────┘ └────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   UFO Service        │
              │ (现有底层，无需改动)  │
              └──────────────────────┘
```

### 2.2 模型配置

| Agent | 模型 | 参数量 | 推理速度 | 用途 |
|-------|------|--------|---------|------|
| **主控 Agent** | `opencrew:claude-sonnet-4-6` | - | ~2s | 任务分配、编排、反思 |
| **视觉 Agent** | `ollama:qwen3-vl:8b` | 8B | ~500ms | 图像识别、元素定位 |
| **执行 Agent** | 无（直接调用 UFO） | - | <100ms | UI 操作执行 |
| **验证 Agent** | `ollama:qwen2.5:7b` | 7B | ~100ms | 结果验证、错误检测 |
| **规划 Agent** | `ollama:llama3.1:8b` | 8B | ~200ms | 辅助规划、步骤生成 |

---

## 3. 核心组件设计

### 3.1 主控 Agent (MasterAgent)

**文件**: `app/agents/master_agent.py`

**职责**:
1. **任务分配** - 接收用户请求，分解并分配给子 Agent
2. **任务编排** - 规划执行流程，管理任务依赖
3. **状态规划** - 定义任务状态转换规则
4. **任务总结** - 生成任务完成报告
5. **反思** - 对执行过程进行深度反思（plan-atc 闭环）

**关键方法**:
```python
class MasterAgent:
    async def assign_tasks(self, user_request: dict) -> dict
    async def orchestrate_execution(self, task_assignment: dict) -> dict
    async def plan_state_transitions(self, task: str) -> dict
    async def summarize_completion(self, execution_result: dict) -> dict
    async def reflect_on_execution(self, execution_result, task_summary) -> dict
    async def execute_with_realtime_reflection(self, task: str) -> dict
    async def listen_to_events(self)  # 监听 MCP 事件
```

### 3.2 视觉 Agent (VisionAgent)

**文件**: `app/agents/vision_agent.py`

**职责**:
- 批量识别界面元素（一次调用识别多个目标）
- 位置缓存（常用按钮直接从缓存读取）
- 变化检测（对比截图，检测页面跳转）

**MCP 工具**:
- `vision_agent_identify` - 批量识别界面元素
- `vision_agent_detect_changes` - 对比截图检测变化

**关键方法**:
```python
class VisionAgent:
    async def identify_batch(self, targets: List[str]) -> Dict[str, Position]
    async def identify_single(self, target: str) -> Position
    async def detect_changes(self, before: str, after: str) -> Dict
```

### 3.3 执行 Agent (ExecutorAgent)

**文件**: `app/agents/executor_agent.py`

**职责**:
- 批量执行操作（串行执行依赖操作）
- 并行执行操作（独立操作同时执行）
- 直接调用 UFO Service（无 LLM 开销）

**MCP 工具**:
- `executor_agent_click` - 点击指定位置
- `executor_agent_batch_execute` - 批量执行操作

**关键方法**:
```python
class ExecutorAgent:
    async def batch_execute(self, operations: List[Operation]) -> List[Result]
    async def parallel_execute(self, operations: List[Operation]) -> List[Result]
```

### 3.4 验证 Agent (VerifierAgent)

**文件**: `app/agents/verifier_agent.py`

**职责**:
- 验证执行结果（操作是否成功）
- 检测错误弹窗（权限、网络等）
- 对比前后截图（确认页面跳转）

**MCP 工具**:
- `verifier_agent_verify` - 验证执行结果
- `verifier_agent_detect_errors` - 检测截图中的错误

**关键方法**:
```python
class VerifierAgent:
    async def verify_results(self, results: List[Result]) -> bool
    async def detect_errors(self, screenshot: str) -> List[str]
    async def compare_screenshots(self, before: str, after: str) -> Dict
```

### 3.5 规划 Agent (PlannerAgent)

**文件**: `app/agents/planner_agent.py`

**职责**:
- 生成执行计划（详细步骤）
- 风险评估（可能的问题）
- 备选方案（主方案失败时的 Plan B）

**MCP 工具**:
- `planner_agent_generate_plan` - 生成执行计划

**关键方法**:
```python
class PlannerAgent:
    async def generate_plan(self, task: str, context: Dict) -> List[Operation]
    async def assess_risks(self, plan: List[Operation]) -> List[str]
    async def generate_fallback(self, plan: List[Operation]) -> List[Operation]
```

---

## 4. MCP 中间层设计

### 4.1 MCP 工具定义

**文件**: `app/mcp/tools/agent_tools.py`

**工具列表**:
1. `vision_agent_identify` - 视觉 Agent 批量识别
2. `vision_agent_detect_changes` - 视觉 Agent 变化检测
3. `executor_agent_click` - 执行 Agent 点击
4. `executor_agent_batch_execute` - 执行 Agent 批量执行
5. `verifier_agent_verify` - 验证 Agent 验证结果
6. `verifier_agent_detect_errors` - 验证 Agent 检测错误
7. `planner_agent_generate_plan` - 规划 Agent 生成计划

### 4.2 MCP 事件推送

**文件**: `app/mcp/events/agent_events.py`

**事件列表**:
1. `execution_started` - 执行开始
2. `execution_completed` - 执行完成
3. `execution_failed` - 执行失败（触发反思）
4. `vision_low_confidence` - 视觉识别置信度低
5. `vision_cache_hit` - 视觉缓存命中

---

## 5. plan-atc 闭环设计

### 5.1 闭环流程

```
Plan（计划） → Act（执行） → Check（检查） → Think（反思）
     ↑                                          ↓
     └──────────────── 修正/优化  ───────────────┘
```

### 5.2 实时反思机制

**每完成一个步骤，立即反思**:
1. 分析步骤是否成功
2. 如果不成功，分析根因
3. 判断是否需要调整后续步骤
4. 提供即时改进建议
5. 应用修正方案（如需要）

### 5.3 最终反思

**任务完成后，深度反思**:
1. **plan-atc 闭环分析**
   - Plan（计划）是否合理？
   - Act（执行）是否高效？
   - Check（检查）是否全面？
   - Think（反思）是否到位？

2. **Agent 协作分析**
   - Agent 分配是否合理？
   - Agent 通信是否顺畅？
   - 是否有 Agent 瓶颈？

3. **性能分析**
   - 哪些环节最耗时？
   - 哪些操作可以优化？
   - 是否有资源浪费？

4. **可靠性分析**
   - 错误处理是否充分？
   - 是否有遗漏的边界情况？
   - 错误恢复是否有效？

5. **改进建议**
   - 具体的优化建议
   - 优先级排序
   - 预期改进效果

---

## 6. 数据流设计

### 6.1 主控 Agent 通过 MCP 调用子 Agent

```
1. 主控 Agent 决定需要识别界面元素
   ↓
2. 通过 MCP 调用视觉 Agent 的工具
   mcp.call_tool("vision_agent_identify", {targets: [...]})
   ↓
3. MCP Server 转发给视觉 Agent
   ↓
4. 视觉 Agent 执行（调用 Qwen3-VL-8B）
   ↓
5. 视觉 Agent 通过 MCP 返回结果
   {"发布商品按钮": {"x": 187, "y": 63, "confidence": 0.98}}
   ↓
6. 主控 Agent 接收 MCP 返回的结果
   ↓
7. 主控 Agent 决定下一步操作
```

### 6.2 子 Agent 通过 MCP 推送事件给主控 Agent

```
1. 执行 Agent 执行操作时遇到错误
   ↓
2. 执行 Agent 通过 MCP 推送错误事件
   mcp.push_event("execution_failed", {error: "..."})
   ↓
3. 主控 Agent 接收事件，触发反思
   ↓
4. 主控 Agent 生成修正方案
   ↓
5. 通过 MCP 调用执行 Agent，执行修正方案
```

---

## 7. 错误处理与恢复

### 7.1 错误分类

| 错误类型 | 处理策略 | 最大重试 |
|---------|---------|---------|
| VISION_LOW_CONFIDENCE | 重试+缓存 | 3 次 |
| EXECUTION_CLICK_FAILED | 调整坐标 | 5 次 |
| NETWORK_TIMEOUT | 等待重试 | 2 次 |
| PERMISSION_DENIED | 提示用户 | 0 次 |

### 7.2 错误恢复流程

```
错误检测 → 分类 → 主控 Agent 反思 → 生成修正方案 → 执行恢复
```

---

## 8. 性能优化策略

### 8.1 批量处理

- 视觉 Agent 一次性识别多个元素
- 执行 Agent 批量执行操作

### 8.2 并行执行

- 独立操作同时执行（如多个截图）

### 8.3 智能缓存

- 缓存常用按钮位置（如"发布商品"按钮）
- 缓存识别结果

### 8.4 本地模型优先

- 默认使用本地 Ollama 模型（快速、免费）
- 只有本地模型失败时，才调用云端模型

---

## 9. 实施计划

### Day 1：核心框架搭建

- [ ] 创建主控 Agent 框架（`app/agents/master_agent.py`）
- [ ] 创建 4 个子 Agent 框架
- [ ] 实现 Agent 通信总线（`app/core/agent_communication.py`）
- [ ] 集成 OpenCrew LLM API

### Day 2：视觉与执行 Agent

- [ ] 实现视觉 Agent（批量识别、位置缓存）
- [ ] 实现执行 Agent（批量执行、并行操作）
- [ ] 测试 Qwen3-VL-8B 识别速度和准确率
- [ ] 测试 UFO Service 调用

### Day 3：验证与规划 Agent

- [ ] 实现验证 Agent（错误检测、结果确认）
- [ ] 实现规划 Agent（步骤生成、风险评估）
- [ ] 测试 Qwen2.5-7B 验证速度
- [ ] 测试 Llama 3.1-8B 规划质量

### Day 4：主控 Agent 与反思机制

- [ ] 实现主控 Agent（任务分配、编排）
- [ ] 实现实时反思机制
- [ ] 实现 plan-atc 闭环
- [ ] 集成测试完整流程

### Day 5：优化与测试

- [ ] 性能优化（缓存、批处理、并行）
- [ ] 完整流程测试（京麦上架）
- [ ] 错误恢复测试
- [ ] 文档编写

---

## 10. 预期效果

| 指标 | 当前 | 目标 | 提升 |
|------|------|------|------|
| 单次上架时间 | 3 分钟 | 20 秒 | 10x |
| 视觉识别准确率 | 70% | 95% | 1.4x |
| 并发能力 | 1 个 | 3 个 | 3x |
| 成本 | 高（云端） | 低（本地） | - |

---

## 11. 文件结构

```
desktop-control-cli/
├── app/
│   ├── agents/
│   │   ├── master_agent.py       # 主控 Agent（OpenCrew LLM）
│   │   ├── vision_agent.py       # 视觉 Agent（Qwen3-VL-8B）
│   │   ├── executor_agent.py     # 执行 Agent（无 LLM）
│   │   ├── verifier_agent.py     # 验证 Agent（Qwen2.5-7B）
│   │   └── planner_agent.py      # 规划 Agent（Llama 3.1-8B）
│   │
│   ├── core/
│   │   ├── agent_communication.py   # Agent 通信总线
│   │   ├── task_state_manager.py   # 任务状态管理
│   │   └── reflection_engine.py     # 反思引擎
│   │
│   ├── mcp/
│   │   ├── tools/                   # MCP 工具定义
│   │   │   └── agent_tools.py
│   │   ├── events/                  # MCP 事件定义
│   │   │   └── agent_events.py
│   │   └── server.py                # MCP Server
│   │
│   └── services/
│       ├── ollama_service.py        # Ollama 服务封装
│       └── opencrew_service.py      # OpenCrew 服务封装
│
├── tests/
│   ├── unit/
│   │   ├── test_master_agent.py
│   │   ├── test_vision_agent.py
│   │   ├── test_executor_agent.py
│   │   ├── test_verifier_agent.py
│   │   └── test_planner_agent.py
│   │
│   ├── integration/
│   │   └── test_jingmai_publish.py
│   │
│   └── performance/
│       └── test_performance.py
│
└── cli.py  # 添加 jingmai publish 命令
```

---

## 12. 总结

本设计提出了一个基于 OpenCrew LLM 的多 Agent 反思架构，具有以下特点：

1. **主控 Agent 负责任务分配、编排、反思** - 使用 OpenCrew LLM（Claude Sonnet 4.6 或 GPT-4 Turbo）
2. **4 个子 Agent 负责具体执行** - 使用本地模型（Qwen3-VL-8B、Qwen2.5-7B、Llama 3.1-8B）
3. **MCP 作为中间层** - 提供标准化工具接口和事件推送
4. **plan-atc 闭环** - 完整的反思循环（计划→执行→检查→思考）
5. **实时反思机制** - 每完成一个步骤立即反思，任务完成后深度反思

**预期效果**：
- ✅ 速度提升 10x（3 分钟 → 20 秒）
- ✅ 准确率提升到 95%
- ✅ 支持 3 个并发任务
- ✅ 自动错误恢复
- ✅ 成本降低（本地模型）

---

**文档版本**: 1.0  
**最后更新**: 2026-04-20
