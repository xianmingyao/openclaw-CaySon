# 自我反思与改进报告 - 2026-04-09

## 今日工作反思

### 1. Karpathy 知识库系统搭建

**做得好的：**

- 完整实现了 INGEST/QUERY/LINT 三阶段闭环

- 成功配置了飞书和 Notion 同步

- 目录结构清晰：raw/ → wiki/ → CLAUDE.md

**遇到的问题：**

- 飞书权限申请耗时（需要手动在开放平台操作）

- Notion 集成需要 Database 页面手动添加连接

- compile.py 生成的中文文件名出现乱码（但 UTF-8 实际正确）

**教训：**

- 第三方平台 API 权限问题最好一开始就验证

- PowerShell 控制台显示乱码 ≠ 实际数据损坏

### 2. agent-browser 使用

**问题：**

- 一开始没加 `--headed`，用户看不到浏览器窗口

- 浪费了很多时间调试

**教训：**

- 宁兄铁律：只要开浏览器，必须 `--headed`

- daemon 已运行时必须先 `agent-browser close` 再重新开

### 3. 调教准则执行

**新准则：**

- 记忆检索：Milvus 优先 → ChromaDB 降级

- 知识验证：6个来源全覆盖

- 存储流程：Karpathy → Wiki → 飞书 → Notion → Milvus

**理解：**

- 这是一套完整的知识管理闭环

- 我需要养成习惯：每次处理信息都走这个流程

---

## 能力提升

### 已掌握技能

| 技能 | 掌握程度 | 备注 |

|------|---------|------|

| compile.py | ✅ | INGEST摄入 |

| lint.py | ✅ | 健康检查 |

| query.py | ✅ | 问答查询 |

| sync_feishu.py | ✅ | 飞书同步 |

| sync_notion.py | ✅ | Notion同步 |

| upload_mem0.py | ✅ | Milvus上传 |

### 待提升

| 技能 | 状态 | 说明 |

|------|------|------|

| Notion API 深入 | 🔰 | Database 创建/权限管理 |

| 抖音内容抓取 | 🔰 | 需要登录Cookie方案 |

| 知识图谱可视化 | 🔰 | 未实践 |

---

## 明日计划

1. 按新准则执行知识检索和整合

2. 测试 query.py 实际使用效果

3. 继续丰富知识库内容