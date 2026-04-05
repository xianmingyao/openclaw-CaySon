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
                catch (e) { reject(e); }
            });
        }).on('error', reject);
    });
}

async function startActor(token, actorId, parsedInput) {
    const apiActorId = actorId.replace('/', '~');
    const url = `https://api.apify.com/v2/acts/${apiActorId}/runs`;

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'User-Agent': 'apify-agent-skills/1.0',
        },
        body: JSON.stringify(parsedInput),
    });

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`API request failed (${response.status}): ${text}`);
    }

    const result = await response.json();
    return { runId: result.data.id, datasetId: result.data.defaultDatasetId };
}

async function pollUntilComplete(token, runId, timeout) {
    const startTime = Date.now();
    let lastStatus = null;

    while (true) {
        const statusData = await fetchJson('https://api.apify.com/v2/actor-runs/' + runId);
        const status = statusData.data.status;
        
        if (status !== lastStatus) {
            console.log(`  Status: ${status}`);
            lastStatus = status;
        }
        
        if (['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'].includes(status)) return status;
        if ((Date.now() - startTime) / 1000 > timeout) return 'TIMED-OUT';
        
        await new Promise(r => setTimeout(r, 10000));
    }
}

async function main() {
    console.log('=== Thai Electric Tricycle Search ===\n');

    // Try Thai search queries
    const queries = [
        'รถสามล้อไฟฟ้า ขาย กรุงเทพ',  // Electric tricycle for sale, Bangkok
        'รถสามล้อไฟฟ้า จีน ราคา',        // Chinese electric tricycle price
        'รถไฟฟ้าสามล้อ ร้านค้า ไทย',     // Electric tricycle store Thailand
    ];

    let allResults = [];

    for (const query of queries) {
        console.log(`\nSearching: "${query}"`);
        
        try {
            const { runId, datasetId } = await startActor(TOKEN, 'apify/facebook-search-scraper', {
                searchQuery: query,
                limit: 20
            });
            console.log(`  Run ID: ${runId}`);
            
            const status = await pollUntilComplete(TOKEN, runId, 120);
            
            if (status === 'SUCCEEDED') {
                const data = await fetchJson(`https://api.apify.com/v2/datasets/${datasetId}/items?format=json`);
                console.log(`  Results: ${data.length}`);
                
                if (data.length > 0 && !data[0].error) {
                    allResults = allResults.concat(data);
                    
                    for (const item of data.slice(0, 3)) {
                        console.log(`\n  - ${item.title || 'N/A'}`);
                        console.log(`    ${(item.text || '').substring(0, 100)}...`);
                    }
                }
            }
        } catch (err) {
            console.log(`  Error: ${err.message}`);
        }
    }

    if (allResults.length > 0) {
        writeFileSync('E:\\workspace\\2026-04-05_thai_tricycle.json', JSON.stringify(allResults, null, 2));
        console.log(`\n\nTotal results saved: ${allResults.length}`);
    } else {
        console.log('\n\nNo results found.');
    }
}

main().catch(console.error);