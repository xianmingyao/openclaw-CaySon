# Jingmai Agent CLI 系统架构

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Entry Point                        │
│                         main.py                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLI Service Layer                          │
│                    cli/service/                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ CLIService  │  │ServiceInit   │  │   Commands      │   │
│  │ - execute   │  │- initialize   │  │ - run           │   │
│  │ - batch     │  │  _cli_services│  │ - interactive   │   │
│  │ - memory    │  │              │  │ - batch         │   │
│  │ - rag       │  │              │  │ - memory_*      │   │
│  │ - skills    │  │              │  │ - rag_*         │   │
│  └─────────────┘  └──────────────┘  │ - skills_*     │   │
│                                      │ - status       │   │
└─────────────────────────┬────────────┴─────────────────┴───┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Service Layer                        │
│                    app/service/                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ LLMManager  │  │ AgentFactory │  │  SkillRegistry  │   │
│  │             │  │ - ufo_agent  │  │  - load_skills  │   │
│  │ - ollama    │  │ - rag_agent  │  │  - list_skills  │   │
│  │ - openai    │  │ - planner    │  │  - search       │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │MemoryManager│  │ RAGService   │  │  SkillLoader    │   │
│  │ - short_term│  │ - query      │  │  - load_from_dir│   │
│  │ - long_term │  │ - rerank     │  │                 │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Database   │  │    Redis     │  │    Milvus       │   │
│  │  (MySQL)    │  │   (Cache)    │  │   (Vector)      │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心组件

### 1. CLI 入口 (main.py)

**职责:** 命令行入口，解析参数，调用服务

**主要命令:**
- `run` - 单任务执行
- `interactive` - 交互模式
- `batch` - 批量执行
- `memory create/search/stats/clear` - 记忆管理
- `rag query/stats` - RAG 查询
- `skills list/search` - 技能管理
- `status` - 系统状态

---

### 2. CLI Service (cli/service/)

#### CLIService
- 任务执行
- 批量执行
- 记忆 CRUD
- RAG 查询
- 技能管理

#### ServiceInitializer
- LLM 管理器初始化
- Agent 工厂初始化
- 记忆管理器初始化
- RAG 服务初始化
- 技能注册表初始化

---

### 3. Agent Service (app/service/)

#### LLMManager
- 多 Provider 支持 (Ollama/OpenAI)
- 模型配置管理
- 对话生成

#### AgentFactory
- `ufo_agent` - UFO Windows 自动化 Agent
- `rag_agent` - RAG 检索 Agent
- `planner_agent` - 规划 Agent

#### MemoryManager
- `ShortTermMemory` - 短期记忆
- `LongTermMemory` - 长期记忆
- 记忆创建/搜索/统计

#### RAGService
- 向量检索
- 重排序
- 知识库查询

#### SkillRegistry
- 技能注册
- 技能加载
- 技能搜索

---

### 4. Skills 系统 (resources/ufo_actions/)

UFO 框架的核心技能定义，包含：
- 鼠标操作 (click/double_click/drag)
- 键盘操作 (type/keyboard_input/keypress)
- 滚动操作 (scroll/wheel_mouse_input)
- 系统操作 (run_command/check_process/open_app)
- 信息获取 (texts/summary/annotation)

---

## 数据流

### 单任务执行流程

```
1. user: jingmai run "打开记事本"
         │
         ▼
2. main.py: run() 命令解析
         │
         ▼
3. ensure_services_initialized()
         │
         ▼
4. ServiceInitializer.initialize_cli_services()
         │
         ▼
5. AgentFactory.create_agent("ufo_agent")
         │
         ▼
6. agent.execute(task, session, max_steps)
         │
         ▼
7. UFO Actions 执行
         │
         ▼
8. 返回执行结果
```

---

## 配置管理

环境变量优先，`.env` 文件次之：

```python
# 优先级
os.environ["KEY"] > .env["KEY"] > 默认值
```

---

## 依赖服务

| 服务 | 用途 | 必需 |
|------|------|------|
| MySQL | 任务/记忆持久化 | 是 |
| Redis | 缓存/工作记忆 | 是 |
| Milvus | 向量存储/RAG | 否 |
| Ollama | LLM 推理 | 是 |

---

## 打包说明

### Windows
```bash
pyinstaller jingmai-cli.spec
```

### Linux
```bash
chmod +x build_cli_linux.sh
./build_cli_linux.sh
```

---

## 扩展开发

### 新增 Agent 类型

1. 在 `app/service/agents/` 创建 Agent 类
2. 在 `AgentFactory.create_agent()` 注册
3. 在 `resources/` 添加对应技能 SKILL.md

### 新增 CLI 命令

1. 在 `main.py` 添加 `@cli.command()`
2. 在 `CLIService` 添加对应方法
