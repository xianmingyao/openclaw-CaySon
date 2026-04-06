# Payment Screenshot Recognition

Extract transaction data from payment app screenshots using OCR and visual detection.

## Supported Platforms

| Platform | Region | Visual Identifiers |
|----------|--------|-------------------|
| **WeChat Pay** | China | 绿色/#07C160, "支付成功", ¥XX |
| **Alipay** | China | 蓝色/#1677FF, "付款成功", ¥XX |
| **Apple Pay** | Global | Wallet app UI, card imagery |
| **Google Pay** | Global | Google Pay branding, checkmark |
| **Bank Apps** | Various | Bank logos, transaction confirmations |
| **UnionPay** | China | UnionPay logo, "交易成功" |
| **PayPal** | Global | PayPal logo, confirmation screen |

## Detection Workflow

```
Screenshot Received
        │
        ▼
┌─────────────────────────────────┐
│   Step 1: Platform Detection    │
│   Identify payment app/service   │
└─────────────────────────────────┘
        │
        ├── Unknown → Ask user for manual entry
        │
        ▼
┌─────────────────────────────────┐
│   Step 2: OCR + Data Extraction │
│   Amount, merchant, timestamp    │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│   Step 3: Validation            │
│   Confidence check, dedup       │
└─────────────────────────────────┘
        │
        ├── High Confidence → Auto-record
        │
        └── Low Confidence  → Ask user to confirm
```

## Visual Detection Criteria

### WeChat Pay (微信支付)

| Element | Expected |
|---------|----------|
| Color Scheme | 绿色 primary (#07C160) |
| Success Icon | 绿色对勾 |
| Key Text | "支付成功", "已支付", "付款成功" |
| Amount | 大号居中, ¥XX.XX 格式 |
| Merchant | 金额下方, 较小文字 |
| Timestamp | "支付时间" + datetime |
| Order ID | "订单号" or "商户单号" |

### Alipay (支付宝)

| Element | Expected |
|---------|----------|
| Color Scheme | 蓝色 primary (#1677FF) |
| Success Icon | 蓝色对勾 or 动画勾 |
| Key Text | "付款成功", "交易成功" |
| Amount | 大号居中 |
| Merchant | 商家名称突出显示 |
| Payment Method | 卡/余额指示器 |

### Generic Bank Apps

| Element | Expected |
|---------|----------|
| Bank Logo | Bank branding |
| Transaction Type | "转账成功", "Transfer Complete" |
| Amount | Currency symbol + amount |
| Recipient/Merchant | Account info or name |
| Reference Number | Transaction ID |

## Data Extraction Schema

```yaml
payment_screenshot:
  # Required fields
  platform: wechat|alipay|apple_pay|google_pay|bank|unionpay|paypal|unknown
  type: expense|income|transfer
  amount: float
  currency: string
  
  # Common fields
  merchant: string           # Merchant/recipient name
  timestamp: ISO8601         # Transaction time from screenshot
  category_hint: string      # AI-inferred category
  
  # Optional fields
  order_id: string          # Order/transaction number
  payment_method: string    # Card, balance, etc.
  original_amount: float     # Pre-discount amount
  discount: float           # Discount/coupon amount
  
  # Metadata
  confidence: float         # 0-1 extraction confidence
  screenshot_path: string    # Path to stored image
  needs_review: boolean     # Flag for low confidence
```

## OCR Best Practices

### Pre-processing (via agent-browser or external tool)

1. **Enhance Contrast**: Improve text readability
2. **Correct Orientation**: Ensure upright
3. **Crop to Content**: Remove unnecessary margins

### Extraction Priority

Extract fields in this order (most reliable first):

1. **Amount**: Usually largest, most prominent text
2. **Platform**: Logo/branding detection
3. **Merchant**: Secondary text near amount
4. **Timestamp**: Standardized format
5. **Other Details**: Payment method, order ID

## Confidence Scoring

| Score | Criteria | Action |
|-------|----------|--------|
| **≥0.9** | All key fields extracted, platform identified | Auto-record |
| **0.7-0.9** | Amount + merchant extracted, some uncertainty | Auto-record, flag for review |
| **0.5-0.7** | Partial extraction, likely payment screenshot | Store, ask for confirmation |
| **<0.5** | Uncertain if payment screenshot | Treat as regular photo |

### Confidence Factors

| Factor | Weight | Notes |
|--------|--------|-------|
| Platform identified | +0.2 | Known UI patterns |
| Amount extracted | +0.3 | Most critical field |
| Merchant extracted | +0.2 | Important for categorization |
| Timestamp found | +0.1 | Helps with deduplication |
| Order ID found | +0.1 | Confirms transaction record |
| Success indicator | +0.1 | Confirms completed payment |

## Deduplication

Prevent recording the same transaction multiple times:

### Match Criteria

Two records are considered duplicates if:

```
same_amount AND
same_merchant (fuzzy match) AND
timestamp_diff < 30 minutes
```

### Resolution Strategy

1. **Screenshot Priority**: Screenshot data is more accurate than conversation
2. **Merge Context**: Combine conversation description with screenshot details
3. **Keep Latest**: If multiple screenshots, keep the most detailed one

## Storage

### Screenshot Files

```
E:\workspace\ledger\receipts\
├── 2026-04-06\
│   ├── receipt_001.jpg      # WeChat Pay
│   ├── receipt_001.json     # Extracted metadata
│   └── receipt_002.jpg     # Alipay
```

### Naming Convention

- Format: `receipt_XXX.{ext}`
- Date-based subdirectories
- Preserve original extension (jpg, png, heic)

## Privacy Considerations

### What to Mask

- Full bank account numbers → keep only last 4 digits
- Personal ID numbers
- Detailed recipient information (for transfers)

### What to Store

- Transaction amount
- Merchant name (not full account)
- Timestamp
- Category
- Order ID (if visible)

## Example Extraction

### WeChat Pay Screenshot

```
Input: [WeChat Pay payment screenshot]
Output:
{
  "platform": "wechat",
  "type": "expense",
  "amount": 158.00,
  "currency": "CNY",
  "merchant": "海底捞火锅",
  "timestamp": "2026-04-06T12:35:00+08:00",
  "category_hint": "food",
  "confidence": 0.95,
  "order_id": "WX2026040612350000"
}
```

### Alipay Screenshot

```
Input: [Alipay payment screenshot]
Output:
{
  "platform": "alipay",
  "type": "expense",
  "amount": 35.00,
  "currency": "CNY",
  "merchant": "滴滴出行",
  "timestamp": "2026-04-06T09:15:00+08:00",
  "category_hint": "transport",
  "confidence": 0.92,
  "payment_method": "余额宝"
}
```

## Integration with Expense Detection

When both conversation and screenshot mention the same transaction:

1. **Screenshot takes priority** (more accurate data)
2. **Deduplicate** using amount + time window
3. **Merge context** from both sources
4. **Single record** with combined confidence
