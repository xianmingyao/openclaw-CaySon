# CodeX 进阶教程：当模型变强，开发流程该怎么重做？

**来源**: https://v.douyin.com/duK_R8ZHcs4/
**原视频ID**: 7650213306375933184
**博主**: 废才俱乐部Club（小红书/抖音/B站/YouTube 同名，主打"每一期一个干货 AI 教程"）
**视频发布日期**: 2026-06-12（已 4.8 万点赞）
**宁兄分享日**: 2026-06-25
**音频**: 已下载至 `E:\workspace\skills\douyin-transcribe-skill\temp\audio_codex_advanced.mp3`（~16MB，约 40 分钟）
**完整逐字稿**: ⚠️ 待 Groq API Key 配齐后补（见底部「待补」）

---

## 1. 🎯 这是什么

废才俱乐部Club 在 **Claude Fable 5（2026-06-09 发布）+ GPT-5.5 + Claude Opus 4.8** 集体冲破能力边界的当口，提出了一个尖锐问题：

> **当大模型已经足够自主时，AI 开发的 Harness（驾驭系统） 也该从"写详细步骤"转向"设目标、写循环"。**

这是把 **Prompt → Context → Harness → Loop** 四阶段演进往前推一步 —— **不是 Harness 升级到 Loop，而是 Harness 本身要变形**：从"步骤级说明书"变成"目标级 + 循环级"两件套。

---

## 2. 📝 关键功能点

### 2.1 视频核心论点（一句话拆解）

```
原标题解构：
"Fable 5 已经上线，GPT-5.5 和 Opus 4.8 也在逼近新的能力边界，
 接下来 GPT-5.6 可能还会继续爆发；
 当大模型已经足够自主时，AI 开发的 Harness 也该从'写详细步骤'
 转向'设目标、写循环'"
```

**三层意思**：
1. **模型现状**：Fable 5 / GPT-5.5 / Opus 4.8 已逼近自主智能
2. **未来预判**：GPT-5.6 可能继续爆发
3. **方法论升级**：Harness 从"步骤"转向"目标 + 循环"

### 2.2 "设目标、写循环" —— Harness 2.0 范式

| 旧 Harness（步骤级） | 新 Harness（目标 + 循环级） |
|--------------------|---------------------------|
| 给 AI 写详细步骤："先读这个文件，然后改这一行，再跑这个测试" | 给 AI 设目标 + 循环："目标 = 这个 bug 修好；循环 = 自己读代码 → 改 → 测 → 不通过就再读再改" |
| 人是"工头"，盯每一步 | 人是"产品经理"，盯结果 |
| 步骤固定，模型自主性低 | 目标固定，路径由模型自由探索 |
| 改动 = 改 prompt | 改动 = 改目标函数 / 改终止条件 |
| 失败 = 步骤错了 | 失败 = 目标定义错了 / 循环跑飞了 |

### 2.3 三款关键模型当前能力定位

| 模型 | 发布 | 定位 | 关键能力 |
|------|------|------|---------|
| **Claude Fable 5** | 2026-06-09 | 首个公众可用 Mythos 级模型 | 长程、复杂任务，几乎所有基准 SOTA |
| **Claude Opus 4.8** | 2026-05 底 | 补齐短板（非架构大改） | SWE-Bench Pro +5%，新增 Dynamic Workflows（并行数百子 Agent） |
| **GPT-5.5** | 持续迭代 | OpenAI 主力旗舰 | 持续逼近 SOTA |
| **GPT-5.6**（预测） | 未来几周 | 下一代 | 内测中，下周上线 |

### 2.4 Codex 在新范式中的角色

**Codex** 不是被替换，而是被"用对地方"：
- **适合**：Codex 当"目标执行器" —— 在 Loop 中被反复调用
- **不适合**：把 Codex 当万能"步骤生成器"（传统 Prompt 思维）

**Codex 2026 新能力（来自菜鸟教程/B站相关教程）**：
- 一键迁移配置
- 全自动开发
- 电脑远程操控
- 看屏幕 + 操作 Figma
- 跨周跨月长任务
- 虚拟鼠键操作

---

## 3. ⚡ 怎么使用（参考实现）

### 3.1 Harness 2.0 模板（"设目标 + 写循环"）

```yaml
# 旧 Harness（步骤级）—— 失败模式
harness_v1:
  steps:
    - 读取订单数据
    - 检查库存
    - 生成发货单
    - 调用物流 API
    - 发通知
# 痛点：任一步出错整个流程挂；改业务要改 N 行 prompt
```

```yaml
# 新 Harness（目标 + 循环级）
harness_v2:
  goal: |
    用户下单后，确保订单完整履约（库存检查 → 发货 → 通知 → 异常处理）。
    完成 = 用户收到货且物流单号回写到订单系统。
  tools:
    - 订单查询
    - 库存查询
    - 物流 API
    - 飞书通知
  loop:
    max_iterations: 20
    exit_condition: "目标完成 OR 异常无法恢复"
    verification: "回查订单系统状态字段"
  guardrails:
    - 单次循环成本上限（避免跑飞烧 Token）
    - 同类异常连续 3 次自动升级给人
    - 涉及金钱的操作必须人工 ack
```

### 3.2 Codex 集成进 Loop 的典型模式

```python
# Loop 主循环 + Codex 作为"重型决策器"
import subprocess
from agnes_client import AgnesClient  # 或者 Claude/GPT-5.5

def loop(task: str, agnes: AgnesClient, codex_cli: str):
    """外循环：AI 自己跑，自己停"""
    state = {"iter": 0, "history": [], "failed": False}
    
    while state["iter"] < 20:
        # 1. 轻量级 LLM 决策：要不要调 Codex？
        decision = agnes.chat(
            model="Agnes-2.0-Flash",
            messages=[{
                "role": "system",
                "content": f"目标：{task}\n历史：{state['history'][-3:]}\n现在应该？"
            }],
            tools=[run_codex, finish, ask_human]
        )
        
        # 2. 根据决策执行
        if decision.tool == "run_codex":
            result = subprocess.run([codex_cli, decision.args], 
                                  capture_output=True, timeout=300)
            state["history"].append({"role": "codex", "content": result.stdout})
        
        elif decision.tool == "finish":
            if verify(task, state):
                return state  # 完成！
            else:
                state["history"].append({"role": "system", "content": "未通过验证，继续"})
        
        elif decision.tool == "ask_human":
            notify_human(decision.question)
            return state  # 异常升级
        
        state["iter"] += 1
    
    return state  # 超时
```

---

## 4. ✅ 优点

| 维度 | 评价 |
|------|------|
| **立意高** | 把"Harness 升级"和"模型进化"对齐，看到范式转折点 |
| **可执行** | 不是空谈，而是给出"设目标 + 写循环"的具体模板 |
| **时机准** | 卡在 Claude Fable 5 上线、Opus 4.8 发布、GPT-5.6 内测的当口 |
| **串联强** | 与江哥 Harness / AI有点聊 Loop Engineering 形成完整演进链 |
| **门槛低** | 普通开发者跟着改 YAML 就能落地，不是必须精通 LangGraph |

---

## 5. ❌ 缺点 / 待验证

| 维度 | 评价 |
|------|------|
| **缺少具体代码** | 标题党"教程"，但发布日是 2026-06-12，标题只有论点，没有代码仓库 |
| **没有对比实验** | "设目标" vs "写步骤"的实际效果差异，未见量化数据 |
| **博主内容风格** | 标题长、口号多、落地少 —— "废才俱乐部"的废才感有点过 |
| **完整逐字稿缺失** | Groq API Key 未配齐，本次归档转录待补 |
| **可能与其他博主内容重叠** | Harness 概念江哥讲过（06-16），Loop Engineering AI有点聊讲过（06-23），本视频是"组合升级版" |

---

## 6. 🎬 使用场景

### 6.1 适合谁

- **AI 工程团队 Lead**：思考团队工作流要不要重做
- **资深独立开发者**：单兵作战，想让 AI Agent 自己跑 1-2 周的大任务
- **Agent 产品经理**：设计新一代 Agent 产品的范式
- **跨境电商 / 自动化运维**：业务多变，频繁改 prompt 不如改目标函数

### 6.2 不适合谁

- **完全没碰过 AI 编程的人**：先学基础 Prompt / Codex 入门
- **业务流程极其稳定的团队**：写步骤反而更高效
- **对成本敏感 + Loop 不收敛**：每步烧 Token 比写步骤贵

---

## 7. 🔧 运行依赖环境

| 依赖 | 必须？ | 说明 |
|------|-------|------|
| Claude Fable 5 / GPT-5.5 / Opus 4.8 之一 | 推荐 | "足够自主"的模型 |
| Codex / Claude Code CLI | ✅ | 目标执行器 |
| Loop 调度机制 | ✅ | APScheduler / asyncio / LangGraph |
| 状态持久化 | ✅ | JSON / SQLite / Redis |
| Token 预算监控 | 推荐 | 避免 Loop 跑飞烧光预算 |
| 人工升级渠道 | 推荐 | 飞书 / 微信 / 邮件 |
| Groq API Key | 选 | 本归档转录需要 |

---

## 8. 🚀 部署使用注意点

### 8.1 Harness 升级踩坑

1. **目标不能太虚** —— "把项目做好"不是目标；"X 个 bug 全部关闭 + Y 个功能上线"才是
2. **终止条件必须可验证** —— 用代码能检查的事实，不用 AI 主观判断
3. **工具列表要稳定** —— 频繁换工具 = Loop 跑飞的最大来源
4. **升级降级并存** —— 老 Harness 不要一下子全废，新场景用新范式

### 8.2 Loop 调 Codex 的成本控制

- Codex 调用一次 ≈ 几十秒 + 几块钱 Token
- Loop 跑 20 步可能 = 几百块 Token
- 必须加：单次循环成本上限 + 总预算上限 + 异常熔断

### 8.3 模型选择决策树

```
任务复杂度？
├─ 简单 CRUD/重构 → Codex + Sonnet 4（便宜）
├─ 中等业务逻辑 → Codex + Opus 4.8（平衡）
├─ 复杂长程任务 → Codex + Claude Fable 5（最贵最猛）
└─ Loop 调度器本身 → Agnes-2.0-Flash（0 Token）
```

---

## 9. 🕳️ 避坑指南

🔴 **坑 1：以为换了 Harness 2.0 就万事大吉**
现实：模型不够强时，新 Harness 会更乱（目标模糊 → Loop 跑飞 → 烧 Token）。**先把模型升到位**，再升级 Harness。

🔴 **坑 2：把"设目标"当甩锅**
现实："AI 自己看着办"不是设目标。目标必须有**验收标准**——可机器验证的状态字段、可量化的指标、可对比的事实。

🟡 **坑 3：Loop 无限跑**
现实：20 步限制只是兜底。更深层问题是**没找到真正的目标分解**。要么目标太大，要么工具不够，要么验证机制太松。

🟡 **坑 4：把所有任务都塞进 Loop**
现实：Loop 适合"持续盯一个目标"，不适合"一次性复杂任务"。一次性任务用 ReAct 单次调用就够了。

🟢 **坑 5：忽视人工升级**
现实：再强模型也有幻觉，关键决策必须能"踢回给人"。Loop 必须有 `ask_human` 这个 tool，而不是闷头跑。

---

## 10. 📊 总结

### 一句话概括
**"模型够强 → Harness 升级：别再写步骤，写目标 + 写循环"** —— Claude Fable 5 + Opus 4.8 + GPT-5.5 的能力，让"AI 自己跑循环完成复杂目标"从理论变成 2026 年的工程现实。

### 学习价值：⭐⭐⭐⭐（4星）
- 把"模型进化"和"Harness 演进"对齐思考
- 提出具体可执行的"设目标 + 写循环"模板
- 卡在三大模型集体爆发的当口，立意有前瞻性

### 推荐指数：⭐⭐⭐⭐（4星）
- 立意好但落地少（标题党，缺代码）
- 与已有知识（江哥 Harness + AI有点聊 Loop）有重叠
- 适合"已经懂基础 Harness 的人"看，不适合入门

### 与宁兄已有知识串联

#### 演进链路
```
2026-06-16  Harness 工程基础（江哥第88集）—— 步骤级
     ↓
2026-06-23  Loop Engineering（AI有点聊）—— 循环级
     ↓
2026-06-25  Loop + Agnes（第四种黑猩猩）—— 循环级 + 0 Token 工具  ← 上午视频
     ↓
2026-06-25  Harness 2.0（废才俱乐部Club）—— 目标 + 循环级组合 ← 本视频
```

#### 知识图谱新增节点
- **Claude Fable 5**（2026-06-09 发布，Mythos 级）
- **Claude Opus 4.8**（2026-05 底，Dynamic Workflows）
- **GPT-5.5 / GPT-5.6**（持续迭代）
- **Codex 2026 新能力**（一键迁移、远程操控、Figma 操作）

#### ELUCKY 场景应用建议
- **目标函数化**：京麦商品发布 SOP → "目标 = 5 步全部完成且图片合规" 的可验证 Loop
- **Codex 当执行器**：跨境电商多平台同步发布，让 Codex 在 Loop 中被反复调用
- **Harness 渐进升级**：不要全盘重写，新业务先试 Harness 2.0，跑通了再迁移老业务

### 待补清单

- [ ] **完整逐字稿** —— 40 分钟长视频，待 Groq API Key 配齐后转录（已下载音频 ~16MB）
- [ ] **博主代码仓库** —— 视频中提到的 YAML 模板/示例代码，评论区找链接
- [ ] **Claude Fable 5 定价详情** —— Mythos 级模型可能很贵，待核实
- [ ] **"设目标 + 写循环"实战案例** —— 跨业务对比数据，本视频未给出

### 参考来源

#### 视频
- 抖音原视频：https://v.douyin.com/duK_R8ZHcs4/
- 博主 YouTube：https://www.youtube.com/@feicaiclub（小红书/抖音/B站同名）

#### 模型资料
- Claude Fable 5 完全指南：https://claude5.ai/zh/blog/claude-fable-5-complete-guide-2026
- 2026 年 6 月模型横评（Coding + Agentic）：https://www.codingplan.fyi/articles/model_comparisons/20260604/
- Opus 4.8 vs GPT-5.5 vs DeepSeek V4 实测：https://blog.csdn.net/weixin_61823230/article/details/161688001
- 腾讯云 Opus 4.8 vs GPT-5.5：https://cloud.tencent.com/developer/article/2680092

#### Codex 教程
- 知乎保姆级教程：https://zhuanlan.zhihu.com/p/1969399639888336599
- 菜鸟教程：https://www.runoob.com/codex/codex-advanced.html
- ChooseAI 全指南：https://www.chooseai.net/news/4096/
- B站系列教程：https://www.bilibili.com/video/BV11pLX6wE4P/

#### 关联知识
- 上午 Loop + Agnes 归档：`E:\workspace\douyin-knowledge\2026-06-25-Loop-Engineering-Agnes-AI打造项目监控雷达-第四种黑猩猩.md`
- Loop Engineering 归档：`E:\workspace\douyin-knowledge\2026-06-23-AI新范式-循环工程Loop-Engineering与Harness.md`
- Harness 工程归档：`E:\workspace\douyin-knowledge\2026-06-16-Harness工程-自说自话的江哥.md`

---

## 标签

#CodeX #Codex #Harness2 #设目标写循环 #ClaudeFable5 #Opus4.8 #GPT55 #动态工作流 #AI编程 #Agent #LoopEngineering #废才俱乐部Club #范式演进