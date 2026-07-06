# 微信机器人登录链接 - 2026-07-05 09:00

## 状态
- 频道：openclaw-weixin (6a4a8adda83b-im-bot)
- 状态：session 超时（errcode: -14），需要重新扫码
- 网络：✅ 正常（curl HTTP 200 0.15s）
- bot_type: 3

## 登录链接（5分钟内有效）
```
https://liteapp.weixin.qq.com/q/7GiQu1?qrcode=0b2fd1d112f45f072224765c931789e4&bot_type=3
```

## 重新生成命令（如需新链接）
```
$body = '{"local_token_list":["6a4a8adda83b@im.bot:060000727904aefc5dc574ee528c9cea7ec0fa"]}'
curl -X POST "https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3" -H "Content-Type: application/json" -d $body
```

## 调试发现
- 微信 API 域名 `ilinkai.weixin.qq.com` DNS 解析到 `198.18.0.101`（FlClash 虚拟接口网段，非真腾讯 IP）
- OpenClaw 历史 ETIMEDOUT 日志是昨晚网络断时的旧日志
- 当前网络完全可达，session 仅是过期
- exec 工具无法跑交互式 `openclaw channels login`
- 解决：直接调用 `get_bot_qrcode` API 拿链接，绕过 CLI 限制
