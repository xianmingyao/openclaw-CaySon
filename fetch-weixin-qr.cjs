// Fetch QR code from WeChat API and save as image + URL file
const { writeFileSync } = require('node:fs');
const QRCode = require('C:/nvm4w/nodejs/node_modules/qrcode');

const API_URL = 'https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3';
const QR_FILE = 'E:/workspace/weixin-qr.png';
const URL_FILE = 'E:/workspace/weixin-qr-url.txt';

async function main() {
  // Fetch QR code from API
  const res = await fetch(API_URL, {
    headers: { 'iLink-App-ClientVersion': '1' }
  });
  const data = await res.json();
  const url = data.qrcode_img_content;
  const qrcode = data.qrcode;

  // Save URL to file (for reference)
  writeFileSync(URL_FILE, url);
  writeFileSync('E:/workspace/weixin-qrcode-id.txt', qrcode);

  // Generate PNG image
  await QRCode.toFile(QR_FILE, url, { width: 400, margin: 2 });
  console.log(`QR saved! ID: ${qrcode}`);
  console.log(`URL: ${url}`);
  console.log('Open: http://127.0.0.1:18789/workspace/weixin-qr.png');
}

main().catch(console.error);
