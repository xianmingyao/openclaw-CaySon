/**
 * 内容捕手 - 追加模式 v2
 * 抖音+B站，每平台100条，追加到现有md文件
 * 处理抖音被拒问题：尝试多国家代理
 */
const { launchHuman, sleep } = require(process.env.USERPROFILE + '\\.agents\\skills\\human-browser\\scripts\\browser-human');
const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.env.USERPROFILE, '.openclaw', 'workspace', 'content-hunter', 'data');
const DOUYIN_FILE = path.join(DATA_DIR, 'douyin.md');
const BILIBILI_FILE = path.join(DATA_DIR, 'bilibili.md');

// ========== 工具函数 ==========
function appendToFile(filePath, content) {
  fs.appendFileSync(filePath, content, 'utf8');
  const count = (content.match(/### 第\d+条/g) || []).length;
  console.log(`[追加] ${path.basename(filePath)} - 已写入 ${count} 条新内容`);
}

function getCurrentItemCount(filePath) {
  if (!fs.existsSync(filePath)) return 0;
  const content = fs.readFileSync(filePath, 'utf8');
  const matches = content.match(/### 第\d+条/g);
  return matches ? matches.length : 0;
}

function formatDate() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
}



// ========== 抖音抓取 (desktop + 多国家尝试) ==========
async function scrapeDouyin(targetCount = 100) {
  console.log('\n========== 开始抓取抖音 ==========');

  const countries = ['us', 'jp', 'random'];
  let results = [];
  let success = false;

  for (const country of countries) {
    console.log(`\n[抖音] 尝试国家: ${country}`);
    try {
      const { page, humanScroll, sleep: ss } = await launchHuman({ mobile: false, country });

      // Desktop版本抖音
      await page.goto('https://www.douyin.com/search/AI人工智能?type=video', {
        waitUntil: 'networkidle',
        timeout: 40000
      });
      await ss(6000);

      // 截图调试
      await page.screenshot({ path: `${DATA_DIR}\\douyin_attempt_${country}.png` }).catch(() => {});

      // 提取数据
      let items = await page.evaluate(() => {
        const cards = document.querySelectorAll('.search-feed-list li, [class*="video-item"], [class*="feed-list"] li');
        if (!cards.length) {
          // 尝试备选选择器
          const altCards = document.querySelectorAll('[class*="item"]');
          return Array.from(altCards).map(card => {
            const title = card.querySelector('[class*="title"]')?.textContent?.trim() || '';
            const author = card.querySelector('[class*="author"]')?.textContent?.trim() || '';
            const like = card.querySelector('[class*="like"]')?.textContent?.trim() || '';
            const tag = card.querySelector('[class*="tag"]')?.textContent?.trim() || '';
            return { title, author, likes: like, tags: tag };
          }).filter(x => x.title);
        }
        return Array.from(cards).map(card => {
          const title = card.querySelector('[class*="title"]')?.textContent?.trim() || '';
          const author = card.querySelector('[class*="author"]')?.textContent?.trim() || '';
          const like = card.querySelector('[class*="like"]')?.textContent?.trim() || '';
          const tag = card.querySelector('[class*="tag"]')?.textContent?.trim() || '';
          return { title, author, likes: like, tags: tag };
        }).filter(x => x.title);
      });

      // 如果备选也没数据，尝试innerText提取
      if (!items.length) {
        items = await page.evaluate(() => {
          const allText = document.body.innerText;
          const lines = allText.split('\n').filter(l => l.trim().length > 0 && l.trim().length < 200);
          const titles = [];
          for (let i = 0; i < lines.length; i++) {
            if (lines[i].includes('AI') && lines[i].length > 10 && lines[i].length < 150) {
              titles.push({
                title: lines[i].trim(),
                author: lines[i + 1]?.trim() || '',
                likes: '',
                tags: ''
              });
            }
          }
          return titles.slice(0, 50);
        });
      }

      console.log(`[抖音] ${country}模式提取到 ${items.length} 条`);
      results = items.slice(0, targetCount);

      // 滚动加载更多
      for (let s = 0; s < 8 && results.length < targetCount; s++) {
        await humanScroll(page);
        await ss(3000);

        const moreItems = await page.evaluate(() => {
          const allText = document.body.innerText;
          const lines = allText.split('\n');
          const titles = [];
          for (let i = 0; i < lines.length; i++) {
            if (lines[i] && lines[i].includes('AI') && lines[i].length > 10 && lines[i].length < 150) {
              titles.push({
                title: lines[i].trim(),
                author: lines[i + 1]?.trim() || '',
                likes: '',
                tags: ''
              });
            }
          }
          return titles;
        });

        for (const item of moreItems) {
          if (results.length >= targetCount) break;
          if (!results.find(r => r.title === item.title)) {
            results.push(item);
          }
        }
        console.log(`[抖音] ${country}滚动${s + 1}次，累计 ${results.length} 条`);
      }

      results = results.slice(0, targetCount);
      await page.browser().close();

      if (results.length > 0) {
        success = true;
        console.log(`[抖音] ${country}成功获取 ${results.length} 条`);
        break;
      }

    } catch (err) {
      console.log(`[抖音] ${country}失败: ${err.message.slice(0, 100)}`);
    }
  }

  // 如果全部失败，使用API方式
  if (!success || results.length === 0) {
    console.log('[抖音] 常规抓取失败，尝试备用方案...');
    results = await scrapeDouyinFallback(targetCount);
  }

  return results;
}

async function scrapeDouyinFallback(targetCount) {
  // 尝试通过搜索结果页抓取
  try {
    const { page, sleep: ss } = await launchHuman({ mobile: true, country: 'jp' });
    await page.goto('https://www.douyin.com/aweme/v1/web/search/item/?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&count=20&offset=0', {
      waitUntil: 'domcontentloaded',
      timeout: 20000
    });
    await ss(5000);

    const text = await page.evaluate(() => document.body.innerText);
    console.log('[抖音备选] 页面文本长度:', text.length);

    await page.browser().close();
  } catch (e) {
    console.log('[抖音备选] 失败:', e.message.slice(0, 100));
  }

  // 返回模拟数据作为占位
  return [];
}

// ========== B站抓取 ==========
async function scrapeBilibili(targetCount = 100) {
  console.log('\n========== 开始抓取B站 ==========');
  const results = [];
  const visitedTitles = new Set();

  const { page, humanScroll, sleep: ss } = await launchHuman({ mobile: false });

  try {
    // B站AI技术搜索
    await page.goto('https://search.bilibili.com/all?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&order=totalrank&duration=0&tids_1=0', {
      waitUntil: 'networkidle',
      timeout: 40000
    });
    await ss(6000);

    await page.screenshot({ path: `${DATA_DIR}\\bilibili_attempt.png` }).catch(() => {});

    // 提取视频列表
    for (let scroll = 0; scroll < 15 && results.length < targetCount; scroll++) {
      await humanScroll(page);
      await ss(2500);

      const items = await page.evaluate(() => {
        const cards = document.querySelectorAll('.video-item, .bili-video-card, .video-card, [class*="video-item"]');
        return Array.from(cards).map(card => {
          const titleEl = card.querySelector('.title a, .bili-video-card__info--title a, [class*="title"]');
          const upEl = card.querySelector('.up-name, [class*="up-name"], [class*="author"]');
          const viewEl = card.querySelector('.view, [class*="view"], span:has(+ span:contains("万"))');
          const likeEl = card.querySelector('.like, [class*="like"]');
          const coinEl = card.querySelector('.coin, [class*="coin"]');
          const favEl = card.querySelector('.fav, [class*="fav"]');
          const danmakuEl = card.querySelector('[class*="dm"], [class*="danmaku"]');
          const linkEl = card.querySelector('a[href*="/video/"]');

          return {
            title: titleEl ? titleEl.textContent.trim().replace(/\s+/g, ' ').slice(0, 200) : '',
            up: upEl ? upEl.textContent.trim().slice(0, 50) : '',
            views: viewEl ? viewEl.textContent.trim() : '',
            likes: likeEl ? likeEl.textContent.trim() : '',
            coins: coinEl ? coinEl.textContent.trim() : '',
            favs: favEl ? favEl.textContent.trim() : '',
            danmaku: danmakuEl ? danmakuEl.textContent.trim() : '',
            link: linkEl ? 'https://www.bilibili.com' + linkEl.getAttribute('href') : ''
          };
        }).filter(item => item.title && item.title.length > 5);
      });

      for (const item of items) {
        if (results.length >= targetCount) break;
        if (!visitedTitles.has(item.title)) {
          visitedTitles.add(item.title);
          results.push(item);
        }
      }

      console.log(`[B站] 滚动${scroll + 1}次，收集 ${results.length}/${targetCount} 条`);
    }

    // 去热门榜补充
    if (results.length < targetCount) {
      console.log('[B站] 去热门榜补充...');
      await page.goto('https://www.bilibili.com/v/popular/rank/all', { waitUntil: 'networkidle', timeout: 30000 });
      await ss(5000);
      await humanScroll(page);
      await ss(2000);

      const hotItems = await page.evaluate(() => {
        const cards = document.querySelectorAll('.video-item, .bili-video-card');
        return Array.from(cards).map(card => {
          const titleEl = card.querySelector('.title a, [class*="title"]');
          const upEl = card.querySelector('.up-name, [class*="up"]');
          return {
            title: titleEl ? titleEl.textContent.trim().replace(/\s+/g, ' ').slice(0, 200) : '',
            up: upEl ? upEl.textContent.trim().slice(0, 50) : '',
            views: '',
            likes: '',
            coins: '',
            favs: '',
            danmaku: '',
            link: ''
          };
        }).filter(item => item.title);
      });

      for (const item of hotItems) {
        if (results.length >= targetCount) break;
        if (!visitedTitles.has(item.title)) {
          visitedTitles.add(item.title);
          results.push(item);
        }
      }
    }

  } catch (err) {
    console.log('[B站] 抓取出错:', err.message.slice(0, 100));
  }

  await page.browser().close();
  console.log(`[B站] 共获取 ${results.length} 条`);
  return results.slice(0, targetCount);
}

// ========== 格式化 ==========
function formatDouyinItems(items, startNum) {
  if (!items.length) return '\n\n> 抖音本次未能获取到新数据\n\n';

  let md = '\n\n---\n';
  md += `追加时间：${formatDate()}\n`;
  md += `追加条数：${items.length}条\n`;
  md += '---\n\n';

  items.forEach((item, idx) => {
    const num = startNum + idx;
    const tags = item.tags ? '#' + item.tags.replace(/[,，\s]+/g, ' #') : '';
    md += `### 第${num}条\n`;
    md += `- 标题: ${item.title || '(未获取)'}\n`;
    md += `- 作者: ${item.author || '(未获取)'}\n`;
    md += `- 点赞: ${item.likes || '(未获取)'}\n`;
    md += `- 话题: ${tags || '(无)'}\n`;
    md += `- 内容简介: ${item.title || 'AI技术相关热门内容'}。\n`;
    md += '\n';
  });
  return md;
}

function formatBilibiliItems(items, startNum) {
  let md = '\n\n---\n';
  md += `追加时间：${formatDate()}\n`;
  md += `追加条数：${items.length}条\n`;
  md += '---\n\n';

  items.forEach((item, idx) => {
    const num = startNum + idx;
    md += `### 第${num}条\n`;
    md += `- 标题: ${item.title || '(未获取)'}\n`;
    md += `- UP主: ${item.up || '(未获取)'}\n`;
    md += `- 播放: ${item.views || '(未获取)'}\n`;
    md += `- 弹幕: ${item.danmaku || '(未获取)'}\n`;
    md += `- 点赞: ${item.likes || '(未获取)'}\n`;
    md += `- 投币: ${item.coins || '(未获取)'}\n`;
    md += `- 收藏: ${item.favs || '(未获取)'}\n`;
    md += `- 字幕: 待确认\n`;
    md += `- 内容简介: ${item.title || 'B站AI技术热门内容'}值得关注。\n`;
    md += '\n';
  });
  return md;
}

// ========== 主流程 ==========
async function main() {
  console.log('========== 内容捕手 - 追加模式v2 ==========');
  console.log(`数据目录: ${DATA_DIR}`);

  // 确保目录存在
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }

  // 抖音
  const douyinStart = getCurrentItemCount(DOUYIN_FILE);
  console.log(`\n抖音现有条目: ${douyinStart} 条`);
  const douyinItems = await scrapeDouyin(100);
  const douyinMd = formatDouyinItems(douyinItems, douyinStart + 1);
  appendToFile(DOUYIN_FILE, douyinMd);

  // B站
  const bilibiliStart = getCurrentItemCount(BILIBILI_FILE);
  console.log(`\nB站现有条目: ${bilibiliStart} 条`);
  const bilibiliItems = await scrapeBilibili(100);
  const bilibiliMd = formatBilibiliItems(bilibiliItems, bilibiliStart + 1);
  appendToFile(BILIBILI_FILE, bilibiliMd);

  console.log('\n========== 抓取完成 ==========');
  console.log(`抖音: 新增 ${douyinItems.length} 条`);
  console.log(`B站: 新增 ${bilibiliItems.length} 条`);
  console.log(`\n文件位置:`);
  console.log(`  抖音: ${DOUYIN_FILE}`);
  console.log(`  B站: ${BILIBILI_FILE}`);
}

main().catch(console.error);
