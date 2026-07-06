# Claude Code + 飞书 Agent办公 - 部署与使用指南

> 来源：微信公众号【文章：分享5个Claude Code + 飞书的超实用Agent办公玩法】
> 文章链接：https://mp.weixin.qq.com/s/6vqkEvFYNEtUu3rTQAllzw
> 更新时间：2026-05-12
> 环境：Windows + Node.js v22 + OpenClaw

---

## 1. 🎯 这篇文章讲什么

### 核心观点
- **Claude Code** 已成为操作飞书的主要工具，减少对GUI的依赖
- 飞书CLI已开源并频繁更新，能力项增加了近120项
- 通过Claude Code操控飞书，可以完成绝大部分自动化办公流程

### 飞书开放平台最新能力（2024年5月）
- **多Agent协作**：Agent之间可以互相@和调用
- **拟人化操作**：Agent能像真实用户一样操作（显示姓名头像、发送多媒体、表情回复、修改群聊等）

---

## 2. 📝 当前环境检查

### 2.1 已有的环境
```
Node.js: v22.22.1 ✅
npm: 可用 ✅
OpenClaw: 已安装 ✅
飞书: 已配置 ✅
```

### 2.2 飞书CLI安装状态
```bash
# 检查是否安装
npx @larksuiteoapi/node-sdk --version

# 如果没有，使用npm安装
npm install -g @larksuiteoapi/node-sdk
```

---

## 3. ⚡ 快速部署

### 3.1 安装飞书CLI工具
```bash
# 方法1：使用npx直接运行
npx @larksuiteoapi/feishu-cli

# 方法2：全局安装
npm install -g @larksuiteoapi/feishu-cli

# 方法3：通过OpenClaw的MCP Server
# OpenClaw已集成飞书MCP Server
```

### 3.2 配置飞书API权限
```
1. 打开 https://open.feishu.cn/app
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 添加权限：
   - im:message（发送消息）
   - docx:document（文档操作）
   - drive:drive（云文档操作）
   - calendar:calendar（日历操作）
5. 发布应用
```

### 3.3 配置OpenClaw飞书MCP
```json
// 在OpenClaw配置中添加
{
  "mcpServers": {
    "feishu": {
      "command": "npx",
      "args": ["@larksuiteoapi/feishu-mcp"]
    }
  }
}
```

---

## 4. 🔧 飞书CLI核心能力

### 4.1 消息相关
```bash
# 发送文本消息
feishu message send --chat-id xxx --content "Hello"

# 发送富媒体消息
feishu message send-card --chat-id xxx --card template.json

# 获取消息列表
feishu message list --chat-id xxx
```

### 4.2 文档相关
```bash
# 创建文档
feishu doc create --title "测试文档"

# 读取文档
feishu doc read --doc-id xxx

# 写入文档块
feishu doc write-block --doc-id xxx --content "内容"
```

### 4.3 云文档相关
```bash
# 上传文件
feishu drive upload --file path/to/file

# 获取文件列表
feishu drive list --folder-id xxx

# 分享文件
feishu drive share --file-id xxx --permission rw
```

### 4.4 日历相关
```bash
# 创建日历事件
feishu calendar create --title "会议" --start-time "2026-05-12 15:00"

# 获取日历列表
feishu calendar list
```

---

## 5. 🤖 Claude Code + 飞书使用场景

### 5.1 自动化办公场景

#### 场景1：自动生成周报
```
用户：帮我整理这周的飞书消息，生成周报

Claude Code执行：
1. 调用飞书API获取本周消息
2. 按项目/人员分类
3. 生成周报格式
4. 发布到飞书文档
```

#### 场景2：智能客服
```
用户：有客户问产品报价，帮我自动回复

Claude Code执行：
1. 调用飞书消息API读取客户消息
2. 理解问题并生成回答
3. 自动发送回复消息
4. 关键问题转人工
```

#### 场景3：会议纪要
```
用户：整理一下今天的会议内容

Claude Code执行：
1. 获取会议录音/文字记录
2. 提取关键决策和待办
3. 生成会议纪要格式
4. 同步到飞书日历+文档
```

### 5.2 多Agent协作

#### Agent架构
```
用户请求
    ↓
调度Agent（理解意图）
    ↓
├── 客服Agent → 回答问题
├── 文档Agent → 整理资料
└── 日历Agent → 安排日程
    ↓
结果汇总 → 飞书通知
```

---

## 6. 🚀 在OpenClaw中使用

### 6.1 通过MCP Server调用飞书
```
在OpenClaw中，可以直接使用飞书MCP Server：

1. 配置MCP Server
2. 使用自然语言控制飞书
3. 自动化工作流
```

### 6.2 飞书文档同步
```bash
# 使用飞书Doc MCP
feishu_doc read --doc-id xxx

# 同步到本地
sync_to_local --doc-id xxx --folder ./docs
```

---

## 7. 📚 相关资源

### 7.1 官方资源
- 飞书开放平台：https://open.feishu.cn
- 能力说明：https://open.feishu.cn/changelog?abilityType=Tool
- 飞书CLI安装指南：https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md

### 7.2 GitHub资源
- 飞书CLI：https://github.com/larksuite/oapi-sdk-nodejs
- Star数：接近1万 ⭐

### 7.3 OpenClaw集成
- 飞书MCP Server：已集成
- Skills：feishu-doc, feishu-drive, feishu-wiki

---

## 8. 🕳️ 避坑指南

### 坑1：权限不足
**问题**：API返回权限错误
**解决**：检查应用权限配置，确保已添加所需权限并发布

### 坑2：Token过期
**问题**：调用API返回401
**解决**：定期刷新Token，或使用refresh_token机制

### 坑3：频率限制
**问题**：API返回限流错误
**解决**：
- 添加请求间隔（1秒以上）
- 使用批量操作替代单次调用
- 申请提升频率限制

### 坑4：中文编码问题
**问题**：返回的中文乱码
**解决**：确保使用UTF-8编码

---

## 9. ✅ 总结

### Claude Code + 飞书 = 办公自动化

| 能力 | 说明 |
|------|------|
| **消息自动化** | 自动收发消息、智能客服 |
| **文档自动化** | 自动生成、整理、同步文档 |
| **日历自动化** | 智能日程安排、会议纪要 |
| **多Agent协作** | 多个Agent分工合作 |

### 一句话总结：
> **用Claude Code操控飞书，即使用户不具备极客级别的技术能力，也能完成绝大部分自动化的办公流程和Agent构建。**

---

*整理时间：2026-05-12*
