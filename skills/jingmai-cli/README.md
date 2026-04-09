# 京麦 UFO 智能体 CLI 工具

## 📋 概述

京麦 UFO 智能体命令行工具（CLI）提供了强大的智能体自动化系统接口，支持任务执行、记忆管理、RAG 检索等功能。

## 🚀 快速开始

### Windows 用户

```cmd
# 1. 直接运行可执行文件
cli\win64\jingmai-cli.exe --help

# 2. 运行一个简单任务
cli\win64\jingmai-cli.exe run "打开记事本并输入Hello World"

# 3. 进入交互模式
cli\win64\jingmai-cli.exe interactive
```

### Linux 用户

```bash
# 1. 添加执行权限
chmod +x cli/linux/jingmai-cli

# 2. 运行 CLI 工具
./cli/linux/jingmai-cli --help

# 3. 运行一个简单任务
./cli/linux/jingmai-cli run "打开记事本并输入Hello World"

# 4. 进入交互模式
./cli/linux/jingmai-cli interactive
```

## 📦 安装

### 从源码运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行 CLI 工具
python cli/main.py --help
```

### 使用打包的可执行文件

直接下载对应平台的可执行文件：
- Windows: `cli/win64/jingmai-cli.exe`
- Linux: `cli/linux/jingmai-cli`

## 🛠️ 主要功能

### 1. 任务执行

#### 运行单个任务
```bash
jingmai-cli run "任务描述" [选项]
```

**选项:**
- `--title, -t`: 任务标题
- `--complexity, -c`: 任务复杂度 (simple/medium/complex)
- `--priority, -p`: 优先级 (1-10)
- `--agent, -a`: Agent 类型 (ufo_agent/rag_agent/planner_agent)
- `--max-steps, -s`: 最大执行步数

**示例:**
```bash
# 简单任务
jingmai-cli run "打开记事本"

# 完整参数
jingmai-cli run "整理桌面文件" -t "文件整理" -c simple -p 3 -a ufo_agent
```

#### 交互式模式
```bash
jingmai-cli interactive [选项]
```

**示例:**
```bash
# 使用默认 Agent
jingmai-cli interactive

# 指定 Agent
jingmai-cli interactive -a rag_agent
```

#### 批量执行
```bash
jingmai-cli batch [文件] [选项]
```

**示例:**
```bash
# 从文件读取
jingmai-cli batch tasks.txt

# JSON 格式
jingmai-cli batch -f json tasks.json

# 从标准输入
echo "任务1\n任务2\n任务3" | jingmai-cli batch
```

### 2. 系统状态

```bash
jingmai-cli status [选项]
```

**选项:**
- `--verbose, -v`: 显示详细信息
- `--json, -j`: 以 JSON 格式输出

**示例:**
```bash
# 基本状态
jingmai-cli status

# 详细信息
jingmai-cli status -v

# JSON 输出
jingmai-cli status --json
```

### 3. 记忆管理

#### 创建记忆
```bash
jingmai-cli memory create "记忆内容" [选项]
```

**选项:**
- `--type, -t`: 记忆类型 (short/long/working)
- `--key, -k`: 记忆键
- `--priority, -p`: 优先级 (low/medium/high/critical)
- `--tags, -g`: 标签
- `--ttl`: 过期时间（秒）

#### 搜索记忆
```bash
jingmai-cli memory search "查询关键词" [选项]
```

**选项:**
- `--type, -t`: 记忆类型过滤
- `--top-k, -k`: 返回结果数量
- `--tags, -g`: 标签过滤

#### 记忆统计
```bash
jingmai-cli memory stats
```

#### 清空记忆
```bash
jingmai-cli memory clear [选项]
```

### 4. RAG 知识库

#### 查询知识库
```bash
jingmai-cli rag query "查询问题" [选项]
```

**选项:**
- `--top-k, -k`: 返回结果数量
- `--rerank, -r`: 启用重排序

#### 知识库统计
```bash
jingmai-cli rag stats
```

### 5. 技能管理

#### 列出技能
```bash
jingmai-cli skills list [选项]
```

**选项:**
- `--category, -c`: 按类别筛选
- `--verbose, -v`: 显示详细信息

#### 搜索技能
```bash
jingmai-cli skills search "搜索关键词" [选项]
```

**选项:**
- `--top-k, -k`: 返回结果数量

## ⚙️ 配置

CLI 工具使用项目根目录的 `.env` 文件进行配置：

```env
# 应用配置
APP_NAME=京麦智能体系统
APP_VERSION=v1.0.0
DEBUG=True

# 数据库配置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=jingmai_agent
DB_USER=root
DB_PASSWORD=password

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# LLM 配置
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5
```

## 🔧 开发

### 打包 CLI 工具

详细的打包说明请参考 [BUILD_GUIDE.md](BUILD_GUIDE.md)

```bash
# Windows
cli\build_cli_win.bat

# Linux
./cli/build_cli_linux.sh
```

### 从源码运行

```bash
# 确保在项目根目录
python cli/main.py --help
```

## 📝 注意事项

1. **环境要求**: 
   - Python 3.12+（从源码运行时）
   - Windows 10+ 或 Linux 系统

2. **依赖服务**:
   - MySQL/MariaDB 数据库
   - Redis 缓存
   - Milvus 向量数据库（RAG 功能）

3. **首次运行**:
   - 确保数据库连接配置正确
   - 检查所有依赖服务是否运行

4. **文件权限** (Linux):
   ```bash
   chmod +x cli/linux/jingmai-cli
   ```

## 🐛 故障排除

### 常见问题

1. **命令无法识别**
   - Windows: 确保使用 `.exe` 后缀
   - Linux: 确保有执行权限

2. **数据库连接失败**
   - 检查 `.env` 文件配置
   - 确保数据库服务运行正常

3. **Agent 初始化失败**
   - 检查 LLM 服务配置
   - 确保 Ollama 服务运行正常

## 📞 支持

- 查看 [BUILD_GUIDE.md](BUILD_GUIDE.md) 了解打包详情
- 查看项目主 README 了解整体架构
- 提交 Issue 报告问题

## 📄 许可证

[项目许可证]
