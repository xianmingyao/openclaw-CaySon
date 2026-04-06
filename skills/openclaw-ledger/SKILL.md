---
name: openclaw-ledger
description: |
  Personal financial tracking skill for OpenClaw.
  Automatically detects expenses and income from conversations and payment screenshots.
  
  Use when:
  - User mentions money/spending (any language)
  - User shares payment screenshots (WeChat Pay, Alipay, etc.)
  - User asks about finances ("How much did I spend?", "My budget")
  - User wants expense reports ("Monthly summary", "Spending analysis")

metadata:
  version: 1.0.0
  author: CaySon
  platform: openclaw

depends:
  - agent-browser (optional, for screenshot OCR)

data_storage:
  ledger_file: E:\workspace\ledger\ledger.yaml
  budget_file: E:\workspace\ledger\budget.yaml
  transactions_file: E:\workspace\ledger\transactions.md

export_to_memory: true
cron_enabled: true
---

# OpenClaw Ledger: Personal Financial Tracking

OpenClaw Ledger automatically extracts financial transactions from your conversations and payment screenshots, providing zero-effort expense tracking.

## Core Capabilities

| Feature | Description |
|---------|-------------|
| **Semantic Expense Detection** | AI identifies spending mentions in natural conversation |
| **Screenshot Recognition** | Extracts transaction data from payment app screenshots |
| **Smart Categorization** | Auto-categorizes based on merchant and context |
| **Budget Tracking** | Monthly budget alerts and progress visualization |
| **Financial Insights** | Pattern analysis for spending habits |
| **Query Support** | Real-time natural language financial inquiries |
| **Daily/Weekly/Monthly Reports** | Automated financial summaries |

## Quick Start

### 1. First Time Setup

```bash
# Create ledger directory
New-Item -Path E:\workspace\ledger -ItemType Directory -Force

# Set your monthly budget (CNY)
# Just tell me: "Set my monthly budget to 5000"
```

### 2. Daily Usage

**Add expenses by conversation:**
- "今天花了150块吃火锅"
- "买了件衣服800"
- "工资到账15000"

**Add expenses by screenshot:**
- Share a WeChat Pay/Alipay payment screenshot
- I'll automatically extract: amount, merchant, category

**Query your finances:**
- "这个月花了多少？"
- "餐饮支出是多少？"
- "还剩多少预算？"

## Data Storage

```
E:\workspace\ledger\
├── ledger.yaml          # Structured transaction data (YAML)
├── budget.yaml          # Budget configuration
├── transactions.md      # Human-readable transaction history
└── reports\            # Generated reports
    ├── daily\          # Daily summaries
    └── monthly\        # Monthly reports
```

## Transaction Schema

```yaml
transactions:
  - id: "20260406_001"
    type: expense              # expense | income | transfer
    amount: 150.00
    currency: CNY
    category: food             # See category list
    category_detail: restaurant
    merchant: "海底捞"
    description: "火锅聚餐"
    timestamp: "2026-04-06T12:30:00+08:00"
    source: conversation       # conversation | screenshot
    confidence: 0.95
    people: ["同事A", "同事B"]  # If shared expense
    notes: "团队午餐"
    
  - id: "20260406_002"
    type: income
    amount: 15000.00
    currency: CNY
    category: income
    description: "4月工资"
    timestamp: "2026-04-05T10:00:00+08:00"
    source: conversation
    confidence: 1.0
```

## Category System

| ID | Name (CN) | Name (EN) | Icon |
|----|-----------|-----------|------|
| food | 餐饮 | Food & Dining | 🍜 |
| transport | 交通 | Transportation | 🚗 |
| shopping | 购物 | Shopping | 🛒 |
| entertainment | 娱乐 | Entertainment | 🎬 |
| utilities | 账单 | Utilities | 📱 |
| housing | 居住 | Housing | 🏠 |
| health | 健康 | Health | 💊 |
| education | 教育 | Education | 📚 |
| personal | 个护 | Personal Care | 💈 |
| subscription | 订阅 | Subscriptions | 🔄 |
| transfer | 转账 | Transfers | 💸 |
| income | 收入 | Income | 💰 |
| other | 其他 | Other | 📦 |

## Supported Payment Platforms

| Platform | Region | Key Indicators |
|----------|--------|----------------|
| WeChat Pay | China | 绿色, "支付成功", ¥XX |
| Alipay | China | 蓝色, "付款成功", ¥XX |
| Apple Pay | Global | Wallet UI, card |
| Bank Apps | Various | Bank logo, transaction confirm |

## Query Examples

| Query (CN) | Query (EN) | Response |
|------------|------------|----------|
| 今天花了多少 | How much did I spend today? | Daily total + breakdown |
| 这周支出了多少 | Weekly expenses? | Weekly summary |
| 本月花费 | Monthly spend | Monthly report |
| 餐饮支出 | Food expenses | Category breakdown |
| 还剩多少预算 | Budget remaining? | Budget status |
| 星巴克消费 | Starbucks transactions | Merchant history |
| 对比上周 | vs last week | Comparison report |

## Budget Configuration

```yaml
budget:
  monthly: 5000.00
  currency: CNY
  categories:
    food: 1500.00      # 30%
    transport: 500.00  # 10%
    shopping: 1000.00  # 20%
    other: 2000.00     # 40%
  alert_threshold: 0.8  # Alert at 80%
```

## Report Templates

### Daily Report
```
## 💰 2026-04-06 财务日报

### 支出
- 🍜 12:30 海底捞火锅: ¥150.00
- 🚗 14:00 滴滴打车: ¥35.00
- 🛒 19:00 淘宝购物: ¥199.00

**今日支出:** ¥384.00
**本月累计:** ¥3,280.00 / ¥5,000.00 (66%)

### 💡 洞察
周末餐饮支出是工作日的3倍
```

### Monthly Report
```
## 💰 2026年4月 财务月报

### 概览
| 项目 | 金额 |
|------|------|
| 总收入 | ¥15,000.00 |
| 总支出 | ¥8,234.00 |
| 结余 | ¥6,766.00 |
| 预算使用 | 165% |

### 分类明细
| 分类 | 金额 | 占比 |
|------|------|------|
| 🍜 餐饮 | ¥2,340 | 28% |
| 🛒 购物 | ¥1,890 | 23% |
| 🚗 交通 | ¥580 | 7% |
| ... | ... | ... |
```

## Integration with OpenClaw

### Trigger Keywords

**Expense Detection:**
- CN: "花了", "买了", "消费", "支出", "付了", "花费", "元", "块"
- EN: "spent", "bought", "paid", "cost", "expense", "$", "¥"

**Income Detection:**
- CN: "到账", "收入", "工资", "奖金", "报销", "收到了"
- EN: "got paid", "income", "salary", "received", "reimbursed"

**Query Keywords:**
- CN: "花了多少", "支出", "预算", "还剩", "统计"
- EN: "how much", "spent", "budget", "total", "expenses"

## Cron Jobs (Optional)

Set up automated reports:

```bash
# Daily summary at 22:00
openclaw cron add \
  --name "Daily expense summary" \
  --cron "0 22 * * *" \
  --tz "Asia/Shanghai" \
  --message "Generate daily expense summary"

# Monthly report at 1st of month 09:00
openclaw cron add \
  --name "Monthly financial report" \
  --cron "0 9 1 * *" \
  --tz "Asia/Shanghai" \
  --message "Generate monthly financial report"
```

## Privacy & Security

- All data stored locally in `E:\workspace\ledger\`
- No cloud upload (unless explicitly configured)
- Screenshots stored locally, paths referenced in ledger
- Sensitive data (full card numbers) masked

## Next Steps

1. Tell me your monthly budget: "Set my budget to 5000"
2. Start sharing expenses naturally!
3. Ask for reports: "本月花了多少？"
