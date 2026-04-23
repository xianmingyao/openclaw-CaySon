# 来源摘要：articles\llm-training-data-sources.md

> 原始路径：raw/articles\llm-training-data-sources.md

> 摄入时间：2026-04-12 20:03

## 核心观点

文章详细介绍了五种LLM训练数据来源，包括人工标注、强模型生成、开源数据集整合、真实用户交互提取和已有文档/知识库转化。

## 关键细节

# LLM训练数据来源详解

> 来源：直播课程截图（明瑶 76250）

> 时间：18:07

> 截图：2026-04-10-18-07-LLM训练数据来源.jpg

## 五种数据来源

### 1. 人工标注（最高质量）

- **成本**：$1-10/条

- **特点**：由领域专家或专业标注员按详细指南编写

- **流程**：详细标注规范 → 多标注员交叉验证 → 质检

- **适用**：核心能力数据、安全对齐数据、高风险领域数据

### 2. 基于强模型生成（性价比最高）

- **方法**：使用GPT-4、Claude等强模型生成训练数据

- **常用技术**：Self-Instruct, Evol-Instruct, 直接批量生成

- **注意事项**：

- 需后续质量过滤（通过率通常60%-80%）

- 注意输出同质化问题

- 注意模型使用条款限制

### 3. 开源数据集整合

- **通用型**：OpenAssistant, ShareGPT, Alpaca, FLAN Collection, UltraChat

- **代码类**：CodeAlpaca

## 相关实体

- [[GPT-4]]

- [[Claude]]

- [[OpenAssistant]]

- [[ShareGPT]]

- [[Alpaca]]

- [[CodeAlpaca]]

- [[Magicoder-OSS-Instruct]]

- [[MetaMathQA]]

- [[GSM8K-augmented]]

- [[BELLE]]

- [[Firefly]]

- [[MOSS-SFT]]

- [[InfinityInstruct]]

## 相关概念

- [[人工标注]]

- [[强模型生成]]

- [[开源数据集整合]]

- [[真实用户交互提取]]

- [[已有文档/知识库转化]]

---

*由 Karpathy 知识库系统自动生成*