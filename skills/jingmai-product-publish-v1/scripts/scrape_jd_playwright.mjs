import { chromium } from 'playwright';

const url = 'https://item.jd.com/16793098028.html';

console.log('Launching browser...');
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 2560, height: 1392 }
});
const page = await context.newPage();

console.log(`Navigating to: ${url}`);
await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

// 等待页面加载
await page.waitForTimeout(3000);

// 提取商品信息
const productInfo = {};

// 商品名称
try {
  const title1 = await page.$eval('[class*="sku-name"]', el => el.innerText).catch(() => null);
  const title2 = await page.$eval('[class*="product-title"]', el => el.innerText).catch(() => null);
  productInfo.title = title1 || title2 || 'Not found';
  console.log('Title:', productInfo.title.substring(0, 50));
} catch (e) {
  console.log('Title error:', e.message);
}

// 价格
try {
  const price = await page.$eval('[class*="price"]', el => el.innerText).catch(() => null);
  productInfo.price = price || 'Not found';
  console.log('Price:', productInfo.price);
} catch (e) {
  console.log('Price error:', e.message);
}

// 品牌
try {
  const brand = await page.$eval('[class*="brand"] a', el => el.innerText).catch(() => null);
  productInfo.brand = brand || 'Not found';
  console.log('Brand:', productInfo.brand);
} catch (e) {
  console.log('Brand error:', e.message);
}

productInfo.productId = '16793098028';

// 规格参数
try {
  const specs = {};
  const specSection = await page.$('[class*="Ptable"]');
  if (specSection) {
    const items = await specSection.$$('[class*="Ptable-item"]');
    for (const item of items) {
      const keyEl = await item.$('dt');
      const valueEl = await item.$('dd');
      if (keyEl && valueEl) {
        const key = await keyEl.innerText();
        const value = await valueEl.innerText();
        specs[key] = value;
      }
    }
  }
  productInfo.specs = specs;
  console.log('Specs count:', Object.keys(specs).length);
} catch (e) {
  console.log('Specs error:', e.message);
}

console.log('\n' + '='.repeat(60));
console.log('商品信息:');
console.log('='.repeat(60));
console.log(JSON.stringify(productInfo, null, 2, null, 2));

// 保存到文件
const fs = await import('fs');
fs.writeFileSync(
  'E:\\workspace\\skills\\jingmai-product-publish\\logs\\jd_product_data.json',
  JSON.stringify(productInfo, null, 2),
  'utf8'
);
console.log('\n数据已保存');

await browser.close();
