const { writeFileSync } = require('node:fs');
const { join } = require('node:path');

const USER_AGENT = 'apify-agent-skills/apify-ultimate-scraper-1.3.0';

async function startActor(token, actorId, parsedInput) {
    const apiActorId = actorId.replace('/', '~');
    const url = `https://api.apify.com/v2/acts/${apiActorId}/runs`;

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            'User-Agent': `${USER_AGENT}/start_actor`,
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

async function pollUntilComplete(token, runId, timeout, interval) {
    const url = `https://api.apify.com/v2/actor-runs/${runId}`;
    const startTime = Date.now();
    let lastStatus = null;

    while (true) {
        const response = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!response.ok) throw new Error(`Failed to get run status`);
        const result = await response.json();
        const status = result.data.status;
        if (status !== lastStatus) { console.log(`  Status: ${status}`); lastStatus = status; }
        if (['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'].includes(status)) return status;
        if ((Date.now() - startTime) / 1000 > timeout) return 'TIMED-OUT';
        await new Promise(resolve => setTimeout(resolve, interval * 1000));
    }
}

async function downloadResults(token, datasetId) {
    const response = await fetch(
        `https://api.apify.com/v2/datasets/${datasetId}/items?format=json`,
        { headers: { 'Authorization': `Bearer ${token}`, 'User-Agent': USER_AGENT } }
    );
    if (!response.ok) throw new Error(`Failed to download results`);
    return response.json();
}

async function main() {
    const token = process.env.APIFY_TOKEN;
    if (!token) throw new Error('APIFY_TOKEN not found');

    console.log('=== Google Search: Electric Tricycles Thailand ===\n');

    // Try different input formats for google-search-scraper
    const inputs = [
        { searchQuery: "electric tricycle Thailand" },  // Try simple format first
        { queries: "electric tricycle Thailand" },     // Maybe queries is a string
    ];

    for (const input of inputs) {
        console.log(`\nTrying input format: ${JSON.stringify(input)}`);
        
        try {
            const { runId, datasetId } = await startActor(token, 'apify/google-search-scraper', input);
            console.log(`  Run ID: ${runId}`);
            
            const status = await pollUntilComplete(token, runId, 90, 3);
            
            if (status === 'SUCCEEDED') {
                const data = await downloadResults(token, datasetId);
                console.log(`  Results: ${data.length}`);
                
                if (data.length > 0) {
                    console.log(`  Sample: ${JSON.stringify(data[0]).substring(0, 200)}`);
                }
            }
        } catch (err) {
            console.log(`  Error: ${err.message}`);
        }
    }

    // Also try compass/crawler-google-places for business listings
    console.log('\n\n=== Trying Google Maps Scraper ===\n');
    
    try {
        const { runId, datasetId } = await startActor(token, 'compass/crawler-google-places', {
            searchStringsArray: ["electric tricycle Thailand", "รถสามล้อไฟฟ้า Thailand"],
            locationQuery: "Thailand",
            maxResults: 20
        });
        console.log(`Run ID: ${runId}`);
        
        const status = await pollUntilComplete(token, runId, 120, 3);
        
        if (status === 'SUCCEEDED') {
            const data = await downloadResults(token, datasetId);
            console.log(`\nGoogle Maps results: ${data.length}`);
            
            if (data.length > 0 && !data[0].error) {
                writeFileSync('E:\\workspace\\2026-04-05_google_maps_results.json', JSON.stringify(data, null, 2));
                
                // Show relevant results
                const relevant = data.filter(item => {
                    const text = ((item.title || '') + ' ' + (item.categories || '')).toLowerCase();
                    return text.includes('tricycle') || text.includes('vehicle') || 
                           text.includes('สามล้อ') || text.includes('ไฟฟ้า') ||
                           text.includes('electric');
                });
                
                console.log(`\nRelevant: ${relevant.length}`);
                
                for (let i = 0; i < Math.min(5, relevant.length); i++) {
                    const item = relevant[i];
                    console.log(`\n[${i+1}] ${item.title || 'N/A'}`);
                    console.log(`    Address: ${item.address || 'N/A'}`);
                    console.log(`    Categories: ${item.categories || 'N/A'}`);
                    console.log(`    Phone: ${item.phone || 'N/A'}`);
                    console.log(`    URL: ${item.url || 'N/A'}`);
                }
            }
        }
    } catch (err) {
        console.log(`Error: ${err.message}`);
    }
}

main().catch((err) => {
    console.error(`Error: ${err.message}`);
    process.exit(1);
});