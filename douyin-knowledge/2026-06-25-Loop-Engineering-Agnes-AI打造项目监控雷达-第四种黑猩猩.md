# Loop Engineering + Agnes AI：打造项目监控雷达

**来源**: https://v.douyin.com/DjQhkemGQik/
**B站对照**: https://www.bilibili.com/video/BV1G7jJ6nEQJ/
**原视频ID**: 7653404615384644986
**博主**: 第四种黑猩猩（AI创业者｜科技前沿探索者｜AI实践派）
**视频发布日期**: 2026-06-20（已 49.8 万点赞）
**宁兄分享日**: 2026-06-25
**音频**: 已下载至 `E:\workspace\skills\douyin-transcribe-skill\temp\audio_loop_agnes.mp3`（~3.3MB，约 7 分钟）
**完整逐字稿**: ⚠️ 待 Groq API Key 配齐后补（见底部「待补」）

---

## 1. 🎯 这是什么

第四种黑猩猩把"Loop Engineering"这种 AI 编程新范式，与 **Agnes AI**（Sapiens AI 推出的全模态免费 API）结合，做出了一个 **"项目监控雷达"** —— 用 AI Agent 自主跑循环，盯住一个项目的关键信号（更新/PR/Issue/价格/库存等），自动判断、自动执行、自动汇报。

这是 Loop Engineering 的**第一个具体落地案例**，证明"人定义目标，AI 自己循环"不是 PPT，而是几十行代码就能跑起来的东西。

---

## 2. 📝 关键功能点

### 2.1 项目监控雷达 = Loop Engineering 的实战模板

| 组件 | 作用 | 对应 Loop 元素 |
|------|------|--------------|
| **监控目标**（GitHub repo / 商品价格 / 服务状态） | 递归目标（Recursive Goal） | "持续监控这个项目直到发现异常" |
| **定时拉取**（scheduler） | 外循环驱动 | 每 N 分钟触发一次 |
| **数据查询工具**（HTTP/RSS/Playwright） | 子智能体工具 | Agent 自己决定何时调用 |
| **状态记忆**（JSON / SQLite） | 外部状态 | 跨轮次的记忆 |
| **验证机制**（变化检测 / 阈值判断） | 内循环验证 | "这次有新内容吗？" |
| **推送通知**（飞书 / 微信 / 邮件） | 自动交接 | 满足条件才叫人 |
| **Agnes AI** | 大脑（理解 + 决策） | "这条信号严重吗？要立刻叫人吗？" |

### 2.2 Agnes AI 工具能力（背景知识）

**Agnes AI**（新加坡 Sapiens AI 团队）—— 全球 Top 10 AI Lab，2026-06-01 起**无限期免费**开放三大模态 API：

| 模型 | 模态 | 用途 | 速率限制 |
|------|------|------|---------|
| **Agnes-2.0-Flash** | 文本 | Agent 大脑、Function Calling、文本生成 | RPM 20 |
| **Agnes-Image-2.1-Flash** | 图像 | 文生图 | RPM 20 |
| **Agnes-Video-V2.0** | 视频 | 文生视频 | RPM 20 |

**关键特性**：
- ✅ **完全兼容 OpenAI SDK** —— 只需替换 `api_key` + `base_url`，存量代码 0 改造
- ✅ **0 Token 消耗**（免费但有速率限制）
- ✅ **不绑卡、不充值** —— 注册即用
- ✅ **Function Calling** 标准支持
- ✅ **多模态统一入口** —— 文本/图像/视频一个 Key 通吃

**接入地址**：`https://platform.agnes-ai.com`（注册拿 Key）

### 2.3 Loop + Agnes 的化学反应

> 昨天归档的 `2026-06-23-AI新范式-循环工程Loop-Engineering与Harness.md` 讲了 Loop Engineering 的**理论**；
> 今天这个视频展示了 Loop Engineering 的**工程落地** —— 选一个 **0 Token 的 LLM** 当大脑，跑一个永远不停的循环。

**最大价值**：当 AI 调用 0 成本 + AI 自己跑循环 = "永远在线的免费 AI 员工"成为现实。

---

## 3. ⚡ 怎么使用（参考实现）

### 3.1 Agnes AI 接入（最快路径）

```python
# 安装 OpenAI SDK（兼容）
# pip install openai>=1.0.0

from openai import OpenAI

client = OpenAI(
    api_key="<从 platform.agnes-ai.com 拿的 Key>",
    base_url="https://api.agnes-ai.com/v1"  # 替换这个即可
)

resp = client.chat.completions.create(
    model="Agnes-2.0-Flash",
    messages=[{"role": "user", "content": "分析这条信号严重吗？"}],
    tools=[...]  # 支持 Function Calling
)
```

> 注：以上 `base_url` 来源于掘金/CSDN 多篇实战评测，实际以 platform.agnes-ai.com 文档为准。

### 3.2 项目监控雷达骨架（Loop Engineering 风格）

```python
# 伪代码 —— 第四种黑猩猩视频的核心思路
import time
from agnes_client import AgnesClient  # 你的 Agnes 封装

STATE_FILE = "radar_state.json"
TARGET = "https://github.com/<owner>/<repo>/releases.atom"

def fetch_signals():
    """拉取信号（HTTP/RSS/Playwright 自由组合）"""
    return requests.get(TARGET).text

def has_change(new_signals, old_signals):
    """验证机制：是否有变化？"""
    return new_signals != old_signals

def judge_severity(signal: str, agnes: AgnesClient) -> dict:
    """Agnes 当大脑：判断是否严重、是否需要叫人"""
    return agnes.chat(
        model="Agnes-2.0-Flash",
        prompt=f"判断这条项目信号严重性:\n{signal}",
        tools=[notify_feishu, create_github_issue]
    )

def loop():
    """外循环：AI 自己跑，自己停"""
    state = load_state(STATE_FILE)
    while True:
        signals = fetch_signals()
        if has_change(signals, state.get("last")):
            decision = judge_severity(signals, agnes)
            if decision["need_notify"]:
                notify_feishu(decision["summary"])
        state["last"] = signals
        save_state(STATE_FILE, state)
        time.sleep(300)  # 5 分钟一次 —— 由 Loop 自己决定何时休眠
```

**这就是 Loop Engineering 落地到"项目监控"的完整骨架**。

---

## 4. ✅ 优点

| 维度 | 评价 |
|------|------|
| **范式新颖** | 第一个把 Loop Engineering 落到具体场景的实操案例 |
| **工具选择聪明** | Agnes 0 Token + 兼容 OpenAI = 几乎零成本无限循环 |
| **可复用性强** | 模板可改造成：商品价格雷达 / 服务健康监控 / 资讯聚合 / 舆情监听 |
| **门槛低** | 几十行 Python 就能跑，比搭 LangGraph 简单 10 倍 |
| **品牌定位清** | 第四种黑猩猩作为"AI 实践派"博主，内容接地气、有代码、有原理 |

---

## 5. ❌ 缺点 / 待验证

| 维度 | 评价 |
|------|------|
| **RPM 20 限制** | Agnes 免费版每分钟 20 次，多目标/高频监控会撞墙 |
| **稳定性未知** | 0 Token 免费模式，长期 SLO 没有承诺（搜不到 SLA 文档） |
| **完整逐字稿缺失** | 本次归档时 Groq API Key 尚未配置，转录待补 |
| **博主代码仓库** | 视频中提到的 GitHub 仓库未直接公布链接，需翻评论区确认 |

---

## 6. 🎬 使用场景

### 6.1 适合谁

- **跨境电商运营**：盯竞品价格 / 库存 / 关键词排名
- **开发者**：盯 GitHub 项目 release / issue / PR / CI 状态
- **运维 SRE**：盯服务健康度 / 错误率 / 慢接口
- **自媒体 / 投研**：盯新闻 / 公告 / 价格异动
- **个人 AI 玩家**：拿 0 Token 的模型 + 自己的小脚本 = 24h 数字员工

### 6.2 不适合谁

- 需要强一致性的关键业务（金融交易、医疗监护）
- 实时性要求 < 1 分钟的场景（受 RPM 限制）
- 团队级生产系统（无 SLA 不敢用）

---

## 7. 🔧 运行依赖环境

| 依赖 | 必须？ | 说明 |
|------|-------|------|
| Python 3.10+ | ✅ | 主脚本语言 |
| OpenAI SDK ≥ 1.0.0 | ✅ | 兼容调用 Agnes |
| Agnes API Key | ✅ | 从 platform.agnes-ai.com 免费注册 |
| requests / httpx | ✅ | 信号拉取 |
| 定时机制 | ✅ | APScheduler / cron / asyncio.sleep |
| 状态持久化 | 推荐 | JSON / SQLite / Redis 任选 |
| 通知渠道 | 推荐 | 飞书 / 微信 / 邮件 webhook |
| Groq API Key | 选 | 仅本工作流归档需要 |

---

## 8. 🚀 部署使用注意点

### 8.1 Agnes 接入坑（来自 CSDN/掘金实测）

1. **`base_url` 经常变** —— 文档更新滞后，不同评测里给的 URL 不一致（实测以 platform.agnes-ai.com 控制台为准）
2. **字段名不一致** —— 部分接口参数名跟 OpenAI 不完全一样，要看具体文档
3. **RPM 20 限制** —— 不是 QPS，是 RPM（每分钟），并发 20 次就限流
4. **Tool Calling 格式** —— 跟 OpenAI 一致，但部分高级 tool（如并行调用）可能不支持

### 8.2 Loop Engineering 落地坑

1. **终止条件必须明确** —— 否则 Agent 会"无限打转"消耗资源
2. **验证机制要轻量** —— 每次循环都调 LLM 成本高，能用规则/Hash 判断就用规则
3. **外部状态必须有** —— 跨轮次记忆靠文件/数据库，不能只放内存
4. **异常必须捕获** —— Loop 是死循环，一个未捕获的异常直接挂掉整个雷达

### 8.3 部署方式推荐

- **个人测试**：本地 Python + cron 即可
- **生产级**：Docker + 进程守护（supervisord / pm2）
- **团队共享**：FastAPI 包装成 Web 控制台

---

## 9. 🕳️ 避坑指南

🔴 **坑 1：把 Loop Engineering 当万能解药**
现实：Loop 解决"持续盯一个目标"的问题，不解决"一次性复杂任务"。ReAct 单次调用 vs Loop 长期循环，是两种工具，不是替代关系。

🔴 **坑 2：选了高价的 LLM**
现实：Loop 是**长时间运行**的，调一次 GPT-4o 一周账单爆炸。选 **0 Token 的 Agnes** 或者便宜的本地模型（qwen2.5:7b 之类），否则跑两天就停。

🟡 **坑 3：变化检测用 LLM 做**
现实："这次有新内容吗"——用 hash / diff / 时间戳就够了。每轮都调 LLM 是浪费。
正确做法：先规则过滤（"信号变了没"），变了再调 LLM 决策（"严不严重、要不要叫人"）。

🟡 **坑 4：没有终止机制**
现实：Loop 是 `while True`，一旦信号源异常或 LLM 幻觉，可能无限通知。
正确做法：加 速率限制（同一信号 1 小时内最多推一次）+ 严重程度阈值（critical/warning/info）+ 人工确认 ack。

🟢 **坑 5：忽视 Agnes RPM 20**
现实：5 个监控目标 × 每目标每分钟 1 次 = 5 RPM，安全；50 个目标就爆了。
正确做法：监控目标数 × 频率 ≤ 18 RPM，留 2 RPM 余量。

---

## 10. 📊 总结

### 一句话概括
**"Loop Engineering + Agnes AI = 0 Token 成本的'永远在线 AI 监控雷达'"** —— 用 AI 自己跑循环 + 免费 LLM，几十行代码做出过去需要 SaaS 才能实现的项目监控能力。

### 学习价值：⭐⭐⭐⭐⭐（5星）
- 第一个 Loop Engineering **完整落地案例**
- 工具选型教科书（0 Token + OpenAI 兼容 = 复用一切存量代码）
- 监控场景的"最小可执行 Loop"模板可直接套用

### 推荐指数：⭐⭐⭐⭐⭐（5星）
- 视频点赞 49.8 万，验证了市场热度
- 落地门槛极低（Python 几十行）
- 与"Prompt → Context → Harness → Loop"演进完美契合

### 与宁兄已有知识串联

#### 演进链路
```
2026-06-16  Harness 工程（江哥第88集）
     ↓
2026-06-23  Loop 工程（AI有点聊，理论）
     ↓
2026-06-25  Loop + Agnes 工程（第四种黑猩猩，实战）  ← 本视频
```

#### 工具关联
- **Harness Engineering**：Loop 的基础设施（工具、约束、验证）
- **MCP**：可替换 Agnes Function Calling，给 Loop 提供"身体"
- **Agnes AI**：Loop 的"大脑"，0 Token 成本
- **Claude Code / Codex**：Loop 跑在哪个环境里都行

#### ELUCKY 场景应用建议
- **跨境电商**：用 Loop 盯 230 个 TikTok 账号的爆款指标
- **京麦自动化**：用 Loop 跑"截图→识别→填表→验证"循环（已有类似雏形）
- **京麦价格雷达**：用 Loop 盯竞品价格，自动调价（前提：突破 RPM 限制）

### 待补清单

- [ ] **完整逐字稿** —— 待 Groq API Key 配齐后转录音频
- [ ] **第四种黑猩猩 GitHub 仓库**（视频中提到的代码）—— 翻评论区或主页确认
- [ ] **Agnes 官方文档链接**（base_url / 模型名最终确认）—— 以 platform.agnes-ai.com 为准
- [ ] **Loop Engineering 5 个核心构建块**（昨天归档待深挖）

### 参考来源

#### 视频
- 抖音原视频：https://v.douyin.com/DjQhkemGQik/
- B站对照：https://www.bilibili.com/video/BV1G7jJ6nEQJ/
- 博主主页：https://www.toutiao.com/c/user/token/MS4wLjABAAAA4HrK-U7kcKnO12CsoJzNRmikRjTPTSLDwfC__5iPYgzlighRz9J3a_O5gG4gCGwU/

#### Agnes AI 资料
- 官方 GitHub：https://github.com/AgnesAI-Labs/Agnes-AI
- 第三方 GitHub：https://github.com/chenpipi0807/Agnes-API
- 平台：https://platform.agnes-ai.com
- 实测报告 1（CSDN）：https://blog.csdn.net/liuzi511/article/details/161676911
- 实测报告 2（CSDN）：https://blog.csdn.net/xiaoma0529/article/details/161936754
- 实测报告 3（CSDN）：https://blog.csdn.net/2601_96229017/article/details/161613225
- 接入指南（掘金）：https://juejin.cn/post/7648530852034854964
- Codex 集成：https://blog.csdn.net/weixin_41961749/article/details/161663207

#### 关联知识
- 昨天 Loop Engineering 归档：`E:\workspace\douyin-knowledge\2026-06-23-AI新范式-循环工程Loop-Engineering与Harness.md`
- 江哥 Harness 工程归档：`E:\workspace\douyin-knowledge\2026-06-16-Harness工程-自说自话的江哥.md`
- Loop Engineering 深度解析：https://zhuanlan.zhihu.com/p/2048317502342666078

---

## 标签

#LoopEngineering #AgnesAI #SapiensAI #零Token #OpenAI兼容 #项目监控 #AI雷达 #Agent实战 #第四种黑猩猩 #Harness #循环工程 #FunctionCalling