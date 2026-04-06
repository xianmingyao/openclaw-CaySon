/**
 * AI Content Scraper - Uses Playwright Stealth approach
 * Extracts data from Bilibili and Douyin search pages
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'workspace', 'content-hunter', 'data');
const SCRAPER_DIR = 'E:\\workspace\\skills\\playwright-scraper-skill';

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Stealth browser launch
async function launchStealthBrowser() {
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage',
      '--no-sandbox'
    ]
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'zh-CN'
  });

  // Remove webdriver property
  const page = await context.newPage();
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
  });

  return { browser, page };
}

// Extract Bilibili video data from page
async function extractBilibiliVideos(page) {
  // Wait for content to load
  await page.waitForTimeout(3000);

  // Get all text content and parse it
  const content = await page.content();

  // Try multiple selector approaches
  const videos = await page.evaluate(() => {
    const results = [];

    // Try list items
    document.querySelectorAll('.video-item, .bili-video-card, .card').forEach(el => {
      const titleEl = el.querySelector('.title, .video-title, [class*="title"]');
      const authorEl = el.querySelector('.up-name, .author, [class*="author"]');
      const metaEl = el.querySelector('.meta, .stats, [class*="stat"]');

      if (titleEl) {
        results.push({
          title: titleEl.textContent.trim(),
          author: authorEl ? authorEl.textContent.trim() : '',
          meta: metaEl ? metaEl.textContent.trim() : ''
        });
      }
    });

    // Fallback: parse page text for video patterns
    if (results.length === 0) {
      const allText = document.body.innerText;
      const lines = allText.split('\n').filter(l => l.trim());
      let current = {};

      lines.forEach(line => {
        const trimmed = line.trim();
        // Look for title-like patterns (short, no special chars except punctuation)
        if (trimmed.length > 5 && trimmed.length < 100 && !trimmed.includes('取消') && !trimmed.includes('综合')) {
          if (!current.title && !trimmed.match(/^\d+\.\d+$/) && !trimmed.match(/^\d+万$/)) {
            current.title = trimmed;
          } else if (current.title && !current.author && trimmed.length < 20) {
            current.author = trimmed;
          } else if (current.title && current.author) {
            current.meta = trimmed;
            results.push({ ...current });
            current = {};
          }
        }
      });
    }

    return results;
  });

  return videos;
}

// Extract Douyin video data from page
async function extractDouyinVideos(page) {
  await page.waitForTimeout(4000);

  const videos = await page.evaluate(() => {
    const results = [];

    // Try to find video cards
    document.querySelectorAll('[class*="video"], [class*="card"], .search-card').forEach(el => {
      const titleEl = el.querySelector('[class*="title"], .title, img[alt]');
      const authorEl = el.querySelector('[class*="author"], .author, .name');
      const likeEl = el.querySelector('[class*="like"], [class*="count"], .count');

      if (titleEl) {
        results.push({
          title: (titleEl.textContent || titleEl.alt || '').trim(),
          author: authorEl ? authorEl.textContent.trim() : '',
          likes: likeEl ? likeEl.textContent.trim() : ''
        });
      }
    });

    return results;
  });

  return videos;
}

async function scrapePlatform(options) {
  const { name, url, extractFn, pages = 5 } = options;
  console.log(`\n🎬 开始抓取${name}...`);

  const allVideos = [];
  const seen = new Set();

  for (let page = 1; page <= pages && allVideos.length < 100; page++) {
    console.log(`  第 ${page}/${pages} 页...`);

    const pageUrl = page === 1 ? url : `${url}&page=${page}`;

    try {
      const { browser, page: p } = await launchStealthBrowser();
      await p.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });

      const videos = await extractFn(p);

      // Dedupe
      for (const v of videos) {
        if (v.title && !seen.has(v.title)) {
          seen.add(v.title);
          allVideos.push(v);
        }
      }

      console.log(`    本页 ${videos.length} 条，累计 ${allVideos.length} 条`);
      await browser.close();
      await new Promise(r => setTimeout(r, 3000));

    } catch (err) {
      console.log(`    页面 ${page} 出错: ${err.message}`);
    }
  }

  console.log(`  ${name}抓取完成: ${allVideos.length} 条`);
  return allVideos;
}

function generateSummary(title) {
  const t = title.toLowerCase();
  if (t.includes('教程') || t.includes('课程') || t.includes('学习')) {
    return '系统性AI教学类内容，讲解技术原理、工具使用或实战应用，适合学习者。';
  }
  if (t.includes('日报') || t.includes('新闻') || t.includes('最新')) {
    return 'AI资讯类内容，汇集行业最新动态、技术进展或产品发布。';
  }
  if (t.includes('解读') || t.includes('分析') || t.includes('评测')) {
    return '深度解读分析类内容，对AI技术或产品进行专业分析。';
  }
  if (t.includes('入门') || t.includes('基础') || t.includes('零基础')) {
    return '入门级AI科普内容，面向初学者讲解基本概念。';
  }
  if (t.includes('工具') || t.includes('软件')) {
    return 'AI工具推荐类内容，介绍实用的AI软件或平台。';
  }
  return 'AI相关热门内容，具有一定关注度和讨论价值。';
}

function formatBilibili(items, startNum = 1) {
  let md = '';
  items.forEach((item, i) => {
    const n = startNum + i;
    const views = item.meta?.match(/[\d.]+万|[亿万千百]/g)?.join('') || '-';
    md += `\n### 第${n}条\n`;
    md += `- 标题: ${item.title}\n`;
    md += `- UP主: ${item.author || '未知'}\n`;
    md += `- 播放: ${views}\n`;
    md += `- 弹幕: -\n`;
    md += `- 点赞: -\n`;
    md += `- 投币: -\n`;
    md += `- 收藏: -\n`;
    md += `- 字幕: 未知\n`;
    md += `- 内容总结: ${generateSummary(item.title)}\n`;
  });
  return md;
}

function formatDouyin(items, startNum = 1) {
  let md = '';
  items.forEach((item, i) => {
    const n = startNum + i;
    md += `\n### 第${n}条\n`;
    md += `- 标题: ${item.title}\n`;
    md += `- 作者: @${item.author || '未知'}\n`;
    md += `- 点赞: ${item.likes || '-'}\n`;
    md += `- 话题: #AI #人工智能\n`;
    md += `- 内容总结: ${generateSummary(item.title)}\n`;
  });
  return md;
}

async function main() {
  const timestamp = new Date().toISOString().slice(0, 16).replace('T', ' ');

  // Bilibili
  const biliUrl = 'https://search.bilibili.com/all?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&order=totalrank';
  const biliItems = await scrapePlatform({
    name: 'B站',
    url: biliUrl,
    extractFn: extractBilibiliVideos,
    pages: 6
  });

  // Append to bilibili.md
  const biliFile = path.join(DATA_DIR, 'bilibili.md');
  if (biliItems.length > 0) {
    fs.appendFileSync(biliFile, formatBilibili(biliItems));
    console.log(`✅ B站 ${biliItems.length} 条已追加`);
  }

  // Douyin
  const douyinUrl = 'https://so.douyin.com/search?keyword=AI%E6%99%BA%E8%83%BD&type=video';
  const douyinItems = await scrapePlatform({
    name: '抖音',
    url: douyinUrl,
    extractFn: extractDouyinVideos,
    pages: 6
  });

  // Append to douyin.md
  const douyinFile = path.join(DATA_DIR, 'douyin.md');
  if (douyinItems.length > 0) {
    fs.appendFileSync(douyinFile, formatDouyin(douyinItems));
    console.log(`✅ 抖音 ${douyinItems.length} 条已追加`);
  }

  console.log('\n🎉 任务完成!');
}

main().catch(console.error);
