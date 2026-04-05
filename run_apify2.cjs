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
    return {
        runId: result.data.id,
        datasetId: result.data.defaultDatasetId,
    };
}

async function pollUntilComplete(token, runId, timeout, interval) {
    const url = `https://api.apify.com/v2/actor-runs/${runId}`;
    const startTime = Date.now();
    let lastStatus = null;

    while (true) {
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!response.ok) {
            const text = await response.text();
            throw new Error(`Failed to get run status: ${text}`);
        }

        const result = await response.json();
        const status = result.data.status;

        if (status !== lastStatus) {
            console.log(`Status: ${status}`);
            lastStatus = status;
        }

        if (['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'].includes(status)) {
            return status;
        }

        const elapsed = (Date.now() - startTime) / 1000;
        if (elapsed > timeout) {
            console.error(`Warning: Timeout after ${timeout}s`);
            return 'TIMED-OUT';
        }

        await new Promise(resolve => setTimeout(resolve, interval * 1000));
    }
}

async function downloadResults(token, datasetId, outputPath) {
    const url = `https://api.apify.com/v2/datasets/${datasetId}/items?format=json`;

    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'User-Agent': `${USER_AGENT}/download`,
        },
    });

    if (!response.ok) {
        const text = await response.text();
        throw new Error(`Failed to download results: ${text}`);
    }

    const data = await response.json();
    writeFileSync(outputPath, JSON.stringify(data, null, 2));
    console.log(`Saved to: ${outputPath}`);
    return data;
}

async function main() {
    const token = process.env.APIFY_TOKEN;
    if (!token) {
        throw new Error('APIFY_TOKEN not found');
    }

    // Try different search queries
    const queries = [
        { searchQuery: "electric tricycle China brand Thailand", limit: 30 },
        { searchQuery: "รถสามล้อไฟฟ้าจีน ไทย", limit: 30 },  // Thai
        { searchQuery: "electric tricycle sale Thailand", limit: 30 }
    ];

    const outputPath = join(process.cwd(), '2026-04-05_facebook_search_results.json');
    let allResults = [];

    for (const query of queries) {
        console.log(`\nSearching: ${query.searchQuery}`);
        
        const { runId, datasetId } = await startActor(token, 'apify/facebook-search-scraper', query);
        console.log(`Run ID: ${runId}`);
        
        const status = await pollUntilComplete(token, runId, 120, 3);
        
        if (status === 'SUCCEEDED') {
            const data = await downloadResults(token, datasetId, outputPath);
            console.log(`Results: ${data.length}`);
            
            if (data.length > 0 && !data[0].error) {
                allResults = allResults.concat(data);
            }
        } else {
            console.log(`Run ${status}`);
        }
    }

    console.log(`\n=== TOTAL RESULTS: ${allResults.length} ===`);
    
    if (allResults.length > 0) {
        writeFileSync('E:\\workspace\\2026-04-05_all_facebook_results.json', JSON.stringify(allResults, null, 2));
        
        // Analyze for relevant posts about electric tricycles
        const relevant = allResults.filter(item => {
            const text = (item.text || '').toLowerCase();
            const title = (item.title || '').toLowerCase();
            return text.includes('tricycle') || text.includes('三轮车') || 
                   text.includes('electric') || text.includes('ไฟฟ้า') ||
                   title.includes('tricycle') || title.includes('三轮车');
        });
        
        console.log(`\nRelevant posts about electric tricycles: ${relevant.length}`);
        
        for (let i = 0; i < Math.min(10, relevant.length); i++) {
            const item = relevant[i];
            console.log(`\n--- Post ${i+1} ---`);
            console.log(`Text: ${(item.text || item.title || 'N/A').substring(0, 300)}`);
            if (item.url) console.log(`URL: ${item.url}`);
            if (item.pageName) console.log(`Page: ${item.pageName}`);
        }
    }
}

main().catch((err) => {
    console.error(`Error: ${err.message}`);
    process.exit(1);
});