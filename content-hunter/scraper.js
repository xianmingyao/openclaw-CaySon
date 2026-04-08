/**
 * 内容捕手 v2 - 抖音/B站 AI内容抓取
 * 使用更通用的文本提取方式
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const DATA_DIR = 'E:/workspace/content-hunter/data/';
const TARGET_COUNT = 100;

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

function appendToFile(filename, content) {
  const filepath = path.join(DATA_DIR, filename);
  fs.appendFileSync(filepath, content + '\n', 'utf8');
}

// 从页面文本中提取视频条目（通用方法）
async function extractVideosFromPage(page) {
  const text = await page.content();
  
  // 提取所有可能的视频标题（根据抖音/B站模式）
  const results = [];
  
  // 抖音搜索结果模式：提取带有 @用户名 和数字（点赞）的条目
  const douyinPattern = /@(\S+)\s*([^\n@]{5,80}?)(?=\s*#|\s*\d+\.?\d*[万]?\s*(?:点赞|播放)?|\s*\d{4,}|$)/g;
  // B站模式
  const bilibiliPattern = /([^\n]{10,80}?)\s*UP\s*[主:]?\s*(\S+)/g;
  
  // 更通用的模式：从<li>或<article>或特定div结构提取
  const htmlLines = text.split('\n');
  let currentItem = {};
  
  for (const line of htmlLines) {
    // 尝试匹配点赞数
    const likesMatch = line.match(/(\d+\.?\d*)[万]?\s*(?:点赞|播放|播放量|阅读)?/);
    // 尝试匹配标题
    const titleMatch = line.match(/title=["']([^"']{10,100})["']/i) 
      || line.match(/alt=["']([^"']{10,100})["']/i)
      || line.match(/>([^<]{15,100}?)<\/a>/);
    // 尝试匹配作者
    const authorMatch = line.match(/@(\S{2,20})/) || line.match(/作者[:：]?\s*(\S+)/);
    
    if (likesMatch && titleMatch) {
      results.push({
        title: (titleMatch[1] || titleMatch[2] || '').trim().substring(0, 100),
        author: authorMatch?.[1] || '未知',
        likes: likesMatch[1] + (line.includes('万') ? '万' : ''),
        tags: '',
        summary: `抖音热门AI相关视频内容`
      });
    }
  }
  
  return results;
}

// 使用JavaScript直接执行来提取数据
async function extractWithJS(page) {
  // 在页面上下文中执行JS提取
  const data = await page.evaluate(() => {
    const results = [];
    
    // 尝试找搜索结果容器
    const selectors = [
      '[data-e2e="search-card-video"]',
      '.search-card-video',
      '[class*="video-item"]',
      '[class*="videoItem"]',
      'li[class*="item"]',
      '.bili-video-card',
      '.video-item'
    ];
    
    let foundElements = [];
    for (const sel of selectors) {
      foundElements = document.querySelectorAll(sel);
      if (foundElements.length > 0) break;
    }
    
    if (foundElements.length === 0) {
      // 备选：直接提取页面中所有文本中有数字和@的条目
      const allText = document.body.innerText;
      const lines = allText.split('\n').filter(l => l.trim().length > 5);
      
      for (const line of lines) {
        const hasNumber = /\d+/.test(line);
        const hasAt = line.includes('@');
        if (hasNumber && hasAt && line.length < 200) {
          const titleMatch = line.match(/@(\S+)\s*(.+)/);
          const likesMatch = line.match(/(\d+\.?\d*[万]?)/);
          if (titleMatch && likesMatch) {
            results.push({
              title: titleMatch[2].trim().substring(0, 100),
              author: titleMatch[1],
              likes: likesMatch[1],
              tags: '',
              summary: 'AI相关热门内容'
            });
          }
        }
      }
    } else {
      for (const el of foundElements) {
        const text = el.innerText || el.textContent || '';
        const titleMatch = text.match(/@(\S+)\s*(.+?)(?=\s*\d+\s*[万]?\s*(?:点赞|次|播放|$))/);
        const likesMatch = text.match(/(\d+\.?\d*[万]?)\s*(?:点赞|万)/);
        
        if (titleMatch) {
          results.push({
            title: titleMatch[2].trim().substring(0, 100),
            author: titleMatch[1],
            likes: likesMatch ? likesMatch[1] : '0',
            tags: '',
            summary: 'AI相关热门内容'
          });
        }
      }
    }
    
    return results;
  });
  
  return data;
}

async function scrapeDouyin(keywords) {
  console.log('[抖音] 启动浏览器...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });
  
  const allResults = [];
  
  for (const keyword of keywords) {
    try {
      console.log(`[抖音] 搜索: ${keyword}`);
      const url = `https://www.douyin.com/search/${encodeURIComponent(keyword)}`;
      await page.goto(url, { waitUntil: 'networkidle', timeout: 20000 });
      await page.waitForTimeout(2000);
      
      // 截图看看实际内容
      await page.screenshot({ path: `E:/workspace/content-hunter/dbg_douyin_${keyword}.png`, fullPage: false });
      
      const items = await extractWithJS(page);
      console.log(`[抖音] ${keyword}: 提取到 ${items.length} 条`);
      
      for (const item of items) {
        item.tags = keyword;
        allResults.push(item);
      }
      
    } catch (e) {
      console.log(`[抖音] ${keyword} 出错: ${e.message}`);
    }
  }
  
  // 去重
  const unique = [];
  const seen = new Set();
  for (const r of allResults) {
    const key = r.title.substring(0, 30);
    if (key && !seen.has(key)) {
      seen.add(key);
      unique.push(r);
    }
  }
  
  await browser.close();
  return unique.slice(0, TARGET_COUNT);
}

async function scrapeBilibili(keywords) {
  console.log('[B站] 启动浏览器...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 900 });
  
  const allResults = [];
  
  for (const keyword of keywords) {
    try {
      console.log(`[B站] 搜索: ${keyword}`);
      const url = `https://search.bilibili.com/all?keyword=${encodeURIComponent(keyword)}&order=totalrank&duration=0&tids_1=0`;
      await page.goto(url, { waitUntil: 'networkidle', timeout: 20000 });
      await page.waitForTimeout(2000);
      
      await page.screenshot({ path: `E:/workspace/content-hunter/dbg_bilibili_${keyword}.png`, fullPage: false });
      
      const items = await page.evaluate(() => {
        const results = [];
        const cards = document.querySelectorAll('.video-item, .bili-video-card, [class*="video-item"]');
        
        if (cards.length > 0) {
          for (const card of cards) {
            const text = card.innerText || '';
            const titleMatch = text.match(/(.+?)(?=\s*@\s*\S+|\s*\d+\.\d+[万]?\s*[播放|追剧|收藏])/);
            const upMatch = text.match(/@\s*(\S+)/);
            const viewsMatch = text.match(/(\d+\.?\d*[万]?)\s*(?:播放|观看)/);
            const likesMatch = text.match(/(\d+\.?\d*[万]?)\s*(?:点赞|投币|收藏)/);
            
            if (titleMatch) {
              results.push({
                title: titleMatch[1].trim().substring(0, 100),
                up: upMatch ? upMatch[1] : '未知',
                views: viewsMatch ? viewsMatch[1] : '0',
                danmaku: '0',
                likes: likesMatch ? likesMatch[1] : '0',
                coins: '0',
                favs: '0',
                summary: 'B站AI相关热门视频'
              });
            }
          }
        }
        
        // 备选：从页面文本提取
        if (results.length === 0) {
          const allText = document.body.innerText;
          const lines = allText.split('\n');
          for (const line of lines) {
            if (line.includes('播放') && line.includes('万') && line.length < 150 && line.length > 10) {
              const clean = line.trim().replace(/\s+/g, ' ');
              if (clean.length > 20) {
                results.push({
                  title: clean.substring(0, 80),
                  up: '未知',
                  views: '未知',
                  danmaku: '未知',
                  likes: '未知',
                  coins: '未知',
                  favs: '未知',
                  summary: 'B站热门内容'
                });
              }
            }
          }
        }
        
        return results;
      });
      
      console.log(`[B站] ${keyword}: 提取到 ${items.length} 条`);
      
      for (const item of items) {
        allResults.push(item);
      }
      
    } catch (e) {
      console.log(`[B站] ${keyword} 出错: ${e.message}`);
    }
  }
  
  // 去重
  const unique = [];
  const seen = new Set();
  for (const r of allResults) {
    const key = r.title.substring(0, 30);
    if (key && !seen.has(key)) {
      seen.add(key);
      unique.push(r);
    }
  }
  
  await browser.close();
  return unique.slice(0, TARGET_COUNT);
}

function formatDouyinItem(item, index) {
  return `### 第${index}条 / Item #${index}
- 标题 / Title: ${item.title}
- 作者 / Author: @${item.author}
- 点赞 / Likes: ${item.likes}
- 话题 / Tags: ${item.tags || ''}
- 内容总结 / Summary: ${item.summary || 'AI相关热门视频内容'}
`;
}

function formatBilibiliItem(item, index) {
  return `### 第${index}条 / Item #${index}
- 标题 / Title: ${item.title}
- UP主 / UP: ${item.up}
- 播放 / Views: ${item.views}
- 弹幕 / Danmaku: ${item.danmaku || '未知'}
- 点赞 / Likes: ${item.likes}
- 投币 / Coins: ${item.coins || '0'}
- 收藏 / Favs: ${item.favs || '0'}
- 内容总结 / Summary: ${item.summary || 'B站AI相关热门视频'}
`;
}

async function main() {
  const keywords_ai = ['AI人工智能', 'ChatGPT', '大模型', 'AI工具', 'AIGC', 'AI绘画', 'AI视频', 'AI写作', '机器学习', '深度学习', 'AI教程'];
  
  // 初始化文件
  const douyinFile = 'douyin.md';
  const bilibiliFile = 'bilibili.md';
  
  appendToFile(douyinFile, `# 抖音 AI技术热门内容\n抓取时间: ${new Date().toLocaleString('zh-CN')}\n`);
  appendToFile(bilibiliFile, `# B站 AI技术热门内容\n抓取时间: ${new Date().toLocaleString('zh-CN')}\n`);
  
  try {
    const douyinData = await scrapeDouyin(keywords_ai);
    console.log(`\n[抖音] 共抓取 ${douyinData.length} 条有效数据`);
    for (let i = 0; i < douyinData.length; i++) {
      appendToFile(douyinFile, formatDouyinItem(douyinData[i], i + 1));
    }
    
    const bilibiliData = await scrapeBilibili(keywords_ai);
    console.log(`[B站] 共抓取 ${bilibiliData.length} 条有效数据`);
    for (let i = 0; i < bilibiliData.length; i++) {
      appendToFile(bilibiliFile, formatBilibiliItem(bilibiliData[i], i + 1));
    }
    
    console.log('\n✅ 抓取完成!');
    console.log(`抖音: ${douyinData.length} 条 -> ${path.join(DATA_DIR, douyinFile)}`);
    console.log(`B站: ${bilibiliData.length} 条 -> ${path.join(DATA_DIR, bilibiliFile)}`);
    
  } catch (e) {
    console.error('抓取出错:', e);
  }
}

main().catch(console.error);
