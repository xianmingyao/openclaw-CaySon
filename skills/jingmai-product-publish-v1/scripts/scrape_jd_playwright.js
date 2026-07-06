const { chromium } = require('playwright');

(async () => {
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
  
  // 商品名称 - 尝试多种选择器
  try {
    // 方式1: 搜索包含商品名的div
    const title1 = await page.$eval('[class*="sku-name"]', el => el.innerText).catch(() => null);
    const title2 = await page.$eval('[class*="product-title"]', el => el.innerText).catch(() => null);
    const title3 = await page.$eval('[class*="goods-title"]', el => el.innerText).catch(() => null);
    
    productInfo.title = title1 || title2 || title3 || 'Not found';
    console.log('Title:', productInfo.title);
  } catch (e) {
    console.log('Title error:', e.message);
  }
  
  // 价格
  try {
    const price = await page.$eval('[class*="price"]', el => el.innerText).catch(() => null);
    const price2 = await page.$eval('[class*="p-price"]', el => el.innerText).catch(() => null);
    productInfo.price = price || price2 || 'Not found';
    console.log('Price:', productInfo.price);
  } catch (e) {
    console.log('Price error:', e.message);
  }
  
  // 品牌
  try {
    const brand = await page.$eval('[class*="brand"]', el => el.innerText).catch(() => null);
    productInfo.brand = brand || 'Not found';
    console.log('Brand:', productInfo.brand);
  } catch (e) {
    console.log('Brand error:', e.message);
  }
  
  // 商品ID
  try {
    const id = await page.$eval('[class*="product-id"]', el => el.innerText).catch(() => null);
    productInfo.productId = id || '16793098028';
    console.log('Product ID:', productInfo.productId);
  } catch (e) {
    productInfo.productId = '16793098028';
  }
  
  // 店铺
  try {
    const shop = await page.$eval('[class*="shop-name"]', el => el.innerText).catch(() => null);
    const shop2 = await page.$eval('[class*="seller"]', el => el.innerText).catch(() => null);
    productInfo.shop = shop || shop2 || 'Not found';
    console.log('Shop:', productInfo.shop);
  } catch (e) {
    console.log('Shop error:', e.message);
  }
  
  // 规格参数
  try {
    const specs = {};
    const specItems = await page.$$('[class*="Ptable-item"]');
    for (const item of specItems) {
      const key = await item.$eval('dt', el => el.innerText).catch(() => '');
      const value = await item.$eval('dd', el => el.innerText).catch(() => '');
      if (key) specs[key] = value;
    }
    productInfo.specs = specs;
    console.log('Specs:', JSON.stringify(specs));
  } catch (e) {
    console.log('Specs error:', e.message);
  }
  
  // 输出完整信息
  console.log('\n' + '='.repeat(60));
  console.log('商品完整信息:');
  console.log('='.repeat(60));
  console.log(JSON.stringify(productInfo, null, 2));
  
  // 保存到文件
  const fs = require('fs');
  fs.writeFileSync(
    'E:\\workspace\\skills\\jingmai-product-publish\\logs\\jd_product_data.json',
    JSON.stringify(productInfo, null, 2),
    'utf8'
  );
  console.log('\n数据已保存到 jd_product_data.json');
  
  await browser.close();
})();
