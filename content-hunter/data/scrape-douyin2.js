const { launchHuman, sleep } = require('C:/Users/Administrator/.agents/skills/human-browser/scripts/browser-human');
const fs = require('fs');

async function scrapeDouyin() {
  console.log('启动浏览器（桌面模式）...');
  process.env.HB_NO_PROXY = '1';
  const { browser, page } = await launchHuman({ mobile: false });
  
  try {
    console.log('打开抖音WAP版...');
    // WAP版更容易抓取
    await page.goto('https://www.douyin.com/wap/search?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD', { 
      waitUntil: 'domcontentloaded',
      timeout: 30000 
    });
    
    await sleep(5000);
    
    // 获取页面内容
    const content = await page.evaluate(() => {
      return document.body.innerText;
    });
    
    console.log('页面文本长度:', content.length);
    console.log('前3000字符:');
    console.log(content.slice(0, 3000));
    
    fs.writeFileSync('E:/workspace/content-hunter/data/douyin-wap.txt', content);
    console.log('已保存到 douyin-wap.txt');
    
    await page.screenshot({ path: 'E:/workspace/content-hunter/data/douyin-wap.png' });
    console.log('截图已保存');
    
  } catch (error) {
    console.error('错误:', error.message);
    await page.screenshot({ path: 'E:/workspace/content-hunter/data/douyin-error2.png' }).catch(() => {});
  } finally {
    await browser.close();
  }
}

scrapeDouyin().catch(console.error);
