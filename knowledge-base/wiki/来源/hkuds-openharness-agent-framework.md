# HKUDS OpenHarness 轻量级Agent框架深度研究报告

## 1. 🎯 这是什么

OpenHarness 是港大HKUDS开源的**轻量级Agent基础设施框架**，核心理念：**"The model is the agent. The code is the harness."**

用**1万行Python**复刻了Claude Code 98%的工具能力。

## 2. 📝 关键功能点

### Agent Harness 定义
Agent Harness = 包裹在LLM外面的完整基础设施

| 组件 | 作用 |
|------|------|
| 🖐️ **hands** | 工具调用（执行操作） |
| 👀 **eyes** | 感知/观测（理解环境） |
| 💾 **memory** | 记忆管理（存储上下文） |
| 🛡️ **safety** | 安全边界（限制行为） |

### 核心数据对比
| 维度 | Claude Code | OpenHarness | 比例 |
|------|-------------|-------------|------|
| 代码量 | 50万行 | 1万行 | **3%** |
| 工具覆盖 | 100% | 98% | - |
| 模型支持 | 仅Anthropic | 任意LLM | 全面 |

### 技术特点
1. **极简代码**：1万行Python vs Claude Code 50万行
2. **兼容生态**：直接使用 anthropics/skills 和 claude-code/plugins
3. **任意模型**：支持任何LLM（不只是Claude）
4. **模块化设计**：hands/eyes/memory/safety 解耦

## 3. ⚡ 怎么使用

### 安装命令
```bash
# 安装
pip install open-harness
# 或
pip install oh

# 初始化项目
oh init my-agent

# 配置模型
oh config --model gpt-4
# 或
oh config --model claude-3-5-sonnet

# 运行
oh run --task "完成XX任务"
```

### 核心命令
```bash
oh init <project>     # 初始化项目
oh run --task <task>  # 运行任务
oh tools list         # 查看可用工具
oh skills list        # 查看可用技能
oh memory view        # 查看记忆状态
oh safety config      # 配置安全边界
```

## 4. ✅ 优点

1. **代码量少**：1万行 vs 50万行，易于理解和修改
2. **模型无关**：不绑定特定LLM，任意模型可用
3. **生态兼容**：直接使用Claude Code的skills和plugins
4. **模块化**：各组件解耦，便于定制
5. **研究友好**：轻量级，适合学习Agent原理

## 5. ❌ 缺点

1. **生态不足**：刚起步，工具链不如Claude Code完善
2. **企业功能缺失**：权限管理、审计日志等企业级功能
3. **稳定性待验证**：生产环境使用需要谨慎
4. **文档有限**：目前文档较少

## 6. 🎬 使用场景

| 场景 | 适用性 |
|------|--------|
| 学习Agent架构 | ⭐⭐⭐⭐⭐ 最佳选择 |
| 快速原型开发 | ⭐⭐⭐⭐ |
| 研究实验 | ⭐⭐⭐⭐⭐ |
| 生产环境 | ⭐⭐⭐ 需谨慎 |
| 定制化Agent | ⭐⭐⭐⭐ |

## 7. 🔧 运行依赖环境

- Python 3.10+
- 任意LLM API（OpenAI/Anthropic/本地模型等）
- 网络（用于API调用）

## 8. 🚀 部署使用注意点

### 与Claude Code对比
| 特性 | Claude Code | OpenHarness |
|------|-------------|-------------|
| 代码量 | 50万行 | 1万行 |
| 模型绑定 | 仅Anthropic | 任意 |
| 部署方式 | 需安装 | pip install |
| 成本 | API费用 | API费用 |

### 最佳实践
1. 用OpenHarness学习原理
2. 生产环境用Claude Code/OpenClaw
3. 需要定制时基于OpenHarness修改

## 9. 🕳️ 避坑指南

### 坑1：文档不足
**问题**：上手资料少
**解决**：参考GitHub README和知乎教程

### 坑2：企业功能缺失
**问题**：没有权限管理、审计等
**解决**：生产环境建议用OpenClaw

### 坑3：工具链不完善
**问题**：部分高级工具缺失
**解决**：可复用Claude Code的skills插件

## 10. 📊 总结

| 维度 | 评分 |
|------|------|
| 学习价值 | ⭐⭐⭐⭐⭐ |
| 实用性 | ⭐⭐⭐ |
| 创新性 | ⭐⭐⭐⭐ |
| 成熟度 | ⭐⭐⭐ |

**结论**：OpenHarness是Agent学习研究的最佳起点，代码量少且架构清晰。适合想理解Agent底层原理的开发者。

## 附录：相关链接

| 资源 | 链接 |
|------|------|
| GitHub | github.com/HKUDS/OpenHarness |
| 知乎深度解析 | zhuanlan.zhihu.com/p/2023517045422047369 |
| 知乎技术分析 | zhichai.net/topic/177169535 |
