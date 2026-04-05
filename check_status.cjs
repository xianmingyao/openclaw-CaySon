const https = require('https');
const { writeFileSync } = require('fs');

const TOKEN = process.env.APIFY_TOKEN;

function fetchJson(url) {
    return new Promise((resolve, reject) => {
        https.get(url, { headers: { 'Authorization': 'Bearer ' + TOKEN } }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch (e) { reject(e); }
            });
        }).on('error', reject);
    });
}

async function waitForRun(runId, maxWait = 180) {
    const start = Date.now();
    while (Date.now() - start < maxWait * 1000) {
        const statusData = await fetchJson('https://api.apify.com/v2/actor-runs/' + runId);
        const status = statusData.data.status;
        console.log(`[${Math.round((Date.now() - start)/1000)}s] Status: ${status}`);
        
        if (status === 'SUCCEEDED') return 'SUCCEEDED';
        if (['FAILED', 'ABORTED', 'TIMED-OUT'].includes(status)) return status;
        
        await new Promise(r => setTimeout(r, 10000));
    }
    return 'TIMED-OUT';
}

async function main() {
    const runId = process.argv[2] || 'aXcShpv3SEC9Rlz3g';
    
    console.log('Waiting for run:', runId);
    const status = await waitForRun(runId);
    
    if (status === 'SUCCEEDED') {
        console.log('\nDownloading results...');
        const data = await fetchJson('https://api.apify.com/v2/datasets/' + runId + '/items?format=json');
        console.log('Total results:', data.length);
        
        if (data.length > 0 && !data[0].error) {
            // Save results
            writeFileSync('E:\\workspace\\2026-04-05_google_maps_results.json', JSON.stringify(data, null, 2));
            console.log('Saved to: 2026-04-05_google_maps_results.json');
            
            // Filter relevant
            const relevant = data.filter(item => {
                const text = ((item.title || '') + ' ' + (item.categories || '') + ' ' + (item.address || '')).toLowerCase();
                return text.includes('tricycle') || text.includes('vehicle') || 
                       text.includes('สามล้อ') || text.includes('ไฟฟ้า') ||
                       text.includes('electric') || text.includes('motor');
            });
            
            console.log('\nRelevant results:', relevant.length);
            
            for (let i = 0; i < Math.min(10, relevant.length); i++) {
                const item = relevant[i];
                console.log(`\n[${i+1}] ${item.title || 'N/A'}`);
                console.log(`    Address: ${item.address || 'N/A'}`);
                console.log(`    Categories: ${item.categories || 'N/A'}`);
                console.log(`    Phone: ${item.phone || 'N/A'}`);
                if (item.website) console.log(`    Website: ${item.website}`);
            }
            
            // Also show location statistics
            const locations = {};
            for (const item of data) {
                const city = item.city || 'Unknown';
                locations[city] = (locations[city] || 0) + 1;
            }
            
            console.log('\n=== Locations (by city) ===');
            const sorted = Object.entries(locations).sort((a, b) => b[1] - a[1]);
            for (const [city, count] of sorted.slice(0, 10)) {
                console.log(`  ${city}: ${count}`);
            }
        } else if (data[0]?.error) {
            console.log('Error:', data[0].errorDescription || data[0].error);
        }
    } else {
        console.log('Run ended with status:', status);
    }
}

main().catch(console.error);