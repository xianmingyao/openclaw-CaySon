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
  
  // 拦截视频响应
  let videoResponse = null;
  let audioResponse = null;
  
  page.on('response', async response => {
    const url = response.url();
    
    // 捕获视频流
    if (url.includes('media-video-avc1') || url.includes('douyinvod.com') && url.includes('video')) {
      console.log('📹 捕获视频:', url.substring(0, 80));
      try {
        videoResponse = await response.body();
        console.log('   视频大小:', videoResponse.length, 'bytes');
      } catch (e) {
        console.log('   失败:', e.message);
      }
    }
    
    // 捕获音频流
    if (url.includes('media-audio') || url.includes('douyinvod.com') && url.includes('audio')) {
      console.log('🎵 捕获音频:', url.substring(0, 80));
      try {
        audioResponse = await response.body();
        console.log('   音频大小:', audioResponse.length, 'bytes');
      } catch (e) {
        console.log('   失败:', e.message);
      }
    }
  });
  
  await page.goto(VIDEO_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
  
  // 等待视频加载并开始播放
  console.log('  等待视频加载...');
  await page.waitForTimeout(15000);
  
  // 点击播放
  try {
    await page.click('video');
    console.log('  已点击播放');
  } catch (e) {}
  
  // 等待更多时间让视频缓冲
  await page.waitForTimeout(10000);
  
  // 保存视频
  if (videoResponse) {
    const videoPath = path.join(OUTPUT_DIR, 'douyin-full-video.mp4');
    fs.writeFileSync(videoPath, videoResponse);
    console.log('✅ 视频已保存:', videoPath);
  } else {
    console.log('❌ 未捕获到视频');
  }
  
  // 保存音频
  if (audioResponse) {
    const audioPath = path.join(OUTPUT_DIR, 'douyin-audio.m4a');
    fs.writeFileSync(audioPath, audioResponse);
    console.log('✅ 音频已保存:', audioPath);
  } else {
    console.log('❌ 未捕获到音频');
  }
  
  // 获取页面标题
  const title = await page.evaluate(() => {
    return document.querySelector('h1')?.textContent?.trim() || document.title;
  });
  console.log('\n📋 标题:', title);
  
  await browser.close();
})();
