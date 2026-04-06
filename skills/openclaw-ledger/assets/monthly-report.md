# Monthly Finance Report Template

Template for OpenClaw Ledger monthly financial summaries.

## Monthly Report Structure

```markdown
---
type: monthly-finance
period: {{PERIOD}}
total_income: {{TOTAL_INCOME}}
total_expense: {{TOTAL_EXPENSE}}
net: {{NET}}
budget: {{BUDGET}}
currency: CNY
generated: {{GENERATED_DATE}}
---

# 💰 {{PERIOD_DISPLAY}} 财务月报

## 📊 月度概览

| 指标 | 金额 |
|------|------|
| 总收入 | ¥{{total_income}} |
| 总支出 | ¥{{total_expense}} |
| **净收支** | **¥{{net}}** |
| 预算使用 | {{budget_percent}}% |

{{#if budget_status}}
{{budget_status}}
{{/if}}

## 📈 支出分类明细

### By Category

| 分类 | 金额 | 占比 | vs 上月 |
|------|------|------|---------|
{{#each categories}}
| {{icon}} {{name}} | ¥{{amount}} | {{percent}}% | {{trend}} |
{{/each}}

### 可视化

```
{{category_chart}}
```

## 📅 日支出分布

| 周 | 周一 | 周二 | 周三 | 周四 | 周五 | 周六 | 周日 | 合计 |
|------|------|------|------|------|------|------|------|------|
{{#each weekly_data}}
| {{week}} | {{mon}} | {{tue}} | {{wed}} | {{thu}} | {{fri}} | {{sat}} | {{sun}} | ¥{{total}} |
{{/each}}

**日均:** ¥{{daily_average}}
**最高日:** {{highest_day}} (¥{{highest_amount}})
**零支出天数:** {{no_spend_days}} 天

## 💳 大额支出

### Top 5 支出

| 日期 | 描述 | 分类 | 金额 |
|------|------|------|------|
{{#each top_expenses}}
| {{date}} | {{description}} | {{category}} | ¥{{amount}} |
{{/each}}

### 收入记录

| 日期 | 来源 | 金额 |
|------|------|------|
{{#each income_entries}}
| {{date}} | {{source}} | +¥{{amount}} |
{{/each}}

## 🔄 固定支出

| 项目 | 频率 | 金额 | 月均 |
|------|------|------|------|
{{#each recurring}}
| {{name}} | {{frequency}} | ¥{{amount}} | ¥{{monthly}} |
{{/each}}

**固定支出合计:** ¥{{recurring_total}}/月

## 📊 月度对比

### vs 上月

| 指标 | 本月 | 上月 | 变化 |
|------|------|------|------|
| 总支出 | ¥{{current_expense}} | ¥{{last_expense}} | {{expense_change}} |
| 餐饮 | ¥{{current_food}} | ¥{{last_food}} | {{food_change}} |
| 购物 | ¥{{current_shopping}} | ¥{{last_shopping}} | {{shopping_change}} |

### vs 年均

- **月度平均:** ¥{{monthly_average}}
- **最高月份:** {{highest_month}} (¥{{highest_amount}})
- **最低月份:** {{lowest_month}} (¥{{lowest_amount}})

## 🎯 预算执行

### 分类预算

| 分类 | 预算 | 实际 | 状态 |
|------|------|------|------|
{{#each budget_performance}}
| {{icon}} {{name}} | ¥{{budget}} | ¥{{actual}} | {{status}} |
{{/each}}

### 预算建议

{{#each recommendations}}
- {{content}}
{{/each}}

## 💡 财务洞察

{{#each insights}}
> [!{{type}}] {{title}}
> {{content}}

{{/each}}

## 📎 附件

- **收据数量:** {{receipt_count}} 张
- **数据文件:** [[ledger.yaml|查看原始数据]]

---

*由 OpenClaw Ledger 自动生成 💰*
*报告日期: {{generated_date}}*
```

## Example Output

```markdown
---
type: monthly-finance
period: 2026-04
total_income: 15000.00
total_expense: 8234.00
net: 6766.00
budget: 5000.00
currency: CNY
generated: 2026-04-30
---

# 💰 2026年4月 财务月报

## 📊 月度概览

| 指标 | 金额 |
|------|------|
| 总收入 | ¥15,000.00 |
| 总支出 | ¥8,234.00 |
| **净收支** | **¥6,766.00** |
| 预算使用 | 165% |

> ⚠️ 预算超支 ¥3,234.00

## 📈 支出分类明细

### By Category

| 分类 | 金额 | 占比 | vs 上月 |
|------|------|------|---------|
| 🍜 餐饮 | ¥2,340 | 28% | ↑15% |
| 🛒 购物 | ¥1,890 | 23% | ↓8% |
| 🚗 交通 | ¥580 | 7% | → |
| 🎬 娱乐 | ¥450 | 5% | ↑25% |
| 🔄 订阅 | ¥200 | 2% | → |
| 📦 其他 | ¥2,774 | 34% | ↑5% |

## 📅 日支出分布

| 周 | 周一 | 周二 | 周三 | 周四 | 周五 | 周六 | 周日 | 合计 |
|------|------|------|------|------|------|------|------|------|
| W1 | ¥120 | ¥85 | ¥0 | ¥340 | ¥210 | ¥450 | ¥180 | ¥1,385 |
| W2 | ¥95 | ¥0 | ¥156 | ¥280 | ¥95 | ¥320 | ¥0 | ¥946 |
| W3 | ¥180 | ¥420 | ¥0 | ¥95 | ¥560 | ¥890 | ¥245 | ¥2,390 |
| W4 | ¥75 | ¥150 | ¥320 | ¥0 | ¥680 | ¥1,280 | ¥108 | ¥2,613 |

**日均:** ¥274.47
**最高日:** 周六 (¥890)
**零支出天数:** 4 天

## 💡 财务洞察

> [!insight] 周末效应
> 周末支出是工作日的2.3倍

> [!warning] 预算超支
> 本月支出超出预算¥3,234，建议控制非必要消费

> [!tip] 优化建议
> 考虑设置分类预算，避免超支

---

*由 OpenClaw Ledger 自动生成 💰*
*报告日期: 2026-04-30*
```

## Report Generation Commands

Generate monthly report via command:
```
"生成4月财务报告"
"本月支出报告"
"月报"
```

## Budget Alert Thresholds

| Threshold | Alert Level | Message |
|-----------|-------------|---------|
| 80% | ⚠️ 注意 | 预算已使用80% |
| 100% | 🔴 超支 | 已超预算 |
| 120% | 🚨 严重超支 | 大幅超出预算，需立即控制 |
