# 企业微信外部群客服机器人配置方案

> 需求：发运单号 → 识别意图 → 请求接口获取轨迹
> 场景：外部群 + 客服账号 + AI 意图识别

---

## 🎯 方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    企业微信外部群                              │
│  ┌─────────────┐                                           │
│  │  客户      │ ──▶ 发消息（运单号）                        │
│  └─────────────┘                                           │
│          │                                                  │
│          ▼                                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              企业微信客服账号                          │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │    │
│  │  │ 消息接收 │─▶│ 意图识别 │─▶│ API调用 │            │    │
│  │  │ Webhook  │  │  LLM/规则 │  │ 物流接口 │            │    │
│  │  └─────────┘  └─────────┘  └─────────┘            │    │
│  └─────────────────────────────────────────────────────┘    │
│          │                                                  │
│          ▼                                                  │
│  ┌─────────────┐                                           │
│  │  返回轨迹   │ ──▶ 回复客户                              │
│  └─────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 配置步骤

### 1. 企业微信应用配置

```
企业微信管理后台 ──▶ 应用管理 ──▶ 创建应用
```

| 配置项 | 值 |
|--------|-----|
| 应用名称 | 物流客服助手 |
| 应用描述 | 物流轨迹查询机器人 |
| 企业可信IP | 你的服务器 IP |
| 消息接收URL | `https://your-server.com/wechat/callback` |

### 2. 获取必要参数

| 参数 | 说明 | 获取位置 |
|------|------|---------|
| CorpID | 企业ID | 企业微信管理后台 |
| CorpSecret | 应用密钥 | 应用详情页 |
| AgentID | 应用ID | 应用详情页 |
| Token | 调用Token | 应用详情页 |
| EncodingAESKey | 加密Key | 应用详情页 |

### 3. 接收消息（Node.js 示例）

```javascript
// wechat-callback.js
const express = require('express');
const crypto = require('crypto');
const axios = require('axios');

const app = express();

// 企业微信配置
const WECOM = {
  corpId: 'your-corp-id',
  corpSecret: 'your-corp-secret',
  agentId: 'your-agent-id',
  token: 'your-token',
  encodingAesKey: 'your-aes-key'
};

// 验证签名
function verifySignature(req) {
  const { msg_signature, timestamp, nonce, echostr } = req.query;
  const str = [WECOM.token, timestamp, nonce, echostr].sort().join('');
  const sha1 = crypto.createHash('sha1').update(str).digest('hex');
  return sha1 === msg_signature;
}

// 解密消息
function decryptMsg(encryptedMsg) {
  const aes = crypto.createDecipheriv(
    'aes-256-cbc',
    Buffer.from(WECOM.encodingAesKey + '=', 'base64'),
    Buffer.from(WECOM.encodingAesKey, 'base64').slice(0, 16)
  );
  aes.setAutoPadding(false);
  let decrypted = Buffer.concat([aes.update(encryptedMsg), aes.final()]);
  // 去除随机串、长度和-padding
  const msgLen = decrypted.readUInt32BE(16);
  return JSON.parse(decrypted.slice(20, 20 + msgLen));
}

// 发送消息
async function sendMessage(toUser, content) {
  const token = await getAccessToken();
  const url = `https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=${token}`;
  
  await axios.post(url, {
    touser: toUser,
    msgtype: 'text',
    agentid: WECOM.agentId,
    text: { content }
  });
}

// 获取轨迹（你的接口）
async function getTracking(orderNo) {
  const response = await axios.get(`https://your-api.com/track/${orderNo}`);
  return response.data;
}

// 意图识别（简化版）
function recognizeIntent(text) {
  // 运单号正则
  const orderPattern = /^[A-Z0-9]{10,20}$/i;
  
  if (orderPattern.test(text.trim())) {
    return { intent: 'query_tracking', orderNo: text.trim() };
  }
  
  return { intent: 'unknown' };
}

// 消息处理
app.post('/wechat/callback', async (req, res) => {
  const { msg_signature, timestamp, nonce } = req.query;
  const encryptedMsg = req.body.Encrypt;
  
  const msg = decryptMsg(encryptedMsg);
  
  if (msg.MsgType === 'text') {
    const { intent, orderNo } = recognizeIntent(msg.Content);
    
    if (intent === 'query_tracking') {
      try {
        const tracking = await getTracking(orderNo);
        await sendMessage(msg.FromUserName, `运单 ${orderNo} 的轨迹：\n${tracking}`);
      } catch (e) {
        await sendMessage(msg.FromUserName, `查询失败：${e.message}`);
      }
    }
  }
  
  res.send('success');
});

app.listen(3000);
```

---

## 🔧 OpenClaw 集成方案

如果用 OpenClaw 集成企业微信：

### 方案1：Feishu Webhook（推荐）

```javascript
// openclaw 企业微信转发
const express = require('express');
const app = express();

app.post('/wecom-webhook', async (req, res) => {
  const { msg_signature, timestamp, nonce } = req.query;
  const encryptedMsg = req.body.Encrypt;
  
  // 解密消息
  const msg = decryptMsg(encryptedMsg);
  
  // 转发到 OpenClaw
  await axios.post('http://localhost:18789/api/message', {
    channel: 'wecom',
    message: msg.Content,
    from: msg.FromUserName
  });
  
  res.send('success');
});
```

### 方案2：直接调用 OpenClaw API

```javascript
// 意图识别 + API 调用
async function handleMessage(text, fromUser) {
  // 1. 识别意图
  const { intent, orderNo } = recognizeIntent(text);
  
  if (intent === 'query_tracking') {
    // 2. 调用物流 API
    const tracking = await getTracking(orderNo);
    
    // 3. 通过 OpenClaw 发送消息
    await axios.post('http://localhost:18789/api/send', {
      channel: 'openclaw-weixin',
      to: fromUser,
      message: formatTrackingResponse(tracking)
    });
  }
}
```

---

## 🤖 意图识别增强（LLM 版）

如果用 AI 做意图识别：

```javascript
// 意图识别 + 实体提取
const { Configuration, OpenAIApi } = require('openai');

const openai = new OpenAIApi(new Configuration({
  apiKey: process.env.OPENAI_API_KEY
}));

async function aiIntentRecognition(text) {
  const response = await openai.createChatCompletion({
    model: 'gpt-3.5-turbo',
    messages: [{
      role: 'system',
      content: `你是一个物流客服助手。用户会发送运单号，你需要识别并提取。

示例：
- "查询运单号 SF1234567890" → {"intent": "query_tracking", "orderNo": "SF1234567890"}
- "你好" → {"intent": "greeting"}
- "谢谢" → {"intent": "thanks"}

只返回 JSON。`
    }, {
      role: 'user',
      content: text
    }]
  });
  
  return JSON.parse(response.data.choices[0].message.content);
}
```

---

## 📊 完整流程图

```
客户发消息
    │
    ▼
企业微信 Webhook
    │
    ▼
消息解密
    │
    ▼
意图识别（规则/LLM）
    │
    ├── 运单号 ──▶ 调用物流 API ──▶ 返回轨迹
    │
    ├── 问候 ──▶ 回复欢迎语
    │
    └── 其他 ──▶ 转人工客服
```

---

## 🛠️ 快速验证

```bash
# 1. 测试消息接收
curl -X POST http://localhost:3000/wechat/callback \
  -H "Content-Type: application/json" \
  -d '{"msg_signature":"xxx","timestamp":"xxx","nonce":"xxx","Encrypt":"xxx"}'

# 2. 测试发送消息
curl -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{"touser":"user-id","content":"测试消息"}'
```

---

## 📝 企业微信外部群配置要点

| 步骤 | 说明 |
|------|------|
| 1. 开通企业微信 | 需要有已认证的企业 |
| 2. 创建应用 | 获取 AgentID、Secret、Token |
| 3. 配置可信IP | 你的服务器 IP 必须在白名单 |
| 4. 设置消息格式 | 文本、图片、图文等 |
| 5. 配置机器人 | 可选：用 Bot 接收消息 |

---

## 💡 关键点

1. **消息必须解密** - 企业微信用 AES 加密
2. **必须响应 success** - 否则会重复发送
3. **可信 IP** - 服务器 IP 必须在白名单
4. **AccessToken** - 需要缓存，过期前刷新
5. **消息格式** - 支持文本、图片、图文、小程序等

---

## 🚀 下一步

1. 你有企业微信的 CorpID、AgentID、Secret 了吗？
2. 物流 API 的接口格式是什么？
3. 需要我帮你写完整的代码吗？
