// Get QR code and save as PNG
const { writeFileSync } = require("node:fs");

const API_BASE = "https://ilinkai.weixin.qq.com";

async function main() {
  const url = `${API_BASE}/ilink/bot/get_bot_qrcode?bot_type=3`;
  const res = await fetch(url, {
    headers: { "iLink-App-ClientVersion": "1" }
  });
  const data = await res.json();
  
  console.log("QR code response keys:", Object.keys(data));
  console.log("qrcode:", data.qrcode);
  console.log("qrcode_img_content type:", typeof data.qrcode_img_content);
  console.log("qrcode_img_content length:", data.qrcode_img_content?.length);
  
  // Check if it's a data URL (base64 image)
  if (data.qrcode_img_content?.startsWith("data:image")) {
    const base64 = data.qrcode_img_content.split(",")[1];
    writeFileSync("E:\\workspace\\weixin-qr.png", Buffer.from(base64, "base64"));
    console.log("QR code saved to E:\\workspace\\weixin-qr.png");
  } else if (data.qrcode_img_content) {
    // It's a URL or text
    writeFileSync("E:\\workspace\\weixin-qr-info.txt", data.qrcode_img_content, "utf8");
    console.log("Content saved to weixin-qr-info.txt");
    console.log("Content:", data.qrcode_img_content);
  }
}

main().catch(console.error);
