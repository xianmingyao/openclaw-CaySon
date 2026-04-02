# MEMORY.md - 长期记忆

## 用户信息
- **称呼**：宁采臣 / 宁兄
- **身份**：CTO，24年技术老炮
- **时区**：Asia/Shanghai

## 核心规范
- 代码必须落地到文件，不能只存在对话中
- 铁律1：实事求是，数据说话
- 铁律2：代码质量 > 代码速度 > 代码炫技

## 记忆检索铁律（重要！）
1. 首选 → 云端 Milvus (8.137.122.11:19530)
2. 备选 → 本地 ChromaDB (Milvus 故障时降级)

## 日报格式逻辑

### 标准格式
```
YYYY.MM.DD(日报)
1、事项 + 完成进度%（括号内补充当日情况）
2、事项 + 状态（括号内补充当日情况）
...
```

### 格式要素
- **日期标题**：`YYYY.MM.DD(日报)`
- **序号**：用中文序号（1、2、3...）
- **事项**：简短描述工作内容
- **进度/状态**：方括号[65]表示百分比，或文字状态
- **括号补充**：说明当日具体情况

### 补充说明类型
- 完成进度：完成进度[65]%
- Git情况：今日无Git提交记录
- 异常情况：今日无异常反馈
- 申请状态：今日重新提交申请接口
- 持续运行：持续运行中

### 涉及人员
- 小刘、小龙虾、京采、小蒙

### 涉及项目
- 京麦智能体、知识库、OpenClaw系统

## 项目记忆
- 京麦智能体：搭建中，进度65%
- OpenClaw：多渠道AI助手，持续运行

## 2026-04-02 技术研究成果

### 浏览器自动化工具集（来源：抖音@大力AI）

| 工具 | 状态 | 说明 |
|------|------|------|
| browser-use CLI | ✅ 已安装 0.12.5 | YC孵化，Token高效，AI Agent专用 |
| agent-browser | ✅ 已装 | OpenClaw技能，Windows友好 |
| WebMCP | 🔍 研究完 | Chrome官方2026-02-10发布，趋势 |

### 关键文档
- `knowledge/browser-use-cli.md` - browser-use CLI 2.0 完整技术报告
- `knowledge/webmcp-mcp-browser-automation.md` - WebMCP + MCP深度报告

### 重要结论
1. **browser-use --mcp** 是官方MCP方案，mcp-browser-use第三方包暂不兼容
2. **Windows必须**设置 `$env:PYTHONIOENCODING="utf-8"` 避免emoji错误
3. **agent-browser + browser-use CLI** 互补，建议同时使用
4. **WebMCP** 是未来趋势（2026年中正式版），值得关注

### GitHub Claude Code相关仓库

| 仓库 | Stars | 定位 | 推荐度 |
|------|-------|------|--------|
| instructkr/claw-code | 48,000+ | Clean-room重写，合法安全 | ⭐⭐⭐⭐⭐ |
| sanbuphy/claude-code-source-code | Fork 41,500 | 泄露源码，⚠️法律风险 | ⭐（仅研究） |
| unohee/OpenSwarm | 232 | 多Agent编排器 | ⭐⭐ |

### GStack 角色映射表

**核心理念：** AI Agent模拟软件团队全生命周期

9大角色：CEO规划 / 工程经理架构 / Staff工程师找bug / QA测试 / 安全护栏 等

### KiloClaw 全托管OpenClaw

**一句话：** OpenClaw全托管云服务，60秒一键部署

**核心特点：**
- ⚡ 60秒部署（vs自托管30-60分钟）
- 🔒 零运维（自动安全/更新/监控）
- 🌐 50+平台接入
- 🤖 500+模型（Kilo Gateway）
- 🏢 企业版解决"影子AI"安全问题
