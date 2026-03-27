const QRCode = require('C:/nvm4w/nodejs/node_modules/qrcode');
const url = process.argv[2];

QRCode.toFile('E:/workspace/weixin-qr.png', url, { width: 400, margin: 2 }, (err) => {
  if (err) { console.error(err); process.exit(1); }
  console.log('Saved! URL:', url);
});
