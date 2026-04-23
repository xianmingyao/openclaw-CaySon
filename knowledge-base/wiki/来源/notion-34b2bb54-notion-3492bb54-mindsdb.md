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

连接(Connect) → 统一(Unify) → 响应(Respond)

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

# 下载安装 Docker Desktop

# https://www.docker.com/products/docker-desktop/

# 运行MindsDB

docker run --name mindsdb_container \

-e MINDSDB_APIS=http,mysql \

-p 47334:47334 \

mindsdb/mindsdb

### 方式2: Docker Compose（生产环境）

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

### 方式3: PyPI（开发环境）

# 安装

pip install mindsdb

# 启动

python -m mindsdb

### 方式4: 云端试用（最快）

# 免费云端体验

# 访问 https://cloud.mindsdb.com

# 注册即可使用，无需安装

---

## 使用演示

### 1. 连接数据源

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

### 2. SQL统一查询

-- 一条SQL查遍所有数据源

SELECT p.name, o.amount, i.stock

FROM my_postgres.products AS p

JOIN my_mongodb.orders AS o ON p.id = o.product_id

JOIN my_postgres.inventory AS i ON p.id = i.product_id

WHERE o.amount > 100

ORDER BY o.amount DESC;

### 3. AI问答（预测）

-- 创建AI模型

CREATE MODEL sales_forecast

FROM my_postgres.sales

PREDICT amount;

-- 用AI预测

SELECT name, amount, sales_forecast

FROM sales_forecast