# Merchant to Category Mapping

Auto-categorize transactions based on merchant names and contextual signals.

## Category Hierarchy

### Primary Categories

| Category ID | Display Name (CN) | Display Name (EN) | Icon | Description |
|-------------|------------------|-------------------|------|-------------|
| `food` | 餐饮 | Food & Dining | 🍜 | Restaurants, groceries, delivery |
| `transport` | 交通 | Transportation | 🚗 | Rides, fuel, public transit |
| `shopping` | 购物 | Shopping | 🛒 | Retail, online purchases |
| `entertainment` | 娱乐 | Entertainment | 🎬 | Movies, games, events |
| `utilities` | 账单 | Utilities | 📱 | Phone, internet, electricity |
| `housing` | 居住 | Housing | 🏠 | Rent, property fees |
| `health` | 健康 | Health | 💊 | Medical, pharmacy, fitness |
| `education` | 教育 | Education | 📚 | Courses, books, training |
| `personal` | 个护 | Personal Care | 💈 | Haircuts, beauty, clothing |
| `subscription` | 订阅 | Subscriptions | 🔄 | Digital services, memberships |
| `transfer` | 转账 | Transfers | 💸 | P2P, bank transfers |
| `income` | 收入 | Income | 💰 | Salary, reimbursements |
| `other` | 其他 | Other | 📦 | Uncategorized |

## High-Confidence Mappings

### Food & Dining

```yaml
food:
  exact_match:
    - "星巴克" / "Starbucks"
    - "瑞幸咖啡" / "Luckin Coffee"
    - "麦当劳" / "McDonald's"
    - "肯德基" / "KFC"
    - "海底捞" / "Haidilao"
    - "沙县小吃"
    - "兰州拉面"
    - "黄焖鸡米饭"
    - "美团" / "Meituan" (food delivery)
    - "饿了么" / "Ele.me"
    
  contains:
    - "餐厅" / "Restaurant"
    - "饭店" / "Eatery"
    - "火锅" / "Hotpot"
    - "烧烤" / "BBQ"
    - "咖啡" / "Cafe"
    - "奶茶" / "Milk Tea"
    - "烘焙" / "Bakery"
    - "Pizza"
    - "外卖" / "Delivery"
    - "食堂" / "Cafeteria"
```

### Transportation

```yaml
transport:
  exact_match:
    - "滴滴出行" / "DiDi"
    - "高德打车"
    - "花小猪"
    - "Uber"
    - "Lyft"
    - "12306"
    - "中国铁路"
    - "东方航空" / "China Eastern"
    - "南方航空" / "China Southern"
    - "国航" / "Air China"
    
  contains:
    - "出租" / "Taxi"
    - "地铁" / "Metro"
    - "公交" / "Bus"
    - "加油" / "Gas"
    - "停车" / "Parking"
    - "机票" / "Flight"
    - "火车" / "Train"
```

### Shopping

```yaml
shopping:
  exact_match:
    - "淘宝" / "Taobao"
    - "天猫" / "Tmall"
    - "京东" / "JD.com"
    - "拼多多" / "Pinduoduo"
    - "亚马逊" / "Amazon"
    - "唯品会" / "Vipshop"
    
  contains:
    - "超市" / "Supermarket"
    - "便利店" / "Convenience"
    - "商城" / "Mall"
    - "商店" / "Store"
    - "电器" / "Electronics"
```

### Entertainment

```yaml
entertainment:
  exact_match:
    - "猫眼电影"
    - "淘票票"
    - "大麦网"
    - "爱奇艺" / "iQIYI"
    - "腾讯视频" / "Tencent Video"
    - "优酷" / "Youku"
    - "网易云音乐" / "NetEase Music"
    - "QQ音乐" / "QQ Music"
    - "Spotify"
    - "Netflix"
    
  contains:
    - "电影" / "Cinema"
    - "KTV"
    - "游戏" / "Game"
    - "演出" / "Show"
    - "门票" / "Ticket"
    - "旅游" / "Travel"
```

### Subscriptions

```yaml
subscription:
  exact_match:
    - "Netflix"
    - "Spotify"
    - "Apple" / "iCloud"
    - "Google One"
    - "ChatGPT"
    - "OpenAI"
    - "GitHub"
    - "爱奇艺会员"
    - "腾讯视频会员"
    - "优酷会员"
    - "网易云会员"
    
  contains:
    - "会员" / "Membership"
    - "订阅" / "Subscription"
    - "月费" / "Monthly"
    - "年费" / "Yearly"
    - "Premium"
    - "Plus"
    - "Pro"
```

### Utilities

```yaml
utilities:
  exact_match:
    - "中国移动" / "China Mobile"
    - "中国联通" / "China Unicom"
    - "中国电信" / "China Telecom"
    
  contains:
    - "话费"
    - "网费"
    - "电费"
    - "水费"
    - "燃气费"
```

## Matching Algorithm

### Priority Order

1. **User Custom Rules** (highest priority)
2. **Exact Match** on merchant name
3. **Platform Match** for known services
4. **Contains Match** for keywords
5. **AI Inference** based on context
6. **Default to `other`** if no match

### Matching Process

```python
def categorize(merchant: str, context: str) -> Category:
    # 1. Check user custom rules
    if match := user_rules.match(merchant):
        return match
    
    # 2. Exact match
    if match := exact_mappings.get(normalize(merchant)):
        return match
    
    # 3. Platform match
    for platform, category in platform_mappings.items():
        if platform in merchant:
            return category
    
    # 4. Contains match
    for keyword, category in keyword_mappings.items():
        if keyword in merchant.lower():
            return category
    
    # 5. AI inference
    if context:
        return ai_infer_category(merchant, context)
    
    # 6. Default
    return Category.OTHER
```

## User Custom Rules

Users can add custom mappings:

```yaml
# Stored in budget.yaml
custom_categories:
  "公司食堂": food
  "公司班车": transport
  "物业费": housing
  "健身房": health
```

### Rule Format

```yaml
custom_categories:
  "[Merchant Name]": [category_id]
  
# With regex support
custom_patterns:
  - pattern: ".*健身.*"
    category: health
  - pattern: ".*Gym.*"
    category: health
```

## Ambiguous Cases

### Context-Dependent Categorization

| Merchant | Possible Categories | Resolution |
|----------|---------------------|------------|
| Amazon | shopping, subscription | Check amount pattern |
| 美团 | food, entertainment | Check specific service |
| Apple | shopping, subscription | Check amount (small = sub) |

### Amount-Based Hints

| Amount Pattern | Likely Category |
|----------------|-----------------|
| < ¥10 regular | food (coffee, snacks) |
| ¥10-20 monthly | subscription |
| Round numbers | transfers |

## Category Statistics

Track category usage for personalization:

```yaml
category_stats:
  food:
    count: 45
    total: 3500.00
    average: 77.78
    last_used: "2026-04-06"
```

Use statistics for:
- Suggesting likely categories for ambiguous merchants
- Detecting unusual spending patterns
- Generating insights
