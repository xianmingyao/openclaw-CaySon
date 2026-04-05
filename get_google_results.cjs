const https = require('https');
const { writeFileSync } = require('fs');

const TOKEN = process.env.APIFY_TOKEN;

function fetchJson(url) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const options = {
            hostname: urlObj.hostname,
            path: urlObj.pathname + urlObj.search,
            headers: { 'Authorization': 'Bearer ' + TOKEN }
        };
        
        https.get(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch (e) { 
                    // If not JSON, return raw
                    resolve({ raw: data.substring(0, 1000) });
                }
            });
        }).on('error', reject);
    });
}

async function main() {
    // Get results from the Google search that succeeded
    const datasetId = 'dtmxe1T21KObjUQ33';
    
    console.log('Fetching Google search results...');
    const data = await fetchJson('https://api.apify.com/v2/datasets/' + datasetId + '/items?format=json');
    
    console.log('Raw response type:', typeof data);
    console.log('Is array:', Array.isArray(data));
    console.log('Length:', data.length);
    
    if (Array.isArray(data) && data.length > 0) {
        console.log('\nFirst item keys:', Object.keys(data[0]));
        console.log('\nFirst item:', JSON.stringify(data[0], null, 2).substring(0, 2000));
        
        // Filter relevant
        const relevant = data.filter(item => {
            const text = ((item.title || '') + ' ' + (item.description || '')).toLowerCase();
            return text.includes('tricycle') || text.includes('vehicle') || 
                   text.includes('สามล้อ') || text.includes('ไฟฟ้า') ||
                   text.includes('electric') || text.includes('ขาย');
        });
        
        console.log('\nRelevant results:', relevant.length);
        
        if (relevant.length > 0) {
            writeFileSync('E:\\workspace\\2026-04-05_google_search_results.json', JSON.stringify(relevant, null, 2));
            console.log('Saved to: 2026-04-05_google_search_results.json');
            
            for (let i = 0; i < Math.min(5, relevant.length); i++) {
                const item = relevant[i];
                console.log(`\n[${i+1}] ${item.title || 'N/A'}`);
                console.log(`    URL: ${item.url || 'N/A'}`);
                console.log(`    Desc: ${(item.description || '').substring(0, 200)}`);
            }
        }
    } else if (data.error) {
        console.log('Error:', data.error);
    } else {
        console.log('Data:', JSON.stringify(data).substring(0, 500));
    }
}

main().catch(console.error);