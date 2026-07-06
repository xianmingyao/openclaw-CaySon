const { chromium } = require('playwright');

const VIDEO_URL = process.argv[2] || 'https://v.douyin.com/PHhwKWZTJ-c/';

(async () => {
  console.log('🚀 启动浏览器...');
  const browser = await chromium.launch({
    headless: false,
    args: ['--disable-blink-features=AutomationControlled']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();
  
  console.log('📱 打开抖音页面:', VIDEO_URL);
  await page.goto(VIDEO_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
  
  // 等待视频加载
  console.log('  等待页面渲染...');
  await page.waitForTimeout(10000);
  
  // 提取页面信息和所有媒体资源
  const pageInfo = await page.evaluate(() => {
    const title = document.querySelector('h1')?.textContent?.trim() ||
                  document.querySelector('[data-e2e="video-desc"]')?.textContent?.trim() ||
                  document.title;
    
    const authorEl = document.querySelector('[data-e2e="video-account-link"]') ||
                     document.querySelector('.author-name') ||
                     document.querySelector('[class*="author"]');
    const author = authorEl?.textContent?.trim();
    
    // 查找所有音频/视频资源
    const entries = performance.getEntriesByType('resource');
    
    // 筛选出抖音的媒体资源
    const mediaEntries = entries.filter(e => 
      e.name.includes('douyin') || 
      e.name.includes('byted') ||
      e.name.includes('lf-douyin') ||
      e.name.includes('tiktok') ||
      e.name.includes('media-audio') ||
      e.name.includes('media-video') ||
      e.name.includes('.mp3') ||
      e.name.includes('.mp4') ||
      e.name.includes('.m4a')
    );
    
    return {
      title,
      author,
      mediaEntries: mediaEntries.map(e => ({ 
        type: e.initiatorType, 
        name: e.name.substring(0, 500),
        duration: e.duration
      }))
    };
  });
  
  console.log('\n📋 页面信息:');
  console.log('  标题:', pageInfo.title);
  console.log('  作者:', pageInfo.author);
  console.log('\n📺 媒体资源:');
  pageInfo.mediaEntries.forEach((entry, i) => {
    console.log(`  [${i+1}] ${entry.type}: ${entry.name}`);
  });
  
  // 保存结果
  const fs = require('fs');
  const result = {
    url: VIDEO_URL,
    title: pageInfo.title,
    author: pageInfo.author,
    mediaEntries: pageInfo.mediaEntries,
    timestamp: new Date().toISOString()
  };
  
  fs.writeFileSync('E:/workspace/scripts/douyin-media-info.json', JSON.stringify(result, null, 2));
  console.log('\n✅ 信息已保存到 douyin-media-info.json');
  
  await browser.close();
})();
