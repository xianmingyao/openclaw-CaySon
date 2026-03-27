// Script to keep fetching QR code and save as image
const QRCode = require('C:/nvm4w/nodejs/node_modules/qrcode');
const https = require('node:https');
const { writeFileSync } = require('node:fs');

const API_URL = 'https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3';
const OUT_FILE = 'E:/workspace/weixin-qr.png';

async function fetchQr() {
  const res = await fetch(API_URL, {
    headers: { 'iLink-App-ClientVersion': '1' }
  });
  const data = await res.json();
  return data.qrcode_img_content;
}

async function main() {
  console.log('Fetching QR code...');
  const url = await fetchQr();
  console.log('QR URL:', url);
  await QRCode.toFile(OUT_FILE, url, { width: 400, margin: 2 });
  console.log('QR saved to', OUT_FILE);
  console.log('Open: http://127.0.0.1:18789/workspace/weixin-qr.png');
}

main().catch(console.error);
