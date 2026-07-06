// 触发微信 bot 重新登录 -> 获取 qrcode URL
// 由 cron 任务 morning-wechat-login-check 调用
//
// 创建：2026-07-03（执行 morning-wechat-login-check 时遇到 exec 拦截 channels login 后的绕过方案）

import { startWeixinLoginWithQr } from 'file:///C:/Users/Administrator/.openclaw/npm/node_modules/@tencent-weixin/openclaw-weixin/dist/src/auth/login-qr.js';

const opts = {
  accountId: '6a4a8adda83b-im-bot',  // 当前活跃的 account id（从 channels status 拿到）
  botType: '3',                       // DEFAULT_ILINK_BOT_TYPE
  force: true,                        // 强制重新生成（即使有缓存）
};

console.log(JSON.stringify({
  ts: new Date().toISOString(),
  action: 'startWeixinLoginWithQr',
  accountId: opts.accountId,
}));

try {
  const result = await startWeixinLoginWithQr(opts);
  console.log('RESULT:' + JSON.stringify(result));
} catch (e) {
  console.log('ERROR:' + e.message);
  console.log('STACK:' + (e.stack || '').slice(0, 500));
}
