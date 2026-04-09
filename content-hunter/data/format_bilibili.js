const fs = require('fs');

const data = JSON.parse(fs.readFileSync('E:/workspace/content-hunter/data/bilibili_raw.json', 'utf8'));

function stripHtml(text) {
    return String(text || '').replace(/<[^>]+>/g, '').trim();
}

const items = data.map(v => {
    const score = (v.play || 0) * 0.1 + (v.like || 0) * 2 + (v.favorites || 0) * 3 + (v.review || 0);
    return {
        title: stripHtml(v.title),
        author: v.author || '未知',
        play: v.play || 0,
        danmaku: v.video_review || 0,
        like: v.like || 0,
        coins: 0,
        favorites: v.favorites || 0,
        review: v.review || 0,
        duration: v.duration || '未知',
        tags: (v.tag || '').split(',').filter(t => t).slice(0, 5).join(' #'),
        url: v.arcurl || '',
        bvid: v.bvid || '',
        desc: stripHtml(v.description).substring(0, 200),
        score: score
    };
}).sort((a, b) => b.score - a.score);

const top100 = items.slice(0, 100);

let header = '# B站热门AI技术内容\n\n';
header += '> 抓取时间: ' + new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }) + ' | 数据来源: Bilibili搜索 | 关键词: AI技术/人工智能/大模型/ChatGPT/深度学习 | 本次: ' + data.length + '条 → TOP100\n\n';

let md = '';
for (let i = 0; i < top100.length; i++) {
    var item = top100[i];
    md += '### 第' + (i+1) + '条\n';
    md += '- 标题: ' + item.title + '\n';
    md += '- UP主: ' + item.author + '\n';
    md += '- 播放: ' + item.play.toLocaleString() + '\n';
    md += '- 弹幕: ' + item.danmaku.toLocaleString() + '\n';
    md += '- 点赞: ' + item.like.toLocaleString() + '\n';
    md += '- 收藏: ' + item.favorites.toLocaleString() + '\n';
    md += '- 时长: ' + item.duration + '\n';
    md += '- 话题: #' + item.tags + '\n';
    md += '- 链接: ' + item.url + '\n';
    md += '- 内容总结: ' + item.desc + '\n\n';
}

const outPath = 'E:/workspace/content-hunter/data/bilibili.md';
const isFirstWrite = !fs.existsSync(outPath);
const existing = isFirstWrite ? '' : fs.readFileSync(outPath, 'utf8');
fs.writeFileSync(outPath, existing + '\n' + (isFirstWrite ? header : '') + md);
console.log('[' + (isFirstWrite ? 'NEW FILE' : 'APPEND') + '] Wrote ' + top100.length + ' items to ' + outPath);
console.log('Top 3 by score:');
top100.slice(0, 3).forEach((v, i) => console.log((i+1) + '. ' + v.title.substring(0, 50) + ' | 播放:' + v.play.toLocaleString() + ' 点赞:' + v.like.toLocaleString()));
