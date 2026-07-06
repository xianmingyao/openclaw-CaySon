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
  console.log('  等待视频加载...');
  await page.waitForTimeout(10000);
  
  // 获取video元素的src
  const videoInfo = await page.evaluate(() => {
    const video = document.querySelector('video');
    if (!video) return { found: false };
    
    // 获取所有source
    const sources = [];
    video.querySelectorAll('source').forEach(s => sources.push(s.src));
    
    // 获取当前src
    const currentSrc = video.src || video.currentSrc || '';
    
    // 获取资源列表
    const entries = performance.getEntriesByType('resource')
      .filter(e => e.name.includes('douyinvod') || e.name.includes('mp4'))
      .map(e => ({ type: e.initiatorType, name: e.name }));
    
    return {
      found: true,
      src: currentSrc,
      sources: sources,
      entries: entries,
      videoDuration: video.duration,
      videoPaused: video.paused
    };
  });
  
  console.log('\n📹 视频信息:');
  console.log('  找到:', videoInfo.found);
  if (videoInfo.found) {
    console.log('  当前src:', videoInfo.src.substring(0, 200));
    console.log('  时长:', videoInfo.videoDuration);
    console.log('  暂停:', videoInfo.videoPaused);
    console.log('  sources:', videoInfo.sources);
    console.log('  资源条目:', JSON.stringify(videoInfo.entries, null, 2));
  }
  
  // 保存信息
  const fs = require('fs');
  fs.writeFileSync('E:/workspace/scripts/video-src-info.json', JSON.stringify(videoInfo, null, 2));
  
  await browser.close();
})();
