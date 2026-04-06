const {launchHuman, humanScroll, humanType, sleep} = require('C:/Users/Administrator/.agents/skills/human-browser/scripts/browser-human');

(async () => {
  const {page} = await launchHuman();
  console.log('Browser launched');
  
  // Test B站
  await page.goto('https://search.bilibili.com/all?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&order=totalrank', {waitUntil:'domcontentloaded', timeout:30000});
  console.log('B站页面加载完成');
  await sleep(3000);
  
  // 截图
  await page.screenshot({path:'C:/Users/Administrator/.openclaw/workspace/content-hunter/data/bilibili_human.png'});
  console.log('B站截图保存');
  
  // 提取内容
  const result = await page.evaluate(() => {
    const items = document.querySelectorAll('.video-item');
    const bodyText = document.body.innerText.substring(0, 3000);
    return {itemCount: items.length, textPreview: bodyText};
  });
  console.log('Items:', JSON.stringify(result));
  
  await page.close();
  process.exit(0);
})().catch(e => { console.error('Error:', e.message); process.exit(1); });
