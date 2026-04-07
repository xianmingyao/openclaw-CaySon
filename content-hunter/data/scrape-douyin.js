const { launchHuman, sleep } = require('C:/Users/Administrator/.agents/skills/human-browser/scripts/browser-human');
const fs = require('fs');
const path = require('path');

async function scrapeDouyin() {
  console.log('启动浏览器...');
  // 禁用代理，直连
  process.env.HB_NO_PROXY = '1';
  const { browser, page } = await launchHuman({ mobile: true });
  
  try {
    console.log('打开抖音搜索页...');
    await page.goto('https://www.douyin.com/search/AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    await sleep(5000);
    
    // 检查验证码
    const captcha = await page.$('iframe');
    if (captcha) {
      console.log('检测到验证码，尝试处理...');
      await page.click('iframe');
      await sleep(3000);
    }
    
    // 截图看看页面状态
    await page.screenshot({ path: 'E:/workspace/content-hunter/data/douyin-screenshot.png' });
    console.log('截图已保存');
    
    // 等待内容加载
    await sleep(3000);
    
    // 尝试滚动加载更多内容
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.scrollBy(0, 500));
      await sleep(1000);
    }
    
    // 获取页面文本内容
    const content = await page.evaluate(() => {
      // 尝试获取iframe内的内容
      const iframes = document.querySelectorAll('iframe');
      let allText = document.body.innerText;
      
      // 也尝试获取shadow DOM内容
      function getShadowText(root) {
        let text = '';
        try {
          text += root.innerText || '';
        } catch(e) {}
        for (const node of root.querySelectorAll('*')) {
          try {
            if (node.shadowRoot) {
              text += getShadowText(node.shadowRoot);
            }
          } catch(e) {}
        }
        return text;
      }
      
      for (const iframe of iframes) {
        try {
          const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
          if (iframeDoc) {
            allText += '\n[IFRAME]: ' + iframeDoc.body.innerText;
          }
        } catch(e) {
          allText += '\n[IFRAME ERROR]: ' + e.message;
        }
      }
      
      return allText;
    });
    
    console.log('页面内容长度:', content.length);
    console.log('前2000字符:', content.slice(0, 2000));
    
    // 保存原始内容
    fs.writeFileSync('E:/workspace/content-hunter/data/douyin-raw.txt', content);
    console.log('原始内容已保存到 douyin-raw.txt');
    
    await page.screenshot({ path: 'E:/workspace/content-hunter/data/douyin-screenshot2.png' });
    
  } catch (error) {
    console.error('错误:', error.message);
    await page.screenshot({ path: 'E:/workspace/content-hunter/data/douyin-error.png' }).catch(() => {});
  } finally {
    await browser.close();
  }
}

scrapeDouyin().catch(console.error);
