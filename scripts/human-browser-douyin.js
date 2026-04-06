const {launchHuman, humanScroll, humanType, sleep} = require('C:/Users/Administrator/.agents/skills/human-browser/scripts/browser-human');

(async () => {
  const {page} = await launchHuman();
  console.log('Browser launched');
  
  // Test 抖音搜索
  await page.goto('https://www.douyin.com/search/AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD?type=video', {waitUntil:'domcontentloaded', timeout:30000});
  console.log('抖音页面加载完成');
  await sleep(5000);
  
  // 截图
  await page.screenshot({path:'C:/Users/Administrator/.openclaw/workspace/content-hunter/data/douyin_human.png'});
  console.log('抖音截图保存');
  
  // 提取内容
  const result = await page.evaluate(() => {
    const bodyText = document.body.innerText.substring(0, 5000);
    const url = window.location.href;
    return {url, textPreview: bodyText};
  });
  console.log('URL:', result.url);
  console.log('内容预览:', result.textPreview.substring(0, 2000));
  
  await page.close();
  process.exit(0);
})().catch(e => { console.error('Error:', e.message); process.exit(1); });
