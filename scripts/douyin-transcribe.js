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
  
  // 等待视频加载 - 抖音需要更多时间
  console.log('  等待页面渲染...');
  await page.waitForTimeout(8000);
  
  // 提取页面信息
  const pageInfo = await page.evaluate(() => {
    const title = document.querySelector('h1')?.textContent?.trim() ||
                  document.querySelector('[data-e2e="video-desc"]')?.textContent?.trim() ||
                  document.title;
    
    const authorEl = document.querySelector('[data-e2e="video-account-link"]') ||
                     document.querySelector('.author-name') ||
                     document.querySelector('[class*="author"]');
    const author = authorEl?.textContent?.trim();
    
    // 查找音频/视频资源
    const entries = performance.getEntriesByType('resource');
    const audioEntry = entries.find(e => e.name.includes('media-audio') || e.name.includes('aweme'));
    const videoEntry = entries.find(e => e.name.includes('media-video') || e.name.includes('.mp4'));
    
    return {
      title,
      author,
      audioUrl: audioEntry?.name || null,
      videoUrl: videoEntry?.name || null,
      allResources: entries.map(e => ({ type: e.initiatorType, name: e.name.substring(0, 200) }))
    };
  });
  
  console.log('\n📋 页面信息:');
  console.log('  标题:', pageInfo.title);
  console.log('  作者:', pageInfo.author);
  console.log('  音频URL:', pageInfo.audioUrl);
  console.log('  视频URL:', pageInfo.videoUrl);
  
  // 保存结果
  const result = {
    url: VIDEO_URL,
    title: pageInfo.title,
    author: pageInfo.author,
    audioUrl: pageInfo.audioUrl,
    videoUrl: pageInfo.videoUrl,
    timestamp: new Date().toISOString()
  };
  
  const fs = require('fs');
  fs.writeFileSync('E:/workspace/scripts/douyin-audio-info.json', JSON.stringify(result, null, 2));
  console.log('\n✅ 信息已保存到 douyin-audio-info.json');
  
  await browser.close();
})();
