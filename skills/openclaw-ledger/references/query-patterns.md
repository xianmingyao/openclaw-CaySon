# Real-time Financial Query Patterns

Query patterns and response templates for OpenClaw Ledger financial inquiries.

## Architecture

**Query parsing is handled by OpenClaw agent.** The Ledger skill provides the underlying data structure and templates. The agent interprets user intent and formats responses.

---

## Query Types

### 1. Time Range Queries (`time_range`)

Queries about total spending or income over a specific period.

| Language | Examples |
|----------|----------|
| **Chinese** | "今天花了多少", "这周支出了多少", "本月花费", "最近三天的开销" |
| **English** | "How much did I spend today?", "Total expenses this week", "Monthly spend so far" |

#### Response Template

```markdown
## 💰 {{period_label}} 支出报告

**总支出:** ¥{{total_amount}}

### 分类明细
| 分类 | 金额 | 占比 |
|------|------|------|
{{#each categories}}
| {{icon}} {{name}} | ¥{{amount}} | {{percent}}% |
{{/each}}

{{#if budget_status}}
### 预算状态
- 已使用: ¥{{used}} / ¥{{budget}} ({{percent}}%)
- 剩余: ¥{{remaining}}
{{/if}}
```

---

### 2. Category Queries (`category`)

Queries focused on specific spending categories.

| Language | Examples |
|----------|----------|
| **Chinese** | "在餐饮上花了多少", "这个月打车花了多少", "购物开支" |
| **English** | "How much did I spend on food?", "Transport expenses this month" |

#### Response Template

```markdown
## 🏷️ {{category_name}} - {{period_label}}

**总计:** ¥{{total_amount}}
**交易次数:** {{transaction_count}} 笔

### 最近交易
| 日期 | 描述 | 金额 |
|------|------|------|
{{#each transactions}}
| {{date}} | {{description}} | ¥{{amount}} |
{{/each}}

{{#if top_merchant}}
### 常去商家
1. {{top_merchant}} - ¥{{top_merchant_amount}} ({{merchant_percent}}%)
{{/if}}
```

---

### 3. Merchant Queries (`merchant`)

Queries about specific merchants or service providers.

| Language | Examples |
|----------|----------|
| **Chinese** | "星巴克消费记录", "最近在淘宝花了多少", "京东订单" |
| **English** | "Starbucks transactions", "How much at Amazon?" |

#### Response Template

```markdown
## 🛒 商家: {{merchant_name}}

**总消费:** ¥{{total_amount}}
**交易次数:** {{transaction_count}} 笔
**上次消费:** {{last_visit_date}}

### 消费记录
| 日期 | 金额 | 描述 |
|------|------|------|
{{#each transactions}}
| {{date}} | ¥{{amount}} | {{description}} |
{{/each}}

{{#if average}}
### 统计
- 平均消费: ¥{{average}}
- 最高单笔: ¥{{max}}
- 最近30天: ¥{{last_30_days}}
{{/if}}
```

---

### 4. Budget Queries (`budget`)

Queries regarding current budget status and remaining limits.

| Language | Examples |
|----------|----------|
| **Chinese** | "还剩多少预算", "本月超支了吗", "我的预算情况" |
| **English** | "How much budget is left?", "Am I over budget?" |

#### Response Template

```markdown
## 🎯 预算状态 - {{period_label}}

### 总体预算
| 项目 | 金额 |
|------|------|
| 预算总额 | ¥{{total_budget}} |
| 已使用 | ¥{{used}} |
| 剩余 | ¥{{remaining}} |
| 进度 | {{percent}}% |

{{#if over_budget}}
### ⚠️ 超支警告
已超支 ¥{{over_amount}}！
{{else}}
### ✅ 预算正常
每日可用: ¥{{daily_allowance}}
{{/if}}

{{#if category_budgets}}
### 分类预算
| 分类 | 预算 | 已用 | 状态 |
|------|------|------|------|
{{#each category_budgets}}
| {{icon}} {{name}} | ¥{{budget}} | ¥{{used}} | {{status}} |
{{/each}}
{{/if}}
```

**Status Icons:**
- ✅ 充足 (>50% remaining)
- ⚠️ 紧张 (20-50% remaining)
- 🔴 即将超支 (<20% remaining)
- ❌ 已超支

---

### 5. Comparison Queries (`comparison`)

Comparing spending between periods or categories.

| Language | Examples |
|----------|----------|
| **Chinese** | "上周对比这周", "比起上个月支出如何" |
| **English** | "Compare this week to last week", "vs last month" |

#### Response Template

```markdown
## 📊 对比报告

### {{period_a}} vs {{period_b}}

| 指标 | {{period_a}} | {{period_b}} | 变化 |
|------|--------------|--------------|------|
| 总支出 | ¥{{amount_a}} | ¥{{amount_b}} | {{diff_percent}} |

{{#if decreased}}
### ✅ 支出下降
比上{{period_name}}少 ¥{{diff_amount}} ({{diff_percent}}下降)
{{else}}
### 📈 支出增加
比上{{period_name}}多 ¥{{diff_amount}} ({{diff_percent}}增加)
{{/if}}

### 分类对比
| 分类 | {{period_a}} | {{period_b}} | 变化 |
|------|--------------|--------------|------|
{{#each category_comparison}}
| {{icon}} {{name}} | ¥{{amount_a}} | ¥{{amount_b}} | {{trend}} |
{{/each}}
```

---

### 6. Income Queries (`income`)

Query income/revenue entries.

| Language | Examples |
|----------|----------|
| **Chinese** | "本月收入多少", "工资到账了吗", "总收入" |
| **English** | "Total income this month?", "Any salary received?" |

#### Response Template

```markdown
## 💰 收入报告 - {{period_label}}

**总收入:** ¥{{total_income}}

### 收入来源
| 来源 | 金额 | 日期 |
|------|------|------|
{{#each income_sources}}
| {{source}} | ¥{{amount}} | {{date}} |
{{/each}}

### 与支出对比
- 收入: ¥{{income}}
- 支出: ¥{{expense}}
- 结余: ¥{{net}}
```

---

### 7. Trends Queries (`trends`)

Spending trends and patterns over time.

| Language | Examples |
|----------|----------|
| **Chinese** | "支出趋势", "每月花费对比", "最近趋势" |
| **English** | "Spending trends", "Monthly comparison" |

#### Response Template

```markdown
## 📈 支出趋势

### 月度趋势
| 月份 | 支出 | vs上月 |
|------|------|--------|
{{#each monthly_trends}}
| {{month}} | ¥{{amount}} | {{trend}} |
{{/each}}

### 统计
- 月均支出: ¥{{monthly_average}}
- 最高月份: {{highest_month}} (¥{{highest_amount}})
- 最低月份: {{lowest_month}} (¥{{lowest_amount}})

### 洞察
{{#each insights}}
> {{icon}} {{insight}}
{{/each}}
```

---

## Edge Case Handling

### 1. No Data Found

**Pattern:** "I couldn't find any records for [Category/Merchant] in [Period]."

**Response:**
```markdown
> 🔍 在此期间没有找到相关记录
> - 查询条件: {{query}}
> - 时间范围: {{period}}
> - 金额: ¥0.00
```

### 2. Ambiguous Time Range

**Pattern:** "recently", "a while ago" without specific dates.

**Behavior:** Default to "Last 30 days" and state the assumption.

**Response:**
```markdown
> 🕒 默认显示最近30天数据
> 如需查询其他时间段，请明确说明日期范围
```

### 3. Budget Not Set

**Pattern:** User asks about budget but none is configured.

**Response:**
```markdown
> ⚠️ 尚未设置预算
> 
> 请告诉我你的月度预算金额，例如:
> "设置预算为5000"
```

### 4. First Time User

**Response:**
```markdown
> 👋 看起来这是你第一次使用记账功能！
> 
> 开始使用：
> 1. 设置预算："设置预算为5000"
> 2. 记录支出："今天花了150块吃火锅"
> 3. 查看报告："本月花了多少？"
```

---

## Report Generation Commands

### Daily Report
```
"今天的财务报告"
"生成日报"
"今日支出"
```

### Weekly Report
```
"这周支出报告"
"生成周报"
"本周花费统计"
```

### Monthly Report
```
"这个月花了多少"
"生成月报"
"本月财务总结"
```

### Yearly Report
```
"今年花了多少"
"年度财务报告"
"年度支出总结"
```
