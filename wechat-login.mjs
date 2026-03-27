// WeChat QR Login - saves QR as image and polls for confirmation
import { writeFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const API_BASE = "https://ilinkai.weixin.qq.com";
const QR_OUT = "E:/workspace/weixin-qr.png";
const STATE_DIR = "C:/Users/Administrator/.openclaw/openclaw-weixin";
const ACCOUNTS_FILE = join(STATE_DIR, "accounts.json");
const STATE_FILE = join(STATE_DIR, "state.json");

// 1. Ensure state dir exists
if (!existsSync(STATE_DIR)) {
  mkdirSync(STATE_DIR, { recursive: true });
  console.log("Created state dir:", STATE_DIR);
}

// 2. Fetch QR code
async function fetchQR(botType = "3") {
  const url = `${API_BASE}/ilink/bot/get_bot_qrcode?bot_type=${botType}`;
  const res = await fetch(url, {
    headers: { "iLink-App-ClientVersion": "1" }
  });
  return await res.json();
}

// 3. Generate QR image
async function saveQRImage(url: string) {
  // Dynamic import qrcode
  const { default: QRCode } = await import("qrcode");
  await QRCode.toFile(QR_OUT, url, { width: 400, margin: 2 });
  console.log("QR image saved:", QR_OUT);
  console.log("Open: http://127.0.0.1:18789/workspace/weixin-qr.png");
}

// 4. Poll QR status
async function pollStatus(qrcode: string) {
  const url = `${API_BASE}/ilink/bot/get_qrcode_status?qrcode=${encodeURIComponent(qrcode)}`;
  const res = await fetch(url, {
    headers: {
      "iLink-App-ClientVersion": "1",
    }
  });
  return await res.json();
}

// 5. Save credentials
function saveCredentials(data: {
  ilink_bot_id: string;
  bot_token?: string;
  baseurl?: string;
  ilink_user_id?: string;
}) {
  // Update accounts.json
  let accounts: string[] = [];
  if (existsSync(ACCOUNTS_FILE)) {
    try {
      accounts = JSON.parse(readFileSync(ACCOUNTS_FILE, "utf-8"));
    } catch {}
  }
  if (!accounts.includes(data.ilink_bot_id)) {
    accounts.push(data.ilink_bot_id);
  }
  writeFileSync(ACCOUNTS_FILE, JSON.stringify(accounts, null, 2));
  console.log("accounts.json updated:", accounts);

  // Save state
  const state = {
    ilink_bot_id: data.ilink_bot_id,
    bot_token: data.bot_token,
    baseurl: data.baseurl || API_BASE,
    ilink_user_id: data.ilink_user_id,
    logged_in_at: new Date().toISOString(),
  };
  const stateFile = join(STATE_DIR, `${data.ilink_bot_id}.json`);
  writeFileSync(stateFile, JSON.stringify(state, null, 2));
  console.log("State saved:", stateFile);
}

// 6. Main loop
async function main() {
  console.log("Fetching QR code...");
  const qrData = await fetchQR();
  if (qrData.ret !== 0 || !qrData.qrcode) {
    console.error("Failed to get QR:", qrData);
    process.exit(1);
  }

  const qrcode = qrData.qrcode;
  const qrUrl = qrData.qrcode_img_content;
  console.log("QR code ID:", qrcode);
  console.log("QR URL:", qrUrl);

  // Save QR image
  await saveQRImage(qrUrl);
  console.log("\n========================================");
  console.log("请用微信扫码！图片路径:");
  console.log("http://127.0.0.1:18789/workspace/weixin-qr.png");
  console.log("========================================\n");

  // Poll for status
  let expired = 0;
  const maxExpired = 3;
  const startTime = Date.now();
  const maxWait = 8 * 60 * 1000; // 8 minutes

  while (Date.now() - startTime < maxWait) {
    await new Promise(r => setTimeout(r, 3000)); // poll every 3s

    // Refresh QR image each time too
    await saveQRImage(qrUrl);

    try {
      const status = await pollStatus(qrcode);
      console.log(`[${new Date().toLocaleTimeString()}] Status: ${status.status}`);

      switch (status.status) {
        case "wait":
          expired = 0;
          break;
        case "scaned":
          console.log("👀 已扫码，请在微信点确认...");
          break;
        case "expired":
          expired++;
          console.log(`⏳ 二维码过期 (${expired}/${maxExpired})，刷新中...`);
          if (expired >= maxExpired) {
            console.error("二维码过期次数过多，请重新运行脚本");
            process.exit(1);
          }
          // Get new QR
          const newQR = await fetchQR();
          qrcode = newQR.qrcode;
          await saveQRImage(newQR.qrcode_img_content);
          console.log("新二维码已保存，请重新扫描！");
          break;
        case "confirmed":
          console.log("\n🎉 登录成功！");
          saveCredentials({
            ilink_bot_id: status.ilink_bot_id!,
            bot_token: status.bot_token,
            baseurl: status.baseurl,
            ilink_user_id: status.ilink_user_id,
          });
          console.log("登录完成！可以关闭此窗口。");
          process.exit(0);
      }
    } catch (e) {
      console.error("Poll error:", e);
    }
  }

  console.error("超时未登录");
  process.exit(1);
}

main().catch(e => {
  console.error("Fatal error:", e);
  process.exit(1);
});
