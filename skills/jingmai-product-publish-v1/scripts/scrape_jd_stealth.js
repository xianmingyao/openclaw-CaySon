const { chromium } = require('E:/workspace/skills/playwright-scraper-skill/node_modules/playwright');

const url = 'https://item.jd.com/16793098028.html';

async function scrape() {
  console.log('Launching stealth browser...');
  
  const browser = await chromium.launch({ 
    headless: true,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '----disable-gpu',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process'
    ]
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  
  // Add stealth scripts
  const StealthScript = `
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => ['Chrome PDF Plugin', 'Chrome PDF Viewer'] });
    Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
    window.chrome = { runtime: {} };
  `;
  
  const page = await context.newPage();
  await page.addInitScript(StealthScript);
  
  console.log(`Navigating to: ${url}`);
  
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(5000);  // Wait for dynamic content
    
    // Extract product info
    const data = {};
    
    // Title
    try {
      const title = await page.$eval('[class*="sku-name"]', el => el.innerText.trim()).catch(() => null);
      data.title = title || await page.$eval('h1', el => el.innerText.trim()).catch(() => null);
    } catch(e) {
      data.title = null;
    }
    
    // Price - try multiple selectors
    try {
      const priceEl = await page.$('[class*="price"]');
      if (priceEl) {
        data.price = await priceEl.innerText();
      }
    } catch(e) {
      data.price = null;
    }
    
    // Shop name
    try {
      data.shop = await page.$eval('[class*="shop-name"]', el => el.innerText.trim()).catch(() => null);
    } catch(e) {
      data.shop = null;
    }
    
    // Brand
    try {
      data.brand = await page.$eval('[class*="brand"]', el => el.innerText.trim()).catch(() => null) || '公牛';
    } catch(e) {
      data.brand = '公牛';
    }
    
    // Get all text content
    data.allText = await page.evaluate(() => document.body.innerText.substring(0, 3000));
    
    // Screenshot
    await page.screenshot({ path: 'E:\\workspace\\skills\\jingmai-product-publish\\logs\\jd_stealth.png', fullPage: false });
    
    console.log('\n=== Product Data ===');
    console.log(JSON.stringify(data, null, 2));
    
    // Save to file
    const fs = require('fs');
    fs.writeFileSync('E:\\workspace\\skills\\jingmai-product-publish\\logs\\jd_product_full.json', JSON.stringify(data, null, 2));
    
  } catch(e) {
    console.error('Error:', e.message);
  }
  
  await browser.close();
  console.log('\nDone!');
}

scrape();
