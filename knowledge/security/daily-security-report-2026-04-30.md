# 🔒 OpenClaw 安全体检报告
**体检时间**: 2026-04-30 02:15 (Asia/Shanghai)
**OpenClaw版本**: 2026.4.11
**节点**: DESKTOP-LV38H7S

---

## ⚠️ 紧急告警：OpenClaw 版本存在大量安全漏洞！

当前版本 **2026.4.11** 存在 **≥28个CVE漏洞**，涵盖：
- 🔴 **1个严重(CRITICAL)** - 飞书Webhook/Card Action验证绕过
- 🟠 **6个高危(HIGH)** - SSRF、授权绕过、路径遍历等
- 🟡 **18个中危(MEDIUM)** - 配置绕过、策略绕过等
- 🟢 **3个低危(LOW)** - 信息泄露等

**推荐方案**: 升级至 **2026.4.21**（最新版）

```bash
npm install -g openclaw@latest
openclaw gateway restart
```

---

## 📊 CVE 漏洞明细（按严重程度）

### 🔴 CRITICAL（严重）

| CVE | 漏洞 | 版本范围 | 修复版本 |
|-----|------|----------|----------|
| GHSA-xh72-v6v9-mwhc | 飞书Webhook/Card Action验证失败开放 | <2026.4.15 | 2026.4.15 |

### 🟠 HIGH（高危）

| CVE | 漏洞 | 版本范围 | 修复版本 |
|-----|------|----------|----------|
| GHSA-2767-2q9v-9326 | QQBot SSRF + 重新上传字节流 | <2026.4.12 | 2026.4.12 |
| GHSA-2cq5-mf3v-mx44 | busybox/toybox applet执行削弱exec审批绑定 | >=2026.2.23, <2026.4.12 | 2026.4.12 |
| GHSA-2gvc-4f3c-2855 | Matrix房间控制命令授权绕过 | >2026.3.28, <2026.4.15 | 2026.4.15 |
| GHSA-53vx-pmqw-863c | 浏览器SSRF策略默认允许私有网络导航 | <2026.4.14 | 2026.4.14 |
| GHSA-8372-7vhw-cm6q | config.get脱敏绕过(sourceConfig/runtimeConfig别名) | <2026.4.14 | 2026.4.14 |
| GHSA-xmxx-7p24-h892 | Gateway HTTP Bearer认证在SecretRef轮换后重新解析 | <2026.4.15 | 2026.4.15 |

### 🟡 MEDIUM（中危）

| CVE | 漏洞 | 版本范围 | 修复版本 |
|-----|------|----------|----------|
| GHSA-c28g-vh7m-fm7v | 所有者强制命令可能将通配符发送者识别为命令所有者 | <=2026.4.20 | 2026.4.21 |
| GHSA-2xcp-x87w-q377 | Hook映射sessionKey模板绕过 | <2026.4.20 | 2026.4.20 |
| GHSA-49cg-279w-m73x | 空审批者列表授予显式审批权限 | <2026.4.12 | 2026.4.12 |
| GHSA-72q8-jcmc-97wx | 飞书卡片动作误分类DM为群组，绕过dmPolicy | <2026.4.20 | 2026.4.20 |
| GHSA-7jm2-g593-4qrc | Agent网关配置可修改受保护运营商配置项 | <2026.4.20 | 2026.4.20 |
| GHSA-c4qm-58hj-j6pj | 浏览器快照/截图路由导航后暴露内部内容 | <2026.4.14 | 2026.4.14 |
| GHSA-g2hm-779g-vm32 | 心跳所有者降级遗漏不可信Webhook唤醒事件 | >=2026.4.7, <2026.4.14 | 2026.4.14 |
| GHSA-h2vw-ph2c-jvwf | dotenv MiniMax宿主管控可重定向凭据请求 | >=2026.4.5, <2026.4.20 | 2026.4.20 |
| GHSA-hxvm-xjvf-93f3 | dotenv可覆盖OpenClaw运行时控制环境变量 | <2026.4.20 | 2026.4.20 |
| GHSA-j6c7-3h5x-99g9 | Shell包装器检测遗漏环境变量-参数赋值注入 | >=2026.2.22, <2026.4.12 | 2026.4.12 |
| GHSA-jwrq-8g5x-5fhm | 收集模式队列批次复用最后发送者授权上下文 | <2026.4.14 | 2026.4.14 |
| GHSA-mj59-h3q9-ghfh | MCP stdio环境变量可从工作区加载危险启动变量 | <2026.4.20 | 2026.4.20 |
| GHSA-qrp5-gfw2-gxv4 | 内置MCP/LSP工具可绕过工具策略 | <2026.4.20 | 2026.4.20 |
| GHSA-r77c-2cmr-7p47 | 投递队列恢复丢失群组工具策略上下文 | >=2026.4.10, <2026.4.14 | 2026.4.14 |

### 🟢 LOW（低危）

| CVE | 漏洞 | 版本范围 | 修复版本 |
|-----|------|----------|----------|
| GHSA-gfg9-5357-hv4c | Webchat音频嵌入可无限制读取本地文件 | <=2026.4.14 | 2026.4.15 |
| GHSA-v8qf-fr4g-28p2 | 助手媒体路由不验证操作者权限范围 | <2026.4.20 | 2026.4.20 |
| GHSA-xrq9-jm7v-g9h7 | 配对设备操作未限制为调用方自身设备 | <2026.4.20 | 2026.4.20 |

### ⚪ 其他漏洞

| CVE | 漏洞 | 版本范围 | 修复版本 |
|-----|------|----------|----------|
| CVE-2026-41389 | 未验证媒体路径导致任意本地文件/UNC读取 | 2026.4.7 ~ <2026.4.15 | 2026.4.15 |
| GHSA-mr34-9552-qr95 | Webchat媒体嵌入强制执行本地根目录限制 | 2026.4.7 ~ <2026.4.15 | 2026.4.15 |
| GHSA-f934-5rqf-xx47 | QMD memory_get读取非规范内存路径 | <2026.4.15 | 2026.4.15 |
| GHSA-gc9r-867r-j85f | Teams SSO调用处理器遗漏发送方授权检查 | >=2026.4.10, <2026.4.14 | 2026.4.14 |
| GHSA-c4qg-j8jg-42q5 | QQBot直接媒体上传跳过URL SSRF检查 | <2026.4.20 | 2026.4.20 |
| GHSA-57r2-h2wj-g887 | 隔离Cron感知事件被记录为受信任系统事件 | <2026.4.20 | 2026.4.20 |

---

## 🔍 本地安全审计结果

### ✅ 已修复/通过项

1. **攻击面**: 开放组=1，允许列表=0（正常）
2. **浏览器控制**: 已启用（正常）
3. **Hook内部钩子**: 已启用（正常）
4. **信任模型**: personal assistant（正常）

### ⚠️ 需关注项

1. **Gateway probe失败** - 深度探测超时，需检查网络连通性
2. **extensions_no_allowlist** - 3个扩展发现但无显式allowlist，建议配置`plugins.allow`
3. **Feishu工具暴露** - `channels.feishu.tools.doc`在未需要时应禁用

---

## 📦 供应链安全

### ⚠️ 未固定的npm依赖

| 插件 | 安装规格 | 风险 |
|------|----------|------|
| feishu | `@m1heng-clawd/feishu` | 无版本锁定，依赖供应链攻击 |
| openclaw-weixin | `@tencent-weixin/openclaw-weixin` | 无版本锁定，依赖供应链攻击 |

**建议**: 使用 `openclaw plugins update feishu@x.x.x` 固定到精确版本

---

## 🛒 SkillHub 商店版本检查

| 技能 | 本地版本 | 商店版本 | 状态 |
|------|----------|----------|------|
| summarize | 1.0.0 | 3.0.6 | ⚠️ **可更新** |
| nano-banana-pro | 1.0.1 | 1.0.1 | ✅ 最新 |
| cloudbase | 1.18.0 | 1.18.0 | ✅ 最新 |
| playwright-scraper-skill | 1.2.0 | 1.2.0 | ✅ 最新 |
| video-summary | 1.6.4 | 1.6.4 | ✅ 最新 |

**建议**: 
```bash
python C:\Users\Administrator\.skillhub\skills_store_cli.py update summarize
```

---

## 🎯 行动项

### 🔴 紧急（24小时内）

1. **升级OpenClaw** - `npm install -g openclaw@latest`
2. **固定Feishu插件版本** - 避免供应链攻击

### ⚠️ 中期（7天内）

1. 配置 `plugins.allow` 显式列表
2. 禁用不需要的Feishu工具 (`channels.feishu.tools.doc`)
3. 调查Gateway probe失败原因
4. 更新 summarize 技能

---

## 📋 总结

- **OpenClaw安全状态**: 🔴 危险（28个漏洞，当前版本太旧）
- **供应链安全**: ⚠️ 警告（未锁定版本）
- **SkillHub技能**: ✅ 基本正常（1个可更新）
- **建议**: 立即升级OpenClaw至最新版

---
*报告自动生成 by edgeone-clawscan @ 2026-04-30 02:15*
