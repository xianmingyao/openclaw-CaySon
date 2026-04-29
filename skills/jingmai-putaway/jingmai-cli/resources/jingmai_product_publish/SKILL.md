---
name: jingmai_product_publish
description: 京麦商品发布 skill，使用结构化 processor 入口执行并生成阶段轨迹
category: automation
version: 1.1.0
author: jingmai-agent
entry_script: scripts/run_skill.py
working_dir: .
config_dir: config
artifact_dir: artifacts
trace_mode: structured_json
metadata:
  display_title: jingmai-product-publish
  match_keywords:
    - jingmai-product-publish
    - 京麦商品发布
    - 京麦上架
    - 京麦发布
    - jingmai product publish
  source_skill_dir: E:\workspace\skills\jingmai-product-publish
---

# Jingmai Product Publish

这个 skill 不再只作为 prompt 文本存在，而是一个可执行 skill 包。

## 核心原则：先看后做

**重要：每次执行任务前，必须先截图分析当前屏幕状态，再决定下一步操作。**

---

## 执行流程

### 阶段 0：视觉检测（必须首先执行）

在执行任何自动化操作之前：

1. **截图当前屏幕**
   - 使用 `screenshot` 捕获整个屏幕
   - 保存到 `artifacts/<execution_id>/phase_0_before.png`

2. **视觉分析**
   - 使用多模态模型分析截图内容
   - 识别当前页面类型（商品管理页/发布页/列表页/其他）
   - 识别关键UI元素位置
   - 输出结构化分析报告

3. **决策输出**
   ```
   ## 阶段0：视觉检测报告
   
   **页面类型**: [商品管理列表页/产品发布页/其他]
   **当前状态**: [已打开京麦/未检测到/需登录]
   **关键元素**:
     - 菜单入口: (x, y)
     - 输入框: (x, y)
     - 按钮: (x, y)
   **操作建议**: [直接继续/需要先打开京麦/需要登录]
   ```

### 阶段 1：任务理解

1. 解析商品数据（从 `product_data/product_1.json` 读取）
2. 确认商品名称、品牌、规格、价格等关键字段
3. 核对京东链接有效性

### 阶段 2：UI导航

根据阶段0的视觉分析结果：

1. **如果京麦未打开**
   - 找到Windows开始菜单或快捷方式
   - 启动京麦应用
   - 等待应用完全加载

2. **如果京麦已打开**
   - 定位到产品发布/上架入口
   - 点击进入商品发布页面

### 阶段 3：表单填写

**类目选择操作步骤（必须严格遵守）：**
1. 在类目搜索/输入框中 **输入** 类目关键词"插座"（使用 type 操作）
2. 等待搜索结果或下拉列表出现
3. 从搜索结果中 **点击** 匹配的类目选项
4. 点击确认/下一步按钮

**类目关键词来自 product_data 中的"类目关键词"字段，当前为：插座**

按照商品数据依次填写：

| 字段 | 值 | 说明 |
|------|-----|------|
| 类目关键词 | 插座 | 类目选择页面必须选择此关键词对应的类目 |
| 商品名称 | 公牛（BULL） 插座/B5系列... | 从product_data读取 |
| 品牌 | 公牛 | |
| 型号 | 无 | |
| 长度 | 250 | mm |
| 宽度 | 76 | mm |
| 高度 | 29 | mm |
| 重量 | 0.5 | KG |
| 单位 | 个 | |
| 京东挂网价 | 70 | 元 |
| 京东链接 | https://item.jd.com/16793098028.html | |
| 备注 | 数量：2 | |

**每填写一个字段后进行截图确认**

### 阶段 4：图片上传

1. 上传产品图片（5张主图 + 1张透明图）
2. 检查图片是否上传成功

### 阶段 5：提交确认

1. 检查所有必填项是否已填写
2. 点击提交/确认按钮
3. 截图确认提交结果

---

## 输出资产

- `artifacts/<execution_id>/phase_trace.json`
- `artifacts/<execution_id>/runtime_result.json`
- `artifacts/<execution_id>/stdout.log`
- `artifacts/<execution_id>/stderr.log`
- `artifacts/<execution_id>/phase_0_before.png` （阶段0截图）

## 轨迹字段

- `phase`
- `action`
- `before_screenshot`
- `after_screenshot`
- `result`
- `retry_reason`
- `status`
- `started_at`
- `ended_at`

---

## 商品数据源

商品数据存储在 `product_data/product_1.json`，包含：
- 上架序号
- 申请业务（慧采）
- 商品名称
- 品牌
- 商品型号
- 尺寸（长宽高）
- 重量
- 单位
- 京东挂网价
- 京东链接
- 商品资质
- 商品简述
- 备注
