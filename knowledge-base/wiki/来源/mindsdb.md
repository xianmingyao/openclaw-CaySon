# MindsDB - AI分析查询引擎

> 2026-04-03 | 来源：抖音@骋风算力

---

## 一句话

**MindsDB = 用SQL查询AI，一条SQL查遍200+数据源，AI直接给你答案**

---

## 项目信息

| 项目 | 信息 |
|------|------|
| **定位** | AI分析查询引擎 |
| **特点** | 一条SQL查遍所有数据源 |
| **数据源** | 200+ 实时数据源 |
| **安装** | Docker / PyPI |
| **官网** | mindsdb.com |
| **开源** | 是 |

---

## 核心功能

```
连接(Connect) → 统一(Unify) → 响应(Respond)
```

| 阶段 | 功能 |
|------|------|
| **连接** | 200+数据源联合访问 |
| **统一** | 结构化表格 + 矢量化知识库融合 |
| **响应** | 自主推理，AI生成答案 |

### 支持的数据源

| 类型 | 示例 |
|------|------|
| 数据库 | PostgreSQL、MongoDB、MySQL |
| SaaS | Slack、Salesforce |
| 文件 | CSV、JSON、PDF、HTML |
| 云 | BigQuery、Snowflake |

---

## 安装部署

### 方式1: Docker Desktop（推荐，3分钟）

```bash
# 下载安装 Docker Desktop
# https://www.docker.com/products/docker-desktop/

# 运行MindsDB
docker run --name mindsdb_container \
  -e MINDSDB_APIS=http,mysql \
  -p 47334:47334 \
  mindsdb/mindsdb
```

### 方式2: Docker Compose（生产环境）

```bash
# 创建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  mindsdb:
    image: mindsdb/mindsdb
    ports:
      - "47334:47334"
    volumes:
      - ./data:/var/lib/mindsdb
EOF

# 启动
docker-compose up -d
```

### 方式3: PyPI（开发环境）

```bash
# 安装
pip install mindsdb

# 启动
python -m mindsdb
```

### 方式4: 云端试用（最快）

```bash
# 免费云端体验
# 访问 https://cloud.mindsdb.com
# 注册即可使用，无需安装
```

---

## 使用演示

### 1. 连接数据源

```sql
-- 连接 PostgreSQL
CREATE DATABASE my_postgres
WITH ENGINE = 'postgres',
PARAMETERS = {
    "host": "localhost",
    "port": "5432",
    "database": "sales",
    "user": "admin",
    "password": "password"
};

-- 连接 MongoDB
CREATE DATABASE my_mongodb
WITH ENGINE = 'mongodb',
PARAMETERS = {
    "host": "localhost",
    "port": "27017",
    "database": "inventory"
};
```

### 2. SQL统一查询

```sql
-- 一条SQL查遍所有数据源
SELECT p.name, o.amount, i.stock
FROM my_postgres.products AS p
JOIN my_mongodb.orders AS o ON p.id = o.product_id
JOIN my_postgres.inventory AS i ON p.id = i.product_id
WHERE o.amount > 100
ORDER BY o.amount DESC;
```

### 3. AI问答（预测）

```sql
-- 创建AI模型
CREATE MODEL sales_forecast
FROM my_postgres.sales
PREDICT amount;

-- 用AI预测
SELECT name, amount, sales_forecast
FROM sales_forecast
WHERE date > '2026-01-01';
```

### 4. AI生成SQL

```sql
-- 用自然语言问AI
ASK AI "哪些产品销量最高？" ;
-- AI自动生成SQL并执行
```

---

## OpenClaw 集成

### 连接MindsDB作为数据源

```python
# OpenClaw Skill中使用MindsDB
import mindsdb

# 连接MindsDB
mdb = mindsdb.connect("http://localhost:47334")

# 查询数据
result = mdb.query("""
    SELECT * FROM my_postgres.customers
    WHERE prediction = 'high_value'
""")
```

### OpenClaw RAG知识库方案

```
┌─────────────────────────────────────┐
│                                     │
│  OpenClaw (调度中心)               │
│                                     │
│  ┌─────────┐  ┌─────────────────┐│
│  │MindsDB  │  │  Atomic Chat    ││
│  │(结构化) │  │  (非结构化)     ││
│  └────┬────┘  └────────┬────────┘│
│       │                  │          │
│       ↓                  ↓          │
│  ┌─────────────────────────────────┐│
│  │     统一查询层 (SQL)            ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

---

## 演示案例：销售分析

### 场景
```
一家公司有：
- PostgreSQL: 客户和产品数据
- MongoDB: 订单和反馈
- Slack: 客服对话

目标：用AI分析哪个产品需要优先补货
```

### 步骤

```sql
-- 1. 连接所有数据源
CREATE DATABASE pg_db FROM postgres ...;
CREATE DATABASE mongo_db FROM mongodb ...;
CREATE DATABASE slack_db FROM slack ...;

-- 2. 统一查询
SELECT p.name, COUNT(o.id) as order_count, AVG(s.satisfaction) as avg_sat
FROM pg_db.products p
JOIN mongo_db.orders o ON p.id = o.product_id
JOIN slack_db.feedback s ON p.id = s.product_id
GROUP BY p.name
ORDER BY order_count DESC;

-- 3. AI预测补货
CREATE MODEL restock_priority
FROM pg_db.products
PREDICT stock_level;

-- 4. AI给出建议
ASK AI "根据分析结果，哪些产品需要优先补货？"
```

---

## 优缺点

| ✅ 优点 | ❌ 缺点 |
|---------|---------|
| SQL统一查询，门槛低 | 复杂查询性能可能下降 |
| 200+数据源支持 | 需要数据库基础知识 |
| AI原生，预测简单 | 部分数据源连接器需配置 |
| 开源免费 | Docker占用资源 |
| 云端可用 | |

---

## 使用场景

| 场景 | 说明 |
|------|------|
| **跨库查询** | 一个SQL查多个数据库 |
| **AI预测** | SQL直接调用AI模型 |
| **数据整合** | 统一所有数据源 |
| **自动化报表** | AI生成分析报告 |
| **RAG知识库** | 结构化+非结构化融合 |

---

## 记住这个

```
MindsDB = AI分析查询引擎
     ↓
一条SQL查遍 200+ 数据源
     ↓
连接 → 统一 → 响应
     ↓
OpenClaw + MindsDB = 数据+AI双剑合璧
```

---

## 文档

- `knowledge/mindsdb.md` - 本文档
- `knowledge/openclaw-knowledge-system.md` - OpenClaw知识库整合

