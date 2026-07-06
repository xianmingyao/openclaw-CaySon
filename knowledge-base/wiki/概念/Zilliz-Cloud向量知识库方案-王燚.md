# Zilliz Cloud 向量知识库方案与使用指南

> 来源：星触达内部文档（王燚，2026-05-11）
> 文档版本：V1.0
> 定位：企业内部AI知识库落地实践

---

## 1. 🎯 这是什么（简介）

**Zilliz Cloud向量知识库**是一套完整的企业级语义搜索解决方案，通过向量数据库实现：
- 跨系统的语义检索
- Claude Code/Codex的主动知识查询
- 客户品牌知识的RAG注入
- 监控问题的语义去重

**一句话理解**：把散落的文档变成AI能"理解"的向量，让检索从"找关键词"升级到"找意思"。

---

## 2. 📝 关键功能点

### 2.1 解决的三个核心问题

| 问题 | 表现 | 解决 |
|------|------|------|
| **客户知识散落** | 坚果云+飞书的品牌资料无法被机器检索 | 统一入库向量语义检索 |
| **Claude Code信息割裂** | CC/Codex看不到Claude.ai的40+份架构文档 | MCP Server主动查询 |
| **元语义问题去重靠人工** | "西装价格"和"套装多少钱"无法匹配 | 向量相似度自动去重 |

### 2.2 向量数据库 vs 传统数据库

```
传统数据库（PostgreSQL）：
  搜"西装价格" → 只能找到包含"西装"和"价格"的记录
  找不到"商务套装多少钱"（用词不同）

向量数据库（Zilliz）：
  搜"西装价格" → 找到所有语义相近的记录
  能找到"商务套装多少钱"、"Bostinen suit price"、"西装价位区间"
  因为它比的是文字背后的"含义"
```

### 2.3 三Collection架构

```
Zilliz Cloud（geo-knowledge Cluster）
│
├── Collection: internal_kb ← 企业内部知识库
│ ├── 存：架构文档、Schema设计、API规范、开发流程
│ ├── 权限：按角色过滤（developer/tech_lead/delivery/business/all）
│ └── 用途：CC/Codex通过MCP按需查询
│
├── Collection: client_kb_{client_id} ← 客户品牌知识库
│ ├── 存：品牌信息、产品资料、行业报告、AI高分段落
│ ├── 权限：只有对应客户的服务团队
│ └── 用途：内容生成时RAG注入品牌知识
│
└── Collection: meta_questions ← 语义问题库
  ├── 存：所有客户的监控问题+向量
  └── 用途：语义去重+问题推荐+跨客户分析
```

---

## 3. ⚡ 怎么使用

### 3.1 写入流程

```
一篇文档
  ↓
分段（chunking）：拆成200-500字段落
  ↓
Embedding：文字→1024维向量
  ↓
写入Zilliz：内容+向量+来源+权限标记+更新时间
  ↓
建索引，可搜索
```

### 3.2 查询流程

```
用户/CC提问 → MCP Server → 问题转向量
  ↓
Zilliz搜索 → 自动权限过滤 → 返回Top5结果
  ↓
CC基于准确信息开发/回答
```

### 3.3 MCP Server架构

```
CC / Codex / 内容生成平台
    ↓
GEO Knowledge MCP Server
 ├── 认证：API Key → 识别角色
 ├── 查询：Embedding → 搜索Zilliz → 过滤权限 → 返回
 └── 写入：文档 → chunking → Embedding → 存入Zilliz
    ↓
Zilliz Cloud（语义搜索） ←→ PostgreSQL（业务数据）
```

---

## 4. ✅ 优点

- **Serverless按需计费**：空闲不收计算费，只付存储
- **免费额度**：5GB免费，三个场景起步够用
- **托管服务**：不用运维，省人力
- **官方MCP Server**：直接对接Claude Code/Codex
- **多租户隔离**：每个客户知识库完全隔离
- **权限精细**：字段级access_levels过滤

---

## 5. ❌ 缺点

- **依赖外部服务**：Zilliz Cloud是SaaS，有vendor lock-in风险
- **Embedding成本**：大规模文档处理有成本
- **分词策略影响大**：chunking方式直接影响召回效果
- **增量同步复杂**：需要维护与PG的数据同步

---

## 6. 🎬 使用场景

### 场景1：Claude Code开发辅助
```
问题：CC开发时不知道Schema设计、API规范
解决：CC通过MCP Server主动查询internal_kb
效果：基于准确信息开发，不凭猜测
```

### 场景2：内容生成平台RAG
```
流程：生成文章前 → 检索客户知识库 → 自动融入品牌知识
效果：生成内容贴合品牌调性
```

### 场景3：监控问题语义去重
```
问题：1千~1万个监控问题，语义相同文字不同
解决：向量相似度>0.85自动合并同一组
效果：减少人工去重工作量
```

---

## 7. 🔧 运行依赖环境

| 组件 | 选型 | 说明 |
|------|------|------|
| 向量数据库 | Zilliz Cloud Serverless | geo-knowledge Cluster |
| Embedding模型 | 豆包Embedding（火山引擎Ark） | 1024维，和LLM调用统一 |
| MCP Server | 自建Python | 定制权限过滤、多Collection路由 |
| 文档分段 | 自建chunker | 复用L2归因的paragraph_splitter |
| 主数据库 | PostgreSQL RDS | 业务数据不动，Zilliz只做语义搜索 |

---

## 8. 🚀 部署使用注意点

### 8.1 四层结构（类比）

```
Organization（组织）= 办公室
 └── Project（项目）= 房间
 └── Cluster（集群）= 文件柜
 └── Collection（集合）= 抽屉
 └── Entity（实体）= 卡片（内容+向量+元数据）
```

### 8.2 分级权限设计

| 角色 | 能查内容 |
|------|---------|
| `all` | 所有文档 |
| `tech_lead` | 技术架构+Schema+API+部署+爬虫 |
| `developer` | 技术架构+Schema+API规范+开发流程+踩坑记录 |
| `delivery` | 客户平台规范+运营平台规范+API文档 |
| `business` | 产品介绍+案例+价格体系+竞品分析+CRM |

### 8.3 Collection Schema

**internal_kb**：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT64 | 自增主键 |
| content | VARCHAR | 知识内容 |
| embedding | FLOAT_VECTOR | 向量 |
| source_doc | VARCHAR | 来源文档名 |
| doc_type | VARCHAR | 文档类型 |
| access_levels | ARRAY | 权限标记 |
| chunk_index | INT32 | 段落序号 |
| updated_at | VARCHAR | 更新时间 |

**client_kb_{id}**：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT64 | 主键 |
| content | VARCHAR | 知识内容 |
| embedding | FLOAT_VECTOR | 向量 |
| knowledge_type | VARCHAR | 类型 |
| source | VARCHAR | 来源 |
| brand_name | VARCHAR | 品牌名 |
| project_id | INT32 | 项目ID |

**meta_questions**：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT64 | 主键 |
| question_text | VARCHAR | 问题文本 |
| embedding | FLOAT_VECTOR | 向量 |
| category | VARCHAR | 类别 |
| client_id | INT32 | 客户ID |
| is_meta | BOOLEAN | 是否元问题 |
| semantic_group_id | INT32 | 语义分组 |

---

## 9. 🕳️ 避坑指南

### 🔴 坑1：Chunksize一刀切
**问题**：所有文档用相同的chunk大小
**解决**：根据文档类型调整（长文档200字，短文档500字）

### 🔴 坑2：权限标记遗漏
**问题**：写入时忘记设置access_levels
**解决**：MCP Server写入时强制检查权限字段

### 🔴 坑3：增量同步遗漏
**问题**：源文档更新后Zilliz未同步
**解决**：Git push触发webhook自动re-embedding

### 🔴 坑4：Embedding模型不一致
**问题**：查询和写入用不同模型
**解决**：统一用豆包Embedding，配置固化

---

## 10. 📊 总结

**学习价值**：⭐⭐⭐⭐⭐（5星）
**推荐指数**：⭐⭐⭐⭐⭐（5星）

### 核心公式
```
向量知识库 = 文档 → Chunking → Embedding → 向量存储 → 语义检索
```

### 一句话总结
> 把散落的文档变成AI能"理解"的向量，让检索从"找关键词"升级到"找意思"。Zilliz Cloud是PG的补充，不是替代。

### 实施四阶段
| 阶段 | 周期 | 目标 |
|------|------|------|
| Phase 1 | 第1-2周 | Zilliz环境+内部知识库MVP+MCP框架 |
| Phase 2 | 第3-4周 | 40+文档全量导入+权限过滤+CC配置 |
| Phase 3 | 第5-6周 | 客户知识库+内容平台RAG对接 |
| Phase 4 | 持续 | 问题去重+数据闭环 |

### docs/目录定位变化
| 信息类型 | 新位置 | 说明 |
|---------|--------|------|
| 页面Spec | 仓库docs/ | 和代码绑定 |
| 数据逻辑 | 仓库docs/ | 和代码绑定 |
| API契约 | 仓库代码 | 自动生成 |
| 跨仓库架构 | Zilliz internal_kb | MCP按需查询 |
| 客户品牌 | Zilliz client_kb | RAG检索 |

**标签**：`#向量数据库` `#Zilliz` `#RAG` `#MCP` `#企业知识库` `#语义搜索`

---

*最后更新：2026-05-12*
