// WeChat QR Login - saves QR as image and polls for confirmation
const { writeFileSync, existsSync, mkdirSync, readFileSync } = require("node:fs");
const path = require("node:path");

const API_BASE = "https://ilinkai.weixin.qq.com";
const QR_OUT = "E:/workspace/weixin-qr.png";
const STATE_DIR = "C:/Users/Administrator/.openclaw/openclaw-weixin";
const ACCOUNTS_FILE = path.join(STATE_DIR, "accounts.json");

// Ensure state dir exists
if (!existsSync(STATE_DIR)) {
  mkdirSync(STATE_DIR, { recursive: true });
  console.log("Created state dir:", STATE_DIR);
}

// Fetch QR code from API
async function fetchQR(botType = "3") {
  const url = `${API_BASE}/ilink/bot/get_bot_qrcode?bot_type=${botType}`;
  const res = await fetch(url, {
    headers: { "iLink-App-ClientVersion": "1" }
  });
  return res.json();
}

// Generate QR image
async function saveQRImage(url) {
  const QRCode = require("C:/nvm4w/nodejs/node_modules/qrcode");
  await QRCode.toFile(QR_OUT, url, { width: 400, margin: 2 });
}

// Poll QR status
async function pollStatus(qrcode) {
  const url = `${API_BASE}/ilink/bot/get_qrcode_status?qrcode=${encodeURIComponent(qrcode)}`;
  const res = await fetch(url, {
    headers: { "iLink-App-ClientVersion": "1" }
  });
  return res.json();
}

// Save credentials
function saveCredentials(data) {
  // Update accounts.json (index file)
  let accounts = [];
  if (existsSync(ACCOUNTS_FILE)) {
    try { accounts = JSON.parse(readFileSync(ACCOUNTS_FILE, "utf-8")); } catch {}
  }
  if (!Array.isArray(accounts)) accounts = [];
  if (!accounts.includes(data.ilink_bot_id)) {
    accounts.push(data.ilink_bot_id);
  }
  writeFileSync(ACCOUNTS_FILE, JSON.stringify(accounts, null, 2));
  console.log("accounts.json updated:", accounts);

  // Save per-account state
  const stateFile = path.join(STATE_DIR, `${data.ilink_bot_id}.json`);
  const state = {
    ilink_bot_id: data.ilink_bot_id,
    bot_token: data.bot_token,
    baseurl: data.baseurl || API_BASE,
    ilink_user_id: data.ilink_user_id,
    logged_in_at: new Date().toISOString(),
  };
  writeFileSync(stateFile, JSON.stringify(state, null, 2));
  console.log("State saved:", stateFile);
}

async function main() {
  console.log("Fetching QR code...\n");
  const qrData = await fetchQR();
  if (qrData.ret !== 0 || !qrData.qrcode) {
    console.error("Failed to get QR:", qrData);
    process.exit(1);
  }

  let qrcode = qrData.qrcode;
  let qrUrl = qrData.qrcode_img_content;

  // Save initial QR image
  await saveQRImage(qrUrl);
  console.log("QR image saved!");
  console.log("Open: http://127.0.0.1:18789/workspace/weixin-qr.png\n");
  console.log("==========================================");
  console.log("  请用微信扫描上方二维码！");
  console.log("  扫码后请在微信里点【确认】");
  console.log("==========================================\n");

  let expired = 0;
  const maxExpired = 3;
  const startTime = Date.now();
  const maxWait = 8 * 60 * 1000;

  while (Date.now() - startTime < maxWait) {
    await new Promise(r => setTimeout(r, 3000));

    // Refresh QR image every poll
    try {
      await saveQRImage(qrUrl);
    } catch(e) { console.error("QR save error:", e.message); }

    try {
      const status = await pollStatus(qrcode);
      const t = new Date().toLocaleTimeString();
      switch (status.status) {
        case "wait":
          expired = 0;
          process.stdout.write(`[${t}] 等待扫码...\r`);
          break;
        case "scaned":
          console.log(`\n[${t}] 👀 已扫码，请在微信点【确认】`);
          break;
        case "expired":
          expired++;
          console.log(`\n[${t}] ⏳ 二维码过期 (${expired}/${maxExpired})，刷新中...`);
          if (expired >= maxExpired) {
            console.error("过期次数过多，请重新运行");
            process.exit(1);
          }
          const newQR = await fetchQR();
          qrcode = newQR.qrcode;
          qrUrl = newQR.qrcode_img_content;
          await saveQRImage(qrUrl);
          console.log("新二维码已保存，请重新扫描！");
          break;
        case "confirmed":
          console.log(`\n[${t}] 🎉 登录成功！`);
          saveCredentials({
            ilink_bot_id: status.ilink_bot_id,
            bot_token: status.bot_token,
            baseurl: status.baseurl,
            ilink_user_id: status.ilink_user_id,
          });
          console.log("\n登录完成！可以关闭此窗口。");
          process.exit(0);
      }
    } catch (e) {
      console.error(`\nPoll error: ${e.message}`);
    }
  }
  console.error("登录超时");
  process.exit(1);
}

main().catch(e => {
  console.error("Fatal error:", e);
  process.exit(1);
});
