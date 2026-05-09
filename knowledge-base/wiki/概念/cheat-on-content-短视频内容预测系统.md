# cheat-on-content - 短视频内容预测系统

> 来源：小红书【他们都叫我蜗牛学长】+ GitHub XBuilderLAB/cheat-on-content
> 日期：2026-05-09
> GitHub：https://github.com/XBuilderLAB/cheat-on-content (1.2k stars)

## 核心定位

**不是生成内容，而是预测+评估内容**

| 其他工具 | cheat-on-content |
|---------|-----------------|
| 给"灵感" | 让你的直觉可衡量 |
| AI替你写 | AI评判，你的脚本还是你的 |
| 发10个版本A/B测试 | 发1个，下注，用数据结算 |
| 静态仪表盘 | 进化评分系统（3个月后的公式和起点不一样）|

## 项目信息

| 项目 | 信息 |
|------|------|
| **Star** | 1.2k |
| **Fork** | 252 |
| **语言** | Shell 50.8% + Python 49.2% |
| **贡献者** | Jooonnn, woniuxuezhang, songth1ef, claude |

## 技术架构

```
cheat-on-content/
├── adapters/         # 平台适配器（抖音/小红书等）
├── docs/            # 文档
├── examples/        # 示例
├── hooks/           # 核心预测钩子
│   ├── log-event.sh           # 事件日志
│   ├── prediction-immutability.json/sh  # 预测不可篡改
│   └── session-start.sh       # 会话启动
├── migrations/      # 迁移脚本
├── shared-references/
├── skills/          # Claude Code技能
├── starter-rubrics/ # 起始评分模板
├── templates/       # 预测模板
├── tools/           # 工具
│   └── score-curve.py  # 评分曲线（核心预测算法）
└── SKILL.md         # 技能定义
```

## 预测系统核心

### v2 prediction system 特性

1. **预测不可篡改**：Hook机制阻止编辑`## 预测`/`## Prediction`区块
2. **事后脚本修改**：通过append处理，不改变原预测
3. **评分曲线算法**：`score-curve.py` 核心预测引擎

### 预测指标体系

| 指标 | 说明 | 精度 |
|------|------|------|
| 播放量 | 预测vs实际 | ±1% ⭐⭐⭐ |
| Bucket(流量池) | 30-100w级别命中 | ✅ 命中 |
| 赞播比 | 点赞率评估 | 4.16%为"强" |
| 分播比 | 分享率 | 1.69%为"良好" |

### MS维度拆解

- **M**: 模版（Template）
- **S**: 数字模式（Number pattern）
- **MS**: 交互效应（Interaction effect）

## 核心洞察

**"90%的创作者都活跃在同一个循环里"**

项目本质：
1. 预测→发布→复盘→优化公式的闭环
2. v2.1单样本强证据——精度±1%
3. 短视频内容预测是可量化系统，不是玄学

## 与其他工具对比

### 为什么不能只用ChatGPT/DeepSeek/豆包？

这些工具给"灵感"，但不帮你"验证"。
cheat-on-content的核心是**让你的直觉变得可衡量**。

### 核心价值

- 把"感觉会火"变成"预测值+置信区间"
- 用数据说话，不是凭感觉
- 持续迭代评分模型

## 安装使用

```bash
# 安装
curl -fsSL https://raw.githubusercontent.com/XBuilderLAB/cheat-on-content/main/install.sh | bash

# 首次运行
# 使用Claude Code集成 skill

# 日常工作流
# 1. 写脚本
# 2. 让AI预测评分
# 3. 发布内容
# 4. 复盘预测准确性
# 5. 更新评分模型
```

## 价值评估

| 维度 | 评分 | 说明 |
|------|------|------|
| **技术价值** | ⭐⭐⭐⭐ | 预测+评估闭环，Hook机制新颖 |
| **商业价值** | ⭐⭐⭐⭐ | 短视频运营神器 |
| **学习价值** | ⭐⭐⭐⭐ | 评分系统+不可篡改预测可借鉴 |
| **集成价值** | ⭐⭐⭐ | 可研究思路，不一定直接用 |

## 相关概念

- [[短视频流量预测]]
- [[内容评分系统]]
- [[Claude-Code-Skills生态]]
