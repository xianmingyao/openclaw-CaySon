# OpenCode + Claude Code Skills完整指南

> 学习日期：2026-04-22

> 来源：抖音 @算力炼丹炉 等

> 视频：我不允许你还没用上开源版Claude design / 重写开源版Claude Code

## 视频概述

### 视频1：开源版Claude design

| 项目 | 内容 |

|------|------|

| **标题** | 我不允许你还没用上开源版Claude design ！ |

| **作者** | @算力炼丹炉 |

| **发布时间** | 2026-04-21 15:48 |

| **数据** | 4446点赞 / 5573收藏 / 852转发 |

| **标签** | #模型 #科技 #ai |

**热评：** "立即用上了，非常nice"、"已亲测，确实不错"

### 视频2：重写开源版Claude Code

| 项目 | 内容 |

|------|------|

| **标题** | 第179集 \| 重写开源版Claude Code ，21天突破18万 |

| **作者** | @骋风算力 |

| **发布时间** | 2026-04-22 17:30 |

| **数据** | 92点赞 / 66评论 / 8转发 |

**项目结构：**

rust/...           ← 核心逻辑（Rust生成CLI二进制）

vscode_ext/...     ← VSCode插件

openai/...         ← Rust接口（高性能封装）

common/...         ← 通用组件

typescript_ext/... ← 原有TypeScript代码

## OpenCode Skills（已安装）

| # | Skill | 版本 | 用途 |

|---|-------|------|------|

| 1 | **opencode** | 1.2.2 | AI驱动代码编辑器（Cursor/Windsurf的CLI/TUI版本） |

| 2 | **opencode-cli** | 1.1.0 | OpenCode CLI集成，AI Agent执行编码任务 |

| 3 | **opencode-controller** | 1.0.0 | 通过斜杠命令控制OpenCode会话/模型/代理 |

| 4 | **opencode-acp-control-3** | 0.1.1 | 通过ACP协议直接控制OpenCode |

| 5 | **easy-opencode** | 1.1.1 | OpenCode可以做所有代码相关的事情 |

### OpenCode核心功能

- **Plan→Build工作流**：计划→构建

- **多模型支持**：Claude Code, Codex, Gemini, Claude, Pi

- **多代理模式**：4种模式+自定义代理

- **Custom Tools**：TypeScript工具扩展

- **Skills加载**：动态加载技能

- **SDK**：完整API结构化输出

## Claude Code Skills（已安装）

| # | Skill | 版本 | 用途 |

|---|-------|------|------|

| 1 | **claude-code-runner** | 0.1.0 | 通过PTY执行Claude Code编程任务 |

| 2 | **claude-code-pro** | 1.1.0 | Token高效工作流（不用轮询tmux） |

| 3 | **claude-code-control** | 1.2.0 | 通过AppleScript控制终端窗口 |

## OpenCode vs Claude Code对比

| 维度 | OpenCode | Claude Code |

|------|----------|-------------|

| **定位** | AI代码编辑器(CLI/TUI) | AI编程Agent |

| **界面** | 终端界面 | 命令行Agent |

| **协议** | ACP (Agent Client Protocol) | MCP (Model Context Protocol) |

| **特点** | 多模型支持，斜杠命令 | 原生Claude，工具调用 |

| **安装** | `pip install opencode` | `npm install -g @anthropics-ai/claude-code` |

## 安装命令

# OpenCode系列

openclaw skills install opencode

openclaw skills install opencode-cli

openclaw skills install opencode-controller

openclaw skills install opencode-acp-control-3

openclaw skills install easy-opencode

# Claude Code系列

openclaw skills install claude-code-runner

openclaw skills install claude-code-pro

openclaw skills install claude-code-control

## 相关热门视频推荐

| 标题 | 点赞 | 时长 | 简介 |

|------|------|------|------|

| Claude Code的设计哲学：渐进式披露 | 2.8万 | 06:45 | 讲设计哲学 |

| OpenCode+Skill：实战到原理一次搞懂 | 2.4万 | 07:27 | OpenCode+Skill实战 |

| Claude构建多智能体协作实战教程 | 9366 | 09:01 | Claude指挥Codex和Gemini |

| Claude Code快速入门 课程介绍与软件安装 | 2617 | 16:06 | 入门教程 |

## 工作流建议

[OpenCode] ←→ [Claude Code] ←→ [OpenClaw]

↓              ↓              ↓

斜杠命令      Agent模式      技能编排

↓              ↓              ↓

编码任务      复杂推理       多Agent协作

## 相关资源

- OpenCode官网：待查找

- Claude Code官网：待查找

- SkillHub：https://clawhub.ai