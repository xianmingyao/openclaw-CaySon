// Get QR code and save as PNG
import { writeFileSync } from "node:fs";

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
    writeFileSync("weixin-qr.png", Buffer.from(base64, "base64"));
    console.log("✅ QR code saved to weixin-qr.png");
  } else if (data.qrcode) {
    // It's a URL or text - save as text file
    writeFileSync("weixin-qr-info.txt", JSON.stringify(data, null, 2));
    console.log("QR code info saved to weixin-qr-info.txt");
    console.log("Content:", data.qrcode_img_content);
  }
}

main().catch(console.error);
