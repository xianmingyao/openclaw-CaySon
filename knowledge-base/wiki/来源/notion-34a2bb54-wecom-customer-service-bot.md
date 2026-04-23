# 企业微信外部群客服机器人配置方案

> 需求：发运单号 → 识别意图 → 请求接口获取轨迹

> 场景：外部群 + 客服账号 + AI 意图识别

---

## 🎯 方案架构

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

---

## 📋 配置步骤

### 1. 企业微信应用配置

企业微信管理后台 ──▶ 应用管理 ──▶ 创建应用

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