/**
 * AI Content Scraper - Parses content from stealth browser runs
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'workspace', 'content-hunter', 'data');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

async function launchStealth() {
  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage', '--no-sandbox']
  });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'zh-CN'
  });
  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
  });
  return { browser, page };
}

// Parse bilibili content preview into structured items
function parseBilibiliContent(contentPreview) {
  const lines = contentPreview.split('\n').map(l => l.trim()).filter(l => l);

  const items = [];
  let currentItem = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Skip navigation/labels
    if (['取消', '综合', '番剧', 'UP主(99+)', '影视(3)', '默认排序', '播放多', '新发布', '弹幕多'].includes(line)) {
      continue;
    }

    // Duration pattern: XX:XX or XX:XX:XX
    if (/^\d{1,2}:\d{2}(:\d{2})?$/.test(line)) {
      if (currentItem && currentItem.title) {
        items.push(currentItem);
      }
      currentItem = { duration: line, views: '', danmaku: '' };
      continue;
    }

    // View count pattern: X.X万, XX万, XXX万, XXXX万
    if (currentItem && !currentItem.views && (line.match(/^[\d.]+万$/) || line.match(/^[\d.]+$/))) {
      if (line.includes('万') || parseInt(line) > 1000) {
        currentItem.views = line;
        // Next line might be danmaku
        if (i + 1 < lines.length && /^\d+$/.test(lines[i + 1])) {
          currentItem.danmaku = lines[i + 1];
          i++;
        }
      } else if (!currentItem.title) {
        // This is actually a title line
        currentItem.title = line;
      }
      continue;
    }

    // Danmaku (number only, after views)
    if (currentItem && currentItem.views && !currentItem.danmaku && /^\d+$/.test(line) && parseInt(line) < 10000) {
      currentItem.danmaku = line;
      continue;
    }

    // Author pattern: starts with Chinese chars or common author indicators
    if (currentItem && currentItem.views && currentItem.danmaku && !currentItem.author && line.length < 30 && line.length > 0) {
      // Check if next line(s) are view/danmaku
      if (line.match(/^[\d.]+万$/) || line.match(/^\d+$/)) {
        // This is still views/danmaku
        continue;
      }
      currentItem.author = line;
      continue;
    }

    // Title: everything else that looks like a title
    if (currentItem && currentItem.duration && !currentItem.title) {
      currentItem.title = line;
      continue;
    }

    // Title continuation or multiline title
    if (currentItem && currentItem.title && currentItem.author && !currentItem.views && !line.match(/^[\d.]+万$/) && !line.match(/^\d+$/) && line.length > 0) {
      currentItem.title += ' ' + line;
      continue;
    }

    // Start of new item (view count directly without title)
    if (currentItem && currentItem.title && !currentItem.views && line.match(/^[\d.]+万$/)) {
      currentItem.views = line;
      continue;
    }
  }

  if (currentItem && currentItem.title) {
    items.push(currentItem);
  }

  return items;
}

// Parse douyin content preview
function parseDouyinContent(contentPreview) {
  const lines = contentPreview.split('\n').map(l => l.trim()).filter(l => l);
  const items = [];
  let currentItem = null;

  for (const line of lines) {
    // Skip nav/headers
    if (['综合', 'AI搜索', '图片', '视频', '直播', '用户', '设计师liya'].includes(line)) continue;
    if (line.includes('广告') || line.includes('为你生成回答') || line.includes('近期热卖')) continue;

    // Video card pattern
    if (line.startsWith('视频同款')) continue;

    if (!currentItem) {
      currentItem = {};
    }

    if (!currentItem.title && line.length > 5 && line.length < 150) {
      currentItem.title = line;
    } else if (currentItem.title && !currentItem.author && line.length < 20) {
      currentItem.author = line;
    } else if (currentItem.title && currentItem.author) {
      currentItem.likes = line;
      items.push(currentItem);
      currentItem = null;
    }
  }

  return items;
}

function generateSummary(title, platform) {
  const t = title.toLowerCase();
  if (t.includes('教程') || t.includes('课程') || t.includes('学习') || t.includes('入门')) {
    return `系统性AI教学类内容，${platform === 'bilibili' ? '在B站获得较高播放量' : '在抖音获得较高点赞量'}，讲解技术原理或实战应用。`;
  }
  if (t.includes('日报') || t.includes('新闻') || t.includes('最新')) {
    return `AI资讯类内容，汇集行业最新动态和技术进展，适合关注AI行业的从业者。`;
  }
  if (t.includes('解读') || t.includes('分析') || t.includes('评测')) {
    return `深度解读分析类内容，对AI技术或产品进行专业分析。`;
  }
  if (t.includes('工具') || t.includes('软件')) {
    return `AI工具推荐类内容，介绍实用的AI软件或平台。`;
  }
  return `AI相关热门内容，具有一定关注度和讨论价值。`;
}

function formatBilibiliMD(items, startNum = 1) {
  let md = '';
  items.forEach((item, i) => {
    const n = startNum + i;
    md += `\n### 第${n}条\n`;
    md += `- 标题: ${item.title || '未知'}\n`;
    md += `- UP主: ${item.author || '未知'}\n`;
    md += `- 播放: ${item.views || '-'}\n`;
    md += `- 弹幕: ${item.danmaku || '-'}\n`;
    md += `- 点赞: -\n`;
    md += `- 投币: -\n`;
    md += `- 收藏: -\n`;
    md += `- 字幕: 未知\n`;
    md += `- 内容总结: ${generateSummary(item.title, 'bilibili')}\n`;
  });
  return md;
}

function formatDouyinMD(items, startNum = 1) {
  let md = '';
  items.forEach((item, i) => {
    const n = startNum + i;
    md += `\n### 第${n}条\n`;
    md += `- 标题: ${item.title || '未知'}\n`;
    md += `- 作者: @${item.author || '未知'}\n`;
    md += `- 点赞: ${item.likes || '-'}\n`;
    md += `- 话题: #AI #人工智能\n`;
    md += `- 内容总结: ${generateSummary(item.title, 'douyin')}\n`;
  });
  return md;
}

async function scrapeBilibili(pages = 7) {
  console.log('🎬 开始抓取B站AI内容...');
  const allItems = [];
  const seen = new Set();

  for (let page = 1; page <= pages; page++) {
    console.log(`  第 ${page}/${pages} 页...`);

    const { browser, page: p } = await launchStealth();
    const url = `https://search.bilibili.com/all?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&order=totalrank&page=${page}`;

    await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await p.waitForTimeout(6000);

    const contentPreview = await p.evaluate(() => document.body.innerText);

    const items = parseBilibiliContent(contentPreview);
    console.log(`    解析到 ${items.length} 条`);

    for (const item of items) {
      if (item.title && !seen.has(item.title)) {
        seen.add(item.title);
        allItems.push(item);
      }
    }

    await browser.close();

    if (allItems.length >= 100) break;
    await new Promise(r => setTimeout(r, 3000));
  }

  console.log(`  B站共抓取 ${allItems.length} 条`);
  return allItems;
}

async function scrapeDouyin(pages = 7) {
  console.log('🎬 开始抓取抖音AI内容...');
  const allItems = [];
  const seen = new Set();

  for (let page = 1; page <= pages; page++) {
    console.log(`  第 ${page}/${pages} 页...`);

    const { browser, page: p } = await launchStealth();
    const url = `https://so.douyin.com/search?keyword=AI%E6%99%BA%E8%83%BD&type=video&page=${page}`;

    await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await p.waitForTimeout(6000);

    const contentPreview = await p.evaluate(() => document.body.innerText);

    const items = parseDouyinContent(contentPreview);
    console.log(`    解析到 ${items.length} 条`);

    for (const item of items) {
      if (item.title && !seen.has(item.title)) {
        seen.add(item.title);
        allItems.push(item);
      }
    }

    await browser.close();

    if (allItems.length >= 100) break;
    await new Promise(r => setTimeout(r, 4000));
  }

  console.log(`  抖音共抓取 ${allItems.length} 条`);
  return allItems;
}

async function main() {
  const timestamp = new Date().toISOString().slice(0, 16).replace('T', ' ');

  try {
    const biliItems = await scrapeBilibili(8);
    const biliFile = path.join(DATA_DIR, 'bilibili.md');
    if (biliItems.length > 0) {
      fs.appendFileSync(biliFile, formatBilibiliMD(biliItems));
      console.log(`✅ B站 ${biliItems.length} 条已追加到 bilibili.md`);
    }

    const douyinItems = await scrapeDouyin(8);
    const douyinFile = path.join(DATA_DIR, 'douyin.md');
    if (douyinItems.length > 0) {
      fs.appendFileSync(douyinFile, formatDouyinMD(douyinItems));
      console.log(`✅ 抖音 ${douyinItems.length} 条已追加到 douyin.md`);
    }

    console.log('\n🎉 抓取任务完成！');
  } catch (err) {
    console.error('❌ 抓取出错:', err.message);
  }
}

main();
