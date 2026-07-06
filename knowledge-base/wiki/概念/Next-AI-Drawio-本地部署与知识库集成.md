# Next AI Draw.io 本地部署与知识库集成

## 1. 🎯 这是什么

**Next AI Draw.io** 本地部署实例，可在知识库工作流中自动生成图表。

---

## 2. 📝 部署信息

| 项目 | 内容 |
|------|------|
| 本地地址 | http://localhost:6002 |
| GitHub | DayuanJiang/next-ai-draw-io |
| 本地路径 | E:\workspace\next-ai-draw-io |
| 版本 | v0.4.15 |
| AI Provider | Google Gemini |
| AI Model | gemini-2.5-flash-preview-05-20 |
| API Key | 已配置（knowledge-base/.env） |

---

## 3. ⚡ 启动方式

```bash
# 方式1：npm 启动
cd E:\workspace\next-ai-draw-io
$env:ELECTRON_MIRROR = "https://npmmirror.com/mirrors/electron/"
npm install  # 首次安装
npm run dev  # 开发模式 http://localhost:6002

# 方式2：Docker
docker build -t next-ai-drawio .
docker run -p 3000:3000 next-ai-drawio
```

### 环境变量配置（.env.local）

```bash
AI_PROVIDER=google
AI_MODEL=gemini-2.5-flash-preview-05-20
GOOGLE_GENERATIVE_AI_API_KEY=你的API_KEY
```

---

## 4. 🔌 MCP 接入

### Claude Desktop / VS Code / Cursor

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

### 使用示例

```
用户：帮我画一个用户登录流程图
→ MCP 调用 Next AI Draw.io
→ 自动生成 draw.xml
→ 打开浏览器展示图表
```

---

## 5. 🔧 知识库工作流集成

### 场景1：文档自动配图

当知识库编译时，检测到缺少图表的文档，自动调用生成：

```python
# knowledge-base/integrations/next_ai_drawio.py

import subprocess
import json

def generate_diagram(prompt: str, output_path: str):
    """
    调用 Next AI Draw.io MCP 生成图表
    """
    mcp_cmd = [
        "npx", "@next-ai-drawio/mcp-server@latest",
        "--prompt", prompt,
        "--output", output_path
    ]
    result = subprocess.run(mcp_cmd, capture_output=True)
    return json.loads(result.stdout)
```

### 场景2：架构图自动生成

在 graphify 图谱生成时，为复杂架构自动生成配图：

```
知识图谱节点：A服务 → B服务 → 数据库
    ↓
自动调用 MCP 生成微服务架构图
```

---

## 6. ✅ 优点

- ✅ 本地部署，数据安全
- ✅ 支持多种图表类型
- ✅ MCP 接入，AI Agent 可直接调用
- ✅ 自然语言描述，零学习成本
- ✅ 开源免费

---

## 7. ❌ 缺点

- ❌ Electron 下载需配置镜像（国内网络）
- ❌ 需要 API Key
- ❌ 复杂图表可能需要多次调整

---

## 8. 🚀 最佳实践

### 图表生成 Prompt 技巧

| 类型 | Prompt 示例 |
|------|------------|
| 流程图 | "用户登录流程：登录页 → 验证码校验 → Token生成 → 跳转首页" |
| 架构图 | "微服务架构：用户服务、订单服务、支付服务，使用REST通信" |
| 数据流图 | "用户下单数据流：从浏览器 → API网关 → 订单服务 → 消息队列 → 库存服务" |

### API 集成

```python
import requests

def call_local_drawio(prompt: str):
    """调用本地实例"""
    response = requests.post(
        "http://localhost:6002/api/generate",
        json={"prompt": prompt}
    )
    return response.json()
```

---

## 9. 📊 总结

| 维度 | 评分 |
|------|------|
| 部署难度 | ⭐⭐⭐（需配置镜像） |
| 使用便捷 | ⭐⭐⭐⭐⭐ |
| 集成难度 | ⭐⭐⭐（MCP 已支持） |
| 图表质量 | ⭐⭐⭐⭐⭐ |

**一句话评价**：本地部署 + MCP 接入 = 知识库自动配图神器！

---

*📅 部署日期：2026-05-08*
