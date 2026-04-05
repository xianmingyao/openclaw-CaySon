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

async function downloadResults(token, datasetId) {
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

    return response.json();
}

async function main() {
    const token = process.env.APIFY_TOKEN;
    if (!token) {
        throw new Error('APIFY_TOKEN not found');
    }

    // Try different Actor types
    const actors = [
        { actor: 'apify/facebook-search-scraper', input: { searchQuery: "electric tricycle Thailand", limit: 20 } },
        { actor: 'apify/facebook-search-scraper', input: { searchQuery: "รถสามล้อไฟฟ้า", limit: 20 } },
        { actor: 'apify/facebook-search-scraper', input: { searchQuery: "电动三轮车 泰国", limit: 20 } },
    ];

    let foundResults = false;

    for (const { actor, input } of actors) {
        console.log(`\nTrying ${actor} with: ${input.searchQuery}`);
        
        try {
            const { runId, datasetId } = await startActor(token, actor, input);
            console.log(`Run ID: ${runId}`);
            
            const status = await pollUntilComplete(token, runId, 120, 3);
            
            if (status === 'SUCCEEDED') {
                const data = await downloadResults(token, datasetId);
                console.log(`Results: ${data.length}`);
                
                if (data.length > 0 && !data[0].error) {
                    console.log('\n=== FOUND RESULTS ===');
                    for (let i = 0; i < Math.min(5, data.length); i++) {
                        const item = data[i];
                        console.log(`\n--- Result ${i+1} ---`);
                        console.log(`Title: ${item.title || 'N/A'}`);
                        console.log(`Text: ${(item.text || '').substring(0, 200)}`);
                        console.log(`URL: ${item.url || 'N/A'}`);
                        console.log(`Page: ${item.pageName || 'N/A'}`);
                    }
                    writeFileSync('E:\\workspace\\2026-04-05_facebook_results.json', JSON.stringify(data, null, 2));
                    foundResults = true;
                    break;
                } else if (data[0]?.error) {
                    console.log(`Error: ${data[0].errorDescription || data[0].error}`);
                }
            }
        } catch (err) {
            console.log(`Error: ${err.message}`);
        }
    }

    if (!foundResults) {
        console.log('\n\n=== NO RESULTS FOUND ===');
        console.log('Possible reasons:');
        console.log('1. Facebook has anti-scraping measures');
        console.log('2. Search terms may not have public posts');
        console.log('3. May need different Actor parameters');
        console.log('\nSuggestions:');
        console.log('- Try searching for specific brand names');
        console.log('- Search for Thai language terms');
        console.log('- Use Facebook page scraper for specific pages');
    }
}

main().catch((err) => {
    console.error(`Error: ${err.message}`);
    process.exit(1);
});