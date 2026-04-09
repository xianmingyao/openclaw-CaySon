const https = require('https');
const { writeFileSync } = require('fs');

const KEYWORDS = ['AI技术', '人工智能', '大模型', 'ChatGPT', '深度学习'];
const outPath = 'E:/workspace/content-hunter/data/bilibili_raw.json';
let allItems = [];

function fetchPage(keyword, page) {
    return new Promise((resolve, reject) => {
        const params = new URLSearchParams({
            search_type: 'video',
            keyword: keyword,
            page: page,
            page_size: 20
        });
        const url = `https://api.bilibili.com/x/web-interface/search/type?${params}`;
        console.log(`Fetching: ${keyword} page ${page}`);
        
        https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com' } }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (json.code === 0 && json.data && json.data.result) {
                        resolve(json.data.result);
                    } else {
                        console.log('No data for', keyword, 'page', page, ':', json.message);
                        resolve([]);
                    }
                } catch (e) {
                    console.error('Parse error:', e.message);
                    resolve([]);
                }
            });
        }).on('error', reject);
    });
}

async function main() {
    for (const keyword of KEYWORDS) {
        for (let page = 1; page <= 5; page++) {
            const items = await fetchPage(keyword, page);
            allItems = allItems.concat(items);
            await new Promise(r => setTimeout(r, 500));
        }
    }
    
    // Deduplicate by bvid
    const seen = new Set();
    const unique = allItems.filter(v => {
        if (seen.has(v.bvid)) return false;
        seen.add(v.bvid);
        return true;
    });
    
    console.log(`Total: ${allItems.length}, Unique: ${unique.length}`);
    writeFileSync(outPath, JSON.stringify(unique, null, 2));
    console.log('Saved to', outPath);
}

main().catch(console.error);
