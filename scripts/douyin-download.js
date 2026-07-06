const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const VIDEO_URL = process.argv[2] || 'https://v.douyin.com/PHhwKWZTJ-c/';
const OUTPUT_DIR = 'E:/workspace/scripts';

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
  
  // 创建自定义响应拦截器来捕获视频数据
  const videoChunks = [];
  let videoUrl = null;
  
  page.on('response', async response => {
    const url = response.url();
    const contentType = response.headers()['content-type'] || '';
    
    // 捕获视频响应
    if (url.includes('media-video') || url.includes('.mp4') || contentType.includes('video/mp4')) {
      console.log('📹 捕获到视频响应:', url.substring(0, 100));
      try {
        const buffer = await response.body();
        console.log('   大小:', buffer.length, 'bytes');
        videoChunks.push(buffer);
        if (!videoUrl) videoUrl = url;
      } catch (e) {
        console.log('   读取失败:', e.message);
      }
    }
    
    // 捕获音频响应
    if (url.includes('media-audio') || url.includes('.m4a') || contentType.includes('audio')) {
      console.log('🎵 捕获到音频响应:', url.substring(0, 100));
    }
  });
  
  await page.goto(VIDEO_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
  
  // 等待视频加载
  console.log('  等待视频加载...');
  await page.waitForTimeout(15000);
  
  // 尝试点击播放按钮
  try {
    await page.click('video', { timeout: 5000 }).catch(() => {});
    console.log('  点击播放按钮');
  } catch (e) {}
  
  await page.waitForTimeout(5000);
  
  // 保存视频数据
  if (videoChunks.length > 0) {
    const totalSize = videoChunks.reduce((acc, chunk) => acc + chunk.length, 0);
    console.log('\n📦 总共捕获', videoChunks.length, '个视频块, 总大小:', totalSize);
    
    // 合并并保存
    const videoBuffer = Buffer.concat(videoChunks);
    const outputPath = path.join(OUTPUT_DIR, 'douyin-captured-video.mp4');
    fs.writeFileSync(outputPath, videoBuffer);
    console.log('✅ 视频已保存到:', outputPath);
  } else {
    console.log('❌ 未捕获到视频数据');
  }
  
  // 获取页面信息
  const pageInfo = await page.evaluate(() => {
    return {
      title: document.querySelector('h1')?.textContent?.trim() || document.title,
      videoElements: document.querySelectorAll('video').length,
      hasVideo: !!document.querySelector('video')
    };
  });
  
  console.log('\n📋 页面信息:');
  console.log('  标题:', pageInfo.title);
  console.log('  视频元素:', pageInfo.videoElements);
  
  await browser.close();
})();
