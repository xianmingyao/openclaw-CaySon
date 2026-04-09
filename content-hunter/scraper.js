/**
 * 内容捕手 - 抖音 & B站 AI内容抓取脚本
 * 抓取AI技术热门内容，追加写入 md 文件
 * 
 * 注意：由于抖音有强反爬，这里主要通过B站API + 搜索抓取
 * 抖音使用TikTok scraper思路（抖音和TikTok同源）
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// ========== 配置 ==========
const DATA_DIR = 'E:/workspace/content-hunter/data';
const BILIBILI_AI_SEARCH_KEYWORDS = ['AI', '人工智能', 'ChatGPT', '大模型', 'LLM', 'AGI', 'AIGC', 'GAI', '机器学习', '深度学习', '神经网络', 'AI Agent', 'AI编程', 'OpenAI', 'GPT', 'Claude', 'Gemini', 'AI视频', 'AI绘图', 'AI音乐'];
const DOUYIN_KEYWORDS = ['AI人工智能', 'ChatGPT', '大模型', 'LLM', 'AGI', 'AIGC', 'AI教程', 'AI工具', 'AI资讯'];
const MAX_ITEMS_PER_PLATFORM = 100;
const MAX_BATCH_SIZE = 20; // 每批最多处理数

// 确保目录存在
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// ========== 工具函数 ==========

/**
 * 追加写入 MD 文件
 */
function appendToMdFile(filename, content) {
  const filepath = path.join(DATA_DIR, filename);
  fs.appendFileSync(filepath, content + '\n', 'utf8');
  console.log(`[追加写入] ${filename}: ${content.slice(0, 80)}...`);
}

/**
 * 格式化日期时间
 */
function formatDateTime() {
  const now = new Date();
  return now.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
}

/**
 * HTTP GET 请求（Promise版本）
 */
function httpGet(url, headers = {}) {
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https') ? https : http;
    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://www.bilibili.com/',
        ...headers
      },
      timeout: 15000
    };

    lib.get(url, options, (res) => {
      // 处理重定向
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        resolve(httpGet(res.headers.location, headers));
        return;
      }

      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject).on('timeout', () => reject(new Error('Request timeout')));
  });
}

/**
 * 从文本中提取AI相关关键词匹配
 */
function isAIRelated(title, tags = []) {
  const text = (title + ' ' + tags.join(' ')).toLowerCase();
  const aiKeywords = [
    'ai', '人工智能', 'chatgpt', '大模型', 'llm', 'agi', 'aigc', 'gai',
    '机器学习', '深度学习', '神经网络', 'agent', 'openai', 'gpt-', 'gpt4',
    'claude', 'gemini', 'ai视频', 'ai绘图', 'ai音乐', 'ai生成', 'ai创作',
    'ai绘画', 'ai配音', 'ai换脸', 'ai克隆', 'copilot', 'copilot', 'langchain',
    'langgraph', 'rag', '向量数据库', 'embedding', 'transformer', 'diffusion',
    'stable diffusion', 'midjourney', 'sora', 'grok', 'kimi', '通义千问',
    '文心一言', '讯飞星火', '智谱ai', '百川ai', 'ai编程', 'cursor', 'github copilot',
    '自动化', '算法', '数据科学', 'ai助手', 'ai应用', 'ai技术', 'ai工具',
    'ai行业', 'ai资讯', 'ai科普', 'ai教程', 'ai开发', 'ai模型', 'ai训练',
    'ai推理', 'ai部署', 'ai应用', '数字人', '虚拟人', 'ai主播', 'ai客服'
  ];
  return aiKeywords.some(kw => text.includes(kw.toLowerCase()));
}

// ========== B站抓取函数 ==========

/**
 * 获取B站全站热门排行榜（综合）
 */
async function getBilibiliHotRanking() {
  console.log('[B站] 获取全站热门排行榜...');
  const videos = [];
  
  try {
    // B站排行榜API - 全站榜
    const apiUrl = 'https://api.bilibili.com/x/web-interface/ranking/v2?pn=1&ps=50&type=all';
    const data = await httpGet(apiUrl);
    const json = JSON.parse(data);
    
    if (json.code === 0 && json.data && json.data.list) {
      for (const item of json.data.list) {
        const title = item.title || '';
        const author = item.owner?.name || '未知';
        const views = item.stat?.view || 0;
        const likes = item.stat?.like || 0;
        const bvid = item.bvid || '';
        const link = `https://www.bilibili.com/video/${bvid}`;
        const desc = item.desc || '';
        const dynamic = item.dynamic || '';
        const pubdate = new Date(item.pubdate * 1000).toLocaleDateString('zh-CN');
        const duration = item.duration || 0;
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        
        videos.push({
          platform: 'B站',
          title,
          author,
          views,
          likes,
          link,
          bvid,
          pubdate,
          duration: `${minutes}:${seconds.toString().padStart(2, '0')}`,
          desc: desc.slice(0, 100),
          tags: (item.tags || []).map(t => t.tag_name),
          score: views * 0.3 + likes * 0.7,
          isAI: isAIRelated(title, item.tags?.map(t => t.tag_name) || [])
        });
      }
    }
    console.log(`[B站] 全站榜获取 ${videos.length} 条`);
  } catch (e) {
    console.error('[B站] 全站榜获取失败:', e.message);
  }
  
  return videos;
}

/**
 * 获取B站知识区分区内容
 */
async function getBilibiliKnowledgeZone() {
  console.log('[B站] 获取知识区分区内容...');
  const videos = [];
  
  try {
    // B站知识区排行榜
    const apiUrl = 'https://api.bilibili.com/x/web-interface/ranking/v2?pn=1&ps=50&type=knowledge';
    const data = await httpGet(apiUrl);
    const json = JSON.parse(data);
    
    if (json.code === 0 && json.data && json.data.list) {
      for (const item of json.data.list) {
        const title = item.title || '';
        const author = item.owner?.name || '未知';
        const views = item.stat?.view || 0;
        const likes = item.stat?.like || 0;
        const bvid = item.bvid || '';
        const link = `https://www.bilibili.com/video/${bvid}`;
        const pubdate = new Date(item.pubdate * 1000).toLocaleDateString('zh-CN');
        const duration = item.duration || 0;
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        
        videos.push({
          platform: 'B站',
          title,
          author,
          views,
          likes,
          link,
          bvid,
          pubdate,
          duration: `${minutes}:${seconds.toString().padStart(2, '0')}`,
          tags: (item.tags || []).map(t => t.tag_name),
          score: views * 0.3 + likes * 0.7,
          isAI: isAIRelated(title, item.tags?.map(t => t.tag_name) || [])
        });
      }
    }
    console.log(`[B站] 知识区获取 ${videos.length} 条`);
  } catch (e) {
    console.error('[B站] 知识区获取失败:', e.message);
  }
  
  return videos;
}

/**
 * 获取B站科技数码分区
 */
async function getBilibiliTechZone() {
  console.log('[B站] 获取科技数码分区...');
  const videos = [];
  
  try {
    // B站科技数码排行榜
    const apiUrl = 'https://api.bilibili.com/x/web-interface/ranking/v2?pn=1&ps=50&type=tech';
    const data = await httpGet(apiUrl);
    const json = JSON.parse(data);
    
    if (json.code === 0 && json.data && json.data.list) {
      for (const item of json.data.list) {
        const title = item.title || '';
        const author = item.owner?.name || '未知';
        const views = item.stat?.view || 0;
        const likes = item.stat?.like || 0;
        const bvid = item.bvid || '';
        const link = `https://www.bilibili.com/video/${bvid}`;
        const pubdate = new Date(item.pubdate * 1000).toLocaleDateString('zh-CN');
        const duration = item.duration || 0;
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        
        videos.push({
          platform: 'B站',
          title,
          author,
          views,
          likes,
          link,
          bvid,
          pubdate,
          duration: `${minutes}:${seconds.toString().padStart(2, '0')}`,
          tags: (item.tags || []).map(t => t.tag_name),
          score: views * 0.3 + likes * 0.7,
          isAI: isAIRelated(title, item.tags?.map(t => t.tag_name) || [])
        });
      }
    }
    console.log(`[B站] 科技区获取 ${videos.length} 条`);
  } catch (e) {
    console.error('[B站] 科技区获取失败:', e.message);
  }
  
  return videos;
}

/**
 * B站搜索AI相关内容
 */
async function searchBilibiliAI(keyword) {
  console.log(`[B站搜索] 关键词: ${keyword}`);
  const videos = [];
  
  try {
    // B站搜索API
    const apiUrl = `https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=${encodeURIComponent(keyword)}&page=1&ps=20&order=totalrank`;
    const data = await httpGet(apiUrl);
    const json = JSON.parse(data);
    
    if (json.code === 0 && json.data && json.data.result) {
      for (const item of json.data.result) {
        if (item.result_type !== 'video') continue;
        
        const title = item.title.replace(/<[^>]+>/g, ''); // 去除HTML标签
        const author = item.author || '未知';
        const bvid = item.bvid || '';
        const link = item.arcurl || `https://www.bilibili.com/video/${bvid}`;
        const pubdate = item.pubdate ? new Date(item.pubdate * 1000).toLocaleDateString('zh-CN') : '未知';
        const duration = item.duration || '未知';
        const views = item.play || 0;
        const likes = item.review || 0; // review在这里是评论数
        
        videos.push({
          platform: 'B站',
          title,
          author,
          views,
          likes,
          link,
          bvid,
          pubdate,
          duration,
          tags: (item.tags || '').split(',').filter(Boolean),
          score: views * 0.3 + likes * 0.7,
          isAI: true
        });
      }
    }
    console.log(`[B站搜索] "${keyword}" 获取 ${videos.length} 条`);
  } catch (e) {
    console.error(`[B站搜索] "${keyword}" 失败:`, e.message);
  }
  
  return videos;
}

// ========== 抖音抓取函数 ==========

/**
 * 获取抖音热榜（通过公开API）
 * 注意：抖音API需要登录态，这里用搜索接口代替
 */
async function getDouyinHotSearch() {
  console.log('[抖音] 获取抖音热榜...');
  const videos = [];
  
  try {
    // 抖音热榜API（无需登录）
    const apiUrl = 'https://www.douyin.com/aweme/v1/web/search/item/?keyword=AI&count=20&offset=0&search_channel=aweme_video_web';
    const data = await httpGet(apiUrl, {
      'Cookie': '',
      'X-SS-TC': '0'
    });
    
    const json = JSON.parse(data);
    if (json.status_code === 0 && json.data) {
      for (const item of json.data) {
        const desc = item.desc || '';
        const author = item.author?.nickname || '未知';
        const views = item.statistics?.play_count || 0;
        const likes = item.statistics?.digg_count || 0;
        const awemeId = item.aweme_id || '';
        const link = `https://www.douyin.com/video/${awemeId}`;
        
        videos.push({
          platform: '抖音',
          title: desc,
          author,
          views,
          likes,
          link,
          awemeId,
          isAI: isAIRelated(desc)
        });
      }
    }
    console.log(`[抖音] 热榜获取 ${videos.length} 条`);
  } catch (e) {
    console.error('[抖音] 热榜获取失败:', e.message);
  }
  
  return videos;
}

/**
 * 抖音搜索AI内容
 */
async function searchDouyinAI(keyword) {
  console.log(`[抖音搜索] 关键词: ${keyword}`);
  const videos = [];
  
  try {
    // 尝试使用抖音搜索API
    const apiUrl = `https://www.douyin.com/aweme/v1/web/search/item/?keyword=${encodeURIComponent(keyword)}&count=20&offset=0&search_channel=aweme_video_web&version_code=170400&version_name=17.4.0`;
    const data = await httpGet(apiUrl, {
      'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
      'Referer': 'https://www.douyin.com/'
    });
    
    const json = JSON.parse(data);
    if (json.status_code === 0 && json.data) {
      for (const item of json.data) {
        const desc = item.desc || '';
        const author = item.author?.nickname || '未知';
        const views = item.statistics?.play_count || 0;
        const likes = item.statistics?.digg_count || 0;
        const awemeId = item.aweme_id || '';
        const link = `https://www.douyin.com/video/${awemeId}`;
        
        videos.push({
          platform: '抖音',
          title: desc,
          author,
          views,
          likes,
          link,
          awemeId,
          isAI: isAIRelated(desc)
        });
      }
    }
    console.log(`[抖音搜索] "${keyword}" 获取 ${videos.length} 条`);
  } catch (e) {
    console.error(`[抖音搜索] "${keyword}" 失败:`, e.message);
  }
  
  return videos;
}

// ========== 主函数 ==========

async function main() {
  console.log('='.repeat(60));
  console.log('内容捕手开始执行！');
  console.log(`时间: ${formatDateTime()}`);
  console.log(`目标: 抖音 + B站 每平台100条AI热门内容`);
  console.log('='.repeat(60));
  
  const allVideos = [];
  const seenTitles = new Set(); // 去重用
  
  // ===== B站抓取 =====
  console.log('\n----- B站抓取开始 -----\n');
  
  // 1. B站全站热榜
  const hotVideos = await getBilibiliHotRanking();
  allVideos.push(...hotVideos);
  
  // 2. B站知识区
  const knowledgeVideos = await getBilibiliKnowledgeZone();
  allVideos.push(...knowledgeVideos);
  
  // 3. B站科技区
  const techVideos = await getBilibiliTechZone();
  allVideos.push(...techVideos);
  
  // 4. B站搜索AI关键词
  for (const kw of BILIBILI_AI_SEARCH_KEYWORDS.slice(0, 8)) {
    const searchResults = await searchBilibiliAI(kw);
    allVideos.push(...searchResults);
    await new Promise(r => setTimeout(r, 500)); // 避免请求过快
  }
  
  // ===== 抖音抓取 =====
  console.log('\n----- 抖音抓取开始 -----\n');
  
  // 抖音搜索AI关键词
  for (const kw of DOUYIN_KEYWORDS) {
    const searchResults = await searchDouyinAI(kw);
    allVideos.push(...searchResults);
    await new Promise(r => setTimeout(r, 500));
  }
  
  // ===== 去重 + 过滤AI相关内容 =====
  console.log('\n----- 数据处理 -----\n');
  console.log(`总抓取量: ${allVideos.length} 条`);
  
  const uniqueVideos = [];
  for (const v of allVideos) {
    const key = v.title + '|' + v.author;
    if (!seenTitles.has(key)) {
      seenTitles.add(key);
      uniqueVideos.push(v);
    }
  }
  console.log(`去重后: ${uniqueVideos.length} 条`);
  
  // 分离B站和抖音
  const bilibiliVideos = uniqueVideos.filter(v => v.platform === 'B站');
  const douyinVideos = uniqueVideos.filter(v => v.platform === '抖音');
  
  console.log(`B站: ${bilibiliVideos.length} 条`);
  console.log(`抖音: ${douyinVideos.length} 条`);
  
  // ===== 写入文件 =====
  console.log('\n----- 写入文件 -----\n');
  
  // B站文件
  const bilibiliFile = `bilibili-ai-${new Date().toISOString().split('T')[0]}.md`;
  const bilibiliHeader = `# B站 AI技术热门内容
抓取时间: ${formatDateTime()}
来源: B站全站热榜 + 知识区 + 科技区 + AI关键词搜索
说明: 本次追加写入

## 内容列表

| # | 标题 | 作者 | 播放 | 点赞 | 时长 | 日期 | 链接 |
|---|------|------|------|------|------|------|------|
`;
  
  // 如果文件不存在，先写头部
  const bilibiliPath = path.join(DATA_DIR, bilibiliFile);
  if (!fs.existsSync(bilibiliPath)) {
    fs.writeFileSync(bilibiliPath, bilibiliHeader + '\n', 'utf8');
  }
  
  // 写入B站内容（按播放量排序）
  const sortedBilibili = bilibiliVideos
    .filter(v => v.isAI || isAIRelated(v.title, v.tags || []))
    .sort((a, b) => b.views - a.views)
    .slice(0, MAX_ITEMS_PER_PLATFORM);
  
  let bilibiliCount = 0;
  for (let i = 0; i < sortedBilibili.length; i++) {
    const v = sortedBilibili[i];
    const num = i + 1;
    const views = typeof v.views === 'number' ? formatNumber(v.views) : v.views;
    const likes = typeof v.likes === 'number' ? formatNumber(v.likes) : v.likes;
    const title = escapeMd(v.title);
    const author = escapeMd(v.author);
    const link = v.link || `https://www.bilibili.com/video/${v.bvid}`;
    const duration = v.duration || '未知';
    const date = v.pubdate || '未知';
    
    const row = `| ${num} | ${title} | ${author} | ${views} | ${likes} | ${duration} | ${date} | [链接](${link}) |`;
    appendToMdFile(bilibiliFile, row);
    bilibiliCount++;
  }
  
  // 抖音文件
  const douyinFile = `douyin-ai-${new Date().toISOString().split('T')[0]}.md`;
  const douyinHeader = `# 抖音 AI技术热门内容
抓取时间: ${formatDateTime()}
来源: 抖音搜索AI关键词
说明: 本次追加写入

## 内容列表

| # | 标题 | 作者 | 播放 | 点赞 | 链接 |
|---|------|------|------|------|------|
`;
  
  const douyinPath = path.join(DATA_DIR, douyinFile);
  if (!fs.existsSync(douyinPath)) {
    fs.writeFileSync(douyinPath, douyinHeader + '\n', 'utf8');
  }
  
  // 写入抖音内容
  const sortedDouyin = douyinVideos
    .filter(v => v.isAI || isAIRelated(v.title))
    .sort((a, b) => b.views - a.views)
    .slice(0, MAX_ITEMS_PER_PLATFORM);
  
  let douyinCount = 0;
  for (let i = 0; i < sortedDouyin.length; i++) {
    const v = sortedDouyin[i];
    const num = i + 1;
    const views = typeof v.views === 'number' ? formatNumber(v.views) : v.views;
    const likes = typeof v.likes === 'number' ? formatNumber(v.likes) : v.likes;
    const title = escapeMd(v.title);
    const author = escapeMd(v.author);
    const link = v.link || `https://www.douyin.com/video/${v.awemeId}`;
    
    const row = `| ${num} | ${title} | ${author} | ${views} | ${likes} | [链接](${link}) |`;
    appendToMdFile(douyinFile, row);
    douyinCount++;
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('内容捕手执行完成！');
  console.log(`B站: 写入 ${bilibiliCount} 条 → ${bilibiliFile}`);
  console.log(`抖音: 写入 ${douyinCount} 条 → ${douyinFile}`);
  console.log(`数据目录: ${DATA_DIR}`);
  console.log('='.repeat(60));
  
  return { bilibiliCount, douyinCount, bilibiliFile, douyinFile };
}

// 辅助函数
function formatNumber(num) {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万';
  }
  return num.toString();
}

function escapeMd(text) {
  if (!text) return '';
  return text.replace(/\|/g, '\\|').replace(/\n/g, ' ').replace(/\[/g, '【').replace(/\]/g, '】');
}

// 执行
main().catch(console.error);
