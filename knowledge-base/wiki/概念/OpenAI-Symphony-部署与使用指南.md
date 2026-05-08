# OpenAI Symphony - 部署与使用指南

## 1. 🎯 概述

Symphony 是一个**开源规范**，不是完整托管平台。需要自己搭建配套环境才能使用。

---

## 2. 📋 部署前提

### 2.1 必需组件

| 组件 | 说明 | 必需 |
|------|------|------|
| **Linear** | 任务看板系统 | ✅ |
| **Codex App Server** | Codex 运行服务器 | ✅ |
| **Symphony 规范** | 编排逻辑定义 | ✅ |
| **API Key** | OpenAI API | ✅ |
| **GitHub** | 代码仓库 | ✅ |

### 2.2 环境要求

- Python 3.10+
- Docker (可选)
- 网络能访问 OpenAI API
- Linear 团队账号

---

## 3. 🔧 部署步骤

### 3.1 克隆仓库

```bash
git clone https://github.com/openai/symphony.git
cd symphony
```

### 3.2 安装依赖

```bash
pip install -e .
```

### 3.3 配置环境变量

创建 `.env` 文件：

```bash
# OpenAI API
OPENAI_API_KEY=sk-...

# Linear API
LINEAR_API_KEY=...

# GitHub Token
GITHUB_TOKEN=ghp_...

# Codex App Server
CODEX_APP_URL=http://localhost:8080
```

### 3.4 配置 Symphony

创建 `symphony.yaml`：

```yaml
# 工作流配置
workflow:
  # Linear 看板配置
  linear:
    team_id: YOUR_TEAM_ID
    project_id: YOUR_PROJECT_ID
    
  # Codex 配置
  codex:
    app_url: http://localhost:8080
    model: gpt-4o
    
  # 隔离工作区
  workspace:
    type: docker  # 或 local
    image: openai/codex:latest
    
  # 失败重试
  retry:
    max_attempts: 3
    backoff: exponential
```

### 3.5 启动 Codex App Server

```bash
# 方式1: Docker
docker run -p 8080:8080 openai/codex-app

# 方式2: CLI
codex-app serve --port 8080
```

### 3.6 启动 Symphony

```bash
# 启动编排器
symphony run --config symphony.yaml

# 或后台运行
symphony run --config symphony.yaml --daemon
```

---

## 4. 📁 项目结构

```
symphony/
├── SPEC.md           # 核心规范定义
├── WORKFLOW.md       # 工作流配置说明
├── symphony/         # 核心代码
│   ├── __init__.py
│   ├── orchestrator.py  # 编排器
│   ├── agent.py         # Agent 封装
│   ├── workspace.py      # 隔离工作区
│   └── linear.py        # Linear 集成
├── examples/        # 示例配置
├── tests/           # 测试
└── README.md
```

---

## 5. ⚙️ 工作流配置 (WORKFLOW.md)

### 5.1 Linear 集成配置

```yaml
linear:
  # 监听特定的 Issue 状态
  trigger_states:
    - "In Progress"
    - "Todo"
    
  # 标签过滤
  labels:
    - "symphony-enabled"
    
  # 忽略的标签
  ignore_labels:
    - "symphony-ignore"
```

### 5.2 Codex Agent 配置

```yaml
codex:
  # 模型选择
  model: gpt-4o
  
  # 系统提示词
  system_prompt: |
    你是一个高效的编码助手。
    遵循 Linear Issue 中的要求完成任务。
    确保代码通过 CI 测试。
    
  # 超时设置
  timeout: 1800  # 30分钟
  
  # 并发数
  max_concurrent: 3
```

### 5.3 工作区配置

```yaml
workspace:
  # 隔离级别
  isolation: container
  
  # 每个任务独立工作区
  per_task_workspace: true
  
  # 代码库路径
  repo_path: /path/to/repo
```

---

## 6. 🚀 使用流程

### 6.1 创建 Linear Issue

在 Linear 中创建一个 Issue，可以选择：
- 添加 `symphony-enabled` 标签
- 或分配给特定的 Team

### 6.2 Symphony 自动处理

```
Issue 创建
    │
    ▼
Symphony 监听到达
    │
    ▼
任务拆分 (如果是复杂Issue)
    │
    ▼
为每个子任务启动 Codex Agent
    │
    ▼
隔离工作区执行代码
    │
    ▼
CI/CD 测试验证
    │
    ▼
自动创建 PR
    │
    ▼
通知审核
```

### 6.3 人工审核

- 检查 PR 内容
- 审核代码变更
- 决定是否合并

---

## 7. ⚠️ 部署注意点

### 7.1 安全风险

| 风险 | 缓解措施 |
|------|----------|
| **Agent 权限过大** | 配置只读 GitHub token |
| **代码执行风险** | 沙箱环境隔离 |
| **API Key 泄露** | 使用环境变量，不提交到 Git |
| **恶意代码注入** | Issue 内容过滤和验证 |

### 7.2 稳定性

| 问题 | 解决方案 |
|------|----------|
| **Codex 超时** | 配置合理的超时和重试 |
| **CI 失败** | 设置最大重试次数 |
| **并发过高** | 限制 max_concurrent |
| **API 限流** | 添加请求间隔 |

### 7.3 成本控制

| 策略 | 说明 |
|------|------|
| **模型选择** | 简单任务用 gpt-4o-mini |
| **Token 限制** | 设置最大上下文长度 |
| **任务拆分** | 避免大Issue消耗过多 |

### 7.4 Linear API 限制

- Linear API 有速率限制
- 需要配置合理的轮询间隔
- 建议 30 秒以上

---

## 8. 🔧 故障排查

### 8.1 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| Codex 不执行 | App Server 未启动 | 检查 localhost:8080 |
| 无法创建 PR | GitHub Token 权限不足 | 添加 repo 权限 |
| Issue 未被监听 | 标签配置错误 | 检查 symphony.yaml |
| 工作区创建失败 | Docker 未安装 | 安装 Docker 或用 local |

### 8.2 日志查看

```bash
# 查看 Symphony 日志
symphony logs

# 查看 Codex App 日志
docker logs codex-app
```

---

## 9. 📊 与 OpenClaw 集成

### 9.1 理念对比

| 维度 | Symphony | OpenClaw |
|------|----------|----------|
| **控制平面** | Linear 任务系统 | 消息平台 |
| **Agent** | Codex | 多Agent |
| **执行方式** | 任务驱动 | 事件驱动 |
| **自动化** | 研发流程 | 全场景 |

### 9.2 集成可能

Symphony 的规范可以被 OpenClaw 借鉴：
- 用 Linear 作为任务源
- 用 OpenClaw Skills 扩展 Agent 能力
- 统一的编排层

---

## 10. ✅ 总结

| 项目 | 说明 |
|------|------|
| **部署难度** | ⭐⭐⭐ 中等 |
| **前置依赖** | Linear + Codex App Server |
| **核心价值** | 全自动研发流水线 |
| **最适合** | 有 Linear 的研发团队 |

---

*📅 收录日期：2026-05-08*
*⚠️ 注意：网络无法访问 GitHub，详情请参考官方文档*
