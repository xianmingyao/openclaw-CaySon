/**
 * AI Content Scraper for Bilibili and Douyin
 * Scrapes AI-related videos from both platforms using Playwright Stealth
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'workspace', 'content-hunter', 'data');
const SCRAPER_DIR = 'E:\\workspace\\skills\\playwright-scraper-skill';

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

async function scrapeBilibili(pages = 5) {
  console.log('🟢 开始抓取B站AI内容...');
  const results = [];
  const seenTitles = new Set();

  for (let page = 1; page <= pages; page++) {
    console.log(`  抓取第 ${page}/${pages} 页...`);
    const url = `https://search.bilibili.com/all?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&order=totalrank&page=${page}`;

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    });
    const pageObj = await context.newPage();

    await pageObj.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await pageObj.waitForTimeout(3000);

    // Extract video cards
    const videoCards = await pageObj.$$eval('.bili-video-card', cards => {
      return cards.map(card => {
        const title = card.querySelector('.bili-video-card__info--title')?.textContent?.trim() || '';
        const author = card.querySelector('.bili-video-card__info--author')?.textContent?.trim() || '';
        const views = card.querySelector('.bili-video-card__stats--views')?.textContent?.trim() || '';
        const danmaku = card.querySelector('.bili-video-card__stats--danmaku')?.textContent?.trim() || '';
        const likes = card.querySelector('[data-append-at="likes"]')?.textContent?.trim() || '';
        const link = card.querySelector('a')?.href || '';

        return { title, author, views, danmaku, likes, link };
      });
    });

    // Also try to extract from list-item format
    const listItems = await pageObj.$$eval('.video-item', items => {
      return items.map(item => {
        const titleEl = item.querySelector('.title');
        const authorEl = item.querySelector('.up-name');
        const metaEl = item.querySelector('.meta');
        const link = item.querySelector('a')?.href || '';

        return {
          title: titleEl?.textContent?.trim() || '',
          author: authorEl?.textContent?.trim() || '',
          views: metaEl?.textContent?.trim() || '',
          link
        };
      }).filter(i => i.title);
    });

    // Combine and dedupe
    const allItems = [...videoCards, ...listItems];
    for (const item of allItems) {
      if (item.title && !seenTitles.has(item.title)) {
        seenTitles.add(item.title);
        results.push(item);
      }
    }

    await browser.close();

    if (results.length >= 100) break;
    await new Promise(r => setTimeout(r, 2000));
  }

  console.log(`  B站抓取完成，共 ${results.length} 条`);
  return results;
}

async function scrapeDouyin(pages = 5) {
  console.log('🔴 开始抓取抖音AI内容...');
  const results = [];
  const seenTitles = new Set();

  for (let page = 1; page <= pages; page++) {
    console.log(`  抓取第 ${page}/${pages} 页...`);
    const url = `https://so.douyin.com/search?keyword=AI%E6%99%BA%E8%83%BD&type=video&page_source=search_history&pd=sysec`;

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    });
    const pageObj = await context.newPage();

    await pageObj.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await pageObj.waitForTimeout(3000);

    // Try to extract video items
    const videoItems = await pageObj.$$eval('[data-e2e="video-item"]', items => {
      return items.map(item => {
        const title = item.querySelector('[data-e2e="video-title"]')?.textContent?.trim() ||
                      item.querySelector('.video-title')?.textContent?.trim() || '';
        const author = item.querySelector('[data-e2e="author-name"]')?.textContent?.trim() ||
                       item.querySelector('.author-name')?.textContent?.trim() || '';
        const likes = item.querySelector('[data-e2e="like-count"]')?.textContent?.trim() ||
                      item.querySelector('.like-count')?.textContent?.trim() || '';
        const link = item.querySelector('a')?.href || '';

        return { title, author, likes, link };
      }).filter(i => i.title);
    });

    // Generic fallback
    const genericItems = await pageObj.$$eval('.video-card, .search-card, [class*="video"]', items => {
      return items.map(item => {
        const title = item.querySelector('img[alt], .title, [class*="title"]')?.textContent?.trim() || '';
        const author = item.querySelector('.author, .name, [class*="author"]')?.textContent?.trim() || '';
        const meta = item.querySelector('.meta, [class*="meta"]')?.textContent?.trim() || '';
        const link = item.querySelector('a')?.href || '';

        if (title) return { title, author, likes: meta, link };
        return null;
      }).filter(Boolean);
    });

    const allItems = [...videoItems, ...genericItems];
    for (const item of allItems) {
      if (item.title && !seenTitles.has(item.title)) {
        seenTitles.add(item.title);
        results.push(item);
      }
    }

    await browser.close();

    if (results.length >= 100) break;
    await new Promise(r => setTimeout(r, 3000));
  }

  console.log(`  抖音抓取完成，共 ${results.length} 条`);
  return results;
}

function formatBilibiliMD(items, startNum = 1) {
  let md = '';
  items.forEach((item, idx) => {
    const num = startNum + idx;
    const summary = generateSummary(item.title, 'bilibili');
    md += `\n### 第${num}条\n`;
    md += `- 标题: ${item.title}\n`;
    md += `- UP主: ${item.author || '未知'}\n`;
    md += `- 播放: ${item.views || '-'}\n`;
    md += `- 弹幕: ${item.danmaku || '-'}\n`;
    md += `- 点赞: ${item.likes || '-'}\n`;
    md += `- 投币: -\n`;
    md += `- 收藏: -\n`;
    md += `- 字幕: 未知\n`;
    md += `- 内容总结: ${summary}\n`;
  });
  return md;
}

function formatDouyinMD(items, startNum = 1) {
  let md = '';
  items.forEach((item, idx) => {
    const num = startNum + idx;
    const summary = generateSummary(item.title, 'douyin');
    md += `\n### 第${num}条\n`;
    md += `- 标题: ${item.title}\n`;
    md += `- 作者: @${item.author || '未知'}\n`;
    md += `- 点赞: ${item.likes || '-'}\n`;
    md += `- 话题: #AI #人工智能\n`;
    md += `- 内容总结: ${summary}\n`;
  });
  return md;
}

function generateSummary(title, platform) {
  // Generate a brief summary based on the title
  const titleLC = title.toLowerCase();

  if (titleLC.includes('教程') || titleLC.includes('课程') || titleLC.includes('学习')) {
    return `系统性教学类视频，讲解AI技术原理、工具使用或实战应用，适合想要系统学习人工智能的学习者。`;
  }
  if (titleLC.includes('日报') || titleLC.includes('新闻') || titleLC.includes('最新')) {
    return `AI资讯类内容，汇集当日AI行业最新动态、技术进展或产品发布，信息密度高，适合关注AI行业的从业者。`;
  }
  if (titleLC.includes('解读') || titleLC.includes('分析') || titleLC.includes('评测')) {
    return `深度解读类视频，对AI技术、产品或现象进行专业分析，内容有一定深度，适合进阶学习者。`;
  }
  if (titleLC.includes('入门') || titleLC.includes('基础') || titleLC.includes('零基础')) {
    return `入门级AI科普内容，面向初学者讲解基本概念和入门路径，内容通俗易懂。`;
  }
  if (titleLC.includes('工具') || titleLC.includes('软件') || titleLC.includes('网站')) {
    return `AI工具推荐类内容，介绍实用的AI软件、平台或工具，实操性强，干货满满。`;
  }
  return `AI相关热门内容，涵盖人工智能技术、应用或资讯，${platform === 'bilibili' ? '在B站获得较高播放量' : '在抖音获得较高点赞量'}。`;
}

async function main() {
  const timestamp = new Date().toISOString().slice(0, 16).replace('T', ' ');

  try {
    // Scrape Bilibili
    const biliItems = await scrapeBilibili(8);
    const biliFile = path.join(DATA_DIR, 'bilibili.md');
    const biliHeader = fs.existsSync(biliFile)
      ? ''
      : `# B站热门内容\n\n> 抓取时间：${timestamp}\n`;
    fs.appendFileSync(biliFile, biliHeader + formatBilibiliMD(biliItems));
    console.log(`✅ B站 ${biliItems.length} 条已追加到 ${biliFile}`);

    // Scrape Douyin
    const douyinItems = await scrapeDouyin(8);
    const douyinFile = path.join(DATA_DIR, 'douyin.md');
    const douyinHeader = fs.existsSync(douyinFile)
      ? ''
      : `# 抖音热门内容\n\n> 抓取时间：${timestamp}\n`;
    fs.appendFileSync(douyinFile, douyinHeader + formatDouyinMD(douyinItems));
    console.log(`✅ 抖音 ${douyinItems.length} 条已追加到 ${douyinFile}`);

    console.log('\n🎉 抓取任务完成！');
  } catch (err) {
    console.error('❌ 抓取失败:', err.message);
    process.exit(1);
  }
}

main();
