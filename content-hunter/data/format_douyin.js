const fs = require('fs');

const data = JSON.parse(fs.readFileSync('E:/workspace/content-hunter/data/douyin_raw_1775696874698.json', 'utf8'));

const items = data.map(v => {
    return {
        title: v.text || '(无标题)',
        author: v.authorMeta?.nickName || v.authorMeta?.name || '未知',
        likes: v.diggCount || 0,
        views: v.playCount || 0,
        comments: v.commentCount || 0,
        shares: v.shareCount || 0,
        hashtags: (v.hashtags || []).map(h => '#' + h.name).join(' '),
        url: v.webVideoUrl || '',
        summary: v.text ? v.text.substring(0, 200) : 'AI相关短视频内容'
    };
}).sort((a, b) => {
    const scoreA = a.likes + a.comments * 2 + a.shares * 3;
    const scoreB = b.likes + b.comments * 2 + b.shares * 3;
    return scoreB - scoreA;
});

const top100 = items.slice(0, 100);

let header = '# 抖音热门AI内容 (TikTok #AI)\n\n';
header += '> 抓取时间: ' + new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }) + ' | 数据来源: TikTok #AI 标签 | 本次抓取: ' + data.length + '条 → 选取TOP100\n\n';

let md = '';
for (let i = 0; i < top100.length; i++) {
    var item = top100[i];
    md += '### 第' + (i+1) + '条\n';
    md += '- 标题: ' + item.title + '\n';
    md += '- 作者: @' + item.author + '\n';
    md += '- 点赞: ' + item.likes.toLocaleString() + '\n';
    md += '- 播放: ' + item.views.toLocaleString() + '\n';
    md += '- 评论: ' + item.comments.toLocaleString() + '\n';
    md += '- 话题: ' + (item.hashtags || '无') + '\n';
    md += '- 链接: ' + item.url + '\n';
    md += '- 内容总结: ' + item.summary + '\n\n';
}

const outPath = 'E:/workspace/content-hunter/data/douyin.md';
const isFirstWrite = !fs.existsSync(outPath);
const existing = isFirstWrite ? '' : fs.readFileSync(outPath, 'utf8');
fs.writeFileSync(outPath, existing + '\n' + (isFirstWrite ? header : '') + md);
console.log('[' + (isFirstWrite ? 'NEW FILE' : 'APPEND') + '] Wrote ' + top100.length + ' items to ' + outPath);
