# Next AI Draw.io - 智能图表生成工具

## 1. 🎯 这是什么

**Next AI Draw.io** 是一个基于 Next.js 的开源 AI 图表生成工具，将 draw.io 的强大编辑能力与 AI 理解能力结合，通过自然语言描述即可创建、编辑专业图表。

**GitHub:** `DayuanJiang/next-ai-draw-io`
**官网 Demo:** https://next-ai-drawio.jiang.jp

---

## 2. 📝 关键功能点

| 功能 | 说明 |
|------|------|
| 🤖 自然语言生成图表 | 说话就能画图 |
| 🖼️ 图片转图表 | 上传图片AI自动还原为图表 |
| 📄 PDF/文档生成图表 | 文档扔进去自动出图 |
| 💬 对话式编辑 | 边聊边改图表 |
| ☁️ 云架构图专精 | AWS/GCP/Azure 架构图 |
| 🎬 动态连接线 | 动画连接器，超炫 |
| 📜 版本历史 | 改错了随时回滚 |

---

## 3. ⚡ 怎么使用

### 在线使用（推荐新手）
1. 打开 https://next-ai-drawio.jiang.jp
2. 输入自然语言描述想要的图表
3. AI 自动生成，支持对话修改

### 本地部署
```bash
# 克隆项目
git clone https://github.com/DayuanJiang/next-ai-draw-io
cd next-ai-draw-io
npm install
cp env.example .env.local

# 填入 API Key（支持：Doubao/OpenAI/DeepSeek/Claude 等）
# 启动
npm run dev

# 打开 http://localhost:6002
```

### MCP 接入（AI Agent 联动）
```json
{
  "mcpServers": {
    "drawio": {
      "command": "npx",
      "args": ["@next-ai-drawio/mcp-server@latest"]
    }
  }
}
```

---

## 4. ✅ 优点

- ✅ **零门槛**：自然语言即可生成专业图表
- ✅ **多格式支持**：架构图、流程图、数据流图、思维导图
- ✅ **AI 对话式编辑**：边聊边改，所见即所得
- ✅ **图片转图表**：草图/截图上传自动还原
- ✅ **MCP 集成**：可接入 Claude Code/Cursor 等 AI 工具
- ✅ **开源免费**：Apache 2.0 协议
- ✅ **活跃社区**：28.6k Stars，3k Forks，57 Contributors

---

## 5. ❌ 缺点

- ❌ 需要自备 API Key（在线 Demo 有免费额度）
- ❌ 部分高级功能需要科学上网
- ❌ Docker 部署对国内服务器不太友好
- ❌ 中文文档较少

---

## 6. 🎬 使用场景

| 场景 | 示例 |
|------|------|
| 微服务架构图 | 用户服务 → 订单服务 → 支付服务 |
| 云架构设计 | AWS/GCP/Azure 拓扑图 |
| 业务流程图 | 审批流、订单处理流程 |
| 技术文档配图 | API 调用链、数据库 ER 图 |
| 数据流图 | ETL 流程、数据管道 |
| 思维导图 | 需求分析、头脑风暴 |

---

## 7. 🔧 运行依赖环境

| 依赖 | 版本要求 |
|------|----------|
| Node.js | ≥18.0.0 |
| npm/pnpm | 最新版 |
| AI API Key | OpenAI/Claude/Doubao/DeepSeek 等 |

---

## 8. 🚀 部署使用注意点

### 环境变量配置
```bash
# .env.local
# 支持多种 AI 提供商（至少配置一个）
DOUBAO_API_KEY=xxx      # 字节豆包
OPENAI_API_KEY=xxx      # OpenAI GPT
ANTHROPIC_API_KEY=xxx   # Claude
DEEPSEEK_API_KEY=xxx    # DeepSeek

# 可选配置
NEXT_PUBLIC_APP_URL=http://localhost:6002
```

### Docker 部署
```bash
docker build -t next-ai-drawio .
docker run -p 3000:3000 next-ai-drawio
```

### 桌面应用
```bash
# Electron 版本，支持离线使用
npm run electron:dev    # 开发模式
npm run electron:build  # 构建安装包
```

---

## 9. 🕳️ 避坑指南

### 🔴 坑1：API Key 未配置
**问题**：启动后 AI 功能不可用
**解决**：必须在 `.env.local` 中配置至少一个 AI API Key

### 🔴 坑2：端口冲突
**问题**：`Port 6002 is already in use`
**解决**：`npm run dev -- -p 3000` 指定其他端口

### 🔴 坑3：MCP 连接失败
**问题**：MCP 服务无法连接
**解决**：
```bash
# 确保使用正确版本
npx @next-ai-drawio/mcp-server@latest --help
```

### 🟡 建议：优先使用 Claude
**推荐理由**：Claude 3.5/4 在图表理解上表现最佳，生成质量高

---

## 10. 📊 总结

| 维度 | 评分 |
|------|------|
| 学习价值 | ⭐⭐⭐⭐⭐（5星） |
| 实用价值 | ⭐⭐⭐⭐⭐（5星） |
| 开源热度 | ⭐⭐⭐⭐⭐（28.6k Stars） |
| 社区活跃度 | ⭐⭐⭐⭐（57 Contributors，119 Issues） |
| 文档完善度 | ⭐⭐⭐⭐（英文为主） |

**推荐指数**：⭐⭐⭐⭐⭐（5星）

**一句话评价**：AI + 图表的完美结合，MCP 接入让 AI Agent 直接生成图表，是技术文档工作者和架构师的效率神器！

---

## 📚 相关资源

- 🌐 官网 Demo：https://next-ai-drawio.jiang.jp
- 💾 GitHub：https://github.com/DayuanJiang/next-ai-draw-io
- 📦 NPM：https://www.npmjs.com/package/@next-ai-drawio/mcp-server
- 🐳 Docker：https://hub.docker.com/r/nextai/drawio

---

*📅 收录日期：2026-05-08*
*🔗 来源：抖音 @成也2077 推荐*
