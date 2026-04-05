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

    // Chinese electric tricycle brands + Thailand
    const searches = [
        "Jinpeng electric tricycle Thailand",
        "Zongshen electric tricycle Thailand", 
        "Huaihai electric tricycle Thailand",
        "electric three wheel Thailand รถสามล้อ",
        "รถสามล้อไฟฟ้า ขาย Thailand"
    ];

    console.log('Searching for Chinese electric tricycle brands in Thailand...\n');

    for (const query of searches) {
        console.log(`\nQuery: "${query}"`);
        
        try {
            const { runId, datasetId } = await startActor(token, 'apify/facebook-search-scraper', {
                searchQuery: query,
                limit: 20
            });
            
            const status = await pollUntilComplete(token, runId, 90, 3);
            
            if (status === 'SUCCEEDED') {
                const data = await downloadResults(token, datasetId);
                
                if (data.length > 0 && !data[0].error) {
                    console.log(`  Found ${data.length} results!`);
                    
                    // Filter for relevant posts
                    const relevant = data.filter(item => {
                        const text = (item.text || '').toLowerCase();
                        const title = (item.title || '').toLowerCase();
                        return text.includes('tricycle') || text.includes('three wheel') || 
                               text.includes('สามล้อ') || text.includes('ไฟฟ้า') ||
                               text.includes('electric') || title.includes('tricycle');
                    });
                    
                    if (relevant.length > 0) {
                        console.log(`  Relevant: ${relevant.length}`);
                        
                        for (const item of relevant.slice(0, 3)) {
                            console.log(`\n  --- Post ---`);
                            console.log(`  Title: ${item.title || 'N/A'}`);
                            console.log(`  Text: ${(item.text || '').substring(0, 150)}...`);
                            console.log(`  URL: ${item.url || 'N/A'}`);
                            console.log(`  Page: ${item.pageName || 'N/A'}`);
                        }
                        
                        writeFileSync('E:\\workspace\\2026-04-05_facebook_electric_tricycle.json', JSON.stringify(data, null, 2));
                        console.log('\n  Saved to: 2026-04-05_facebook_electric_tricycle.json');
                        return;
                    }
                } else {
                    console.log(`  No results or error: ${data[0]?.errorDescription || data[0]?.error || 'unknown'}`);
                }
            }
        } catch (err) {
            console.log(`  Error: ${err.message}`);
        }
    }

    console.log('\n\n=== FACEBOOK SEARCH LIMITATIONS ===');
    console.log('Facebook has strict anti-scraping measures.');
    console.log('The Apify facebook-search-scraper may return empty results for many queries.');
    console.log('\n=== ALTERNATIVE APPROACHES ===');
    console.log('1. Search on Google for "site:facebook.com electric tricycle Thailand"');
    console.log('2. Manually search Facebook for specific stores/pages');
    console.log('3. Use a browser automation approach (agent-browser skill)');
    console.log('4. Try different Apify actors like compass/crawler-google-places');
    console.log('   to find stores on Google Maps, then check their Facebook pages');
}

main().catch((err) => {
    console.error(`Error: ${err.message}`);
    process.exit(1);
});