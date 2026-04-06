# Daily Finance Report Template

Template for OpenClaw Ledger daily financial summaries.

## Daily Report Structure

```markdown
# 💰 {{DATE}} 财务日报

## 📊 今日概览

| 指标 | 金额 |
|------|------|
| 支出 | ¥{{daily_expense}} |
| 收入 | ¥{{daily_income}} |
| 净收支 | ¥{{daily_net}} |

## 📝 交易明细

{{#if transactions}}
| 时间 | 类型 | 描述 | 分类 | 金额 |
|------|------|------|------|------|
{{#each transactions}}
| {{time}} | {{type_icon}} | {{description}} | {{category_icon}} {{category}} | ¥{{amount}} |
{{/each}}
{{else}}
*今日无交易记录* ✨
{{/if}}

## 🏷️ 分类支出

{{#if category_breakdown}}
| 分类 | 金额 | 占比 | 趋势 |
|------|------|------|------|
{{#each category_breakdown}}
| {{icon}} {{name}} | ¥{{amount}} | {{percent}}% | {{trend}} |
{{/each}}
{{else}}
*无支出*
{{/if}}

## 🎯 预算状态

| 项目 | 金额 |
|------|------|
| 本月预算 | ¥{{monthly_budget}} |
| 本月已用 | ¥{{monthly_used}} |
| 本月剩余 | ¥{{monthly_remaining}} |
| 进度 | {{budget_percent}}% |

{{#if budget_alert}}
> ⚠️ {{budget_alert}}
{{/if}}

## 💡 今日洞察

{{#if insights}}
{{#each insights}}
> {{icon}} {{insight}}
{{/each}}
{{else}}
> 💡 今日支出正常，保持良好习惯！
{{/if}}

---

*由 OpenClaw Ledger 自动生成*
*生成时间: {{generated_at}}*
```

## Example Output

### Normal Day with Expenses

```markdown
# 💰 2026-04-06 财务日报

## 📊 今日概览

| 指标 | 金额 |
|------|------|
| 支出 | ¥384.00 |
| 收入 | ¥0.00 |
| 净收支 | -¥384.00 |

## 📝 交易明细

| 时间 | 类型 | 描述 | 分类 | 金额 |
|------|------|------|------|------|
| 12:35 | 🍜 | 海底捞火锅 | 餐饮 | ¥158.00 |
| 14:20 | 🚗 | 滴滴出行 | 交通 | ¥35.00 |
| 19:45 | 🛒 | 淘宝购物 | 购物 | ¥191.00 |

## 🏷️ 分类支出

| 分类 | 金额 | 占比 | 趋势 |
|------|------|------|------|
| 🍜 餐饮 | ¥158.00 | 41% | ↑ |
| 🛒 购物 | ¥191.00 | 50% | ↑ |
| 🚗 交通 | ¥35.00 | 9% | ↓ |

## 🎯 预算状态

| 项目 | 金额 |
|------|------|
| 本月预算 | ¥5,000.00 |
| 本月已用 | ¥3,280.00 |
| 本月剩余 | ¥1,720.00 |
| 进度 | 66% |

## 💡 今日洞察

> 💡 餐饮支出占比偏高，建议减少外卖次数
> 💡 本月预算进度正常，剩余 ¥1,720

---

*由 OpenClaw Ledger 自动生成*
*生成时间: 2026-04-06 22:00:00*
```

### No Spending Day

```markdown
# 💰 2026-04-07 财务日报

## 📊 今日概览

| 指标 | 金额 |
|------|------|
| 支出 | ¥0.00 |
| 收入 | ¥0.00 |
| 净收支 | ¥0.00 |

## 📝 交易明细

*今日无交易记录* ✨

## 🎯 预算状态

| 项目 | 金额 |
|------|------|
| 本月预算 | ¥5,000.00 |
| 本月已用 | ¥3,280.00 |
| 本月剩余 | ¥1,720.00 |
| 进度 | 66% |

## 💡 今日洞察

> 🎉 连续第2天无支出！
> 💡 本月预算进度正常，剩余 ¥1,720

---

*由 OpenClaw Ledger 自动生成*
*生成时间: 2026-04-07 22:00:00*
```

### Income Day

```markdown
# 💰 2026-04-05 财务日报

## 📊 今日概览

| 指标 | 金额 |
|------|------|
| 支出 | ¥280.00 |
| 收入 | ¥15,000.00 |
| 净收支 | +¥14,720.00 |

## 📝 交易明细

| 时间 | 类型 | 描述 | 分类 | 金额 |
|------|------|------|------|------|
| 10:00 | 💰 | 4月工资 | 收入 | +¥15,000.00 |
| 12:30 | 🍜 | 庆祝午餐 | 餐饮 | -¥180.00 |
| 15:00 | 🛒 | 买菜 | 购物 | -¥100.00 |

## 💡 今日洞察

> 💰 工资到账，本月财务状况良好
> 🎉 本月结余: ¥14,720

---

*由 OpenClaw Ledger 自动生成*
*生成时间: 2026-04-05 22:00:00*
```

## Conditional Sections

### Show Section If

- **交易明细**: Any transactions exist
- **分类支出**: More than 0 expenses
- **预算警告**: Budget used > 80%
- **洞察**: Any insights available

### Hide Section If

- No financial activity → Show "No spending day" message
- Budget not set → Hide budget section

## Usage

Generate daily report via command:
```
"生成今日财务报告"
"今天的支出报告"
"日报"
```
