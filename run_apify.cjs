const { writeFileSync } = require('node:fs');
const { join } = require('node:path');

const USER_AGENT = 'apify-agent-skills/apify-ultimate-scraper-1.3.0';

function validateActorId(actorId) {
    const TECHNICAL_NAME = /^[a-zA-Z0-9][a-zA-Z0-9._-]*\/[a-zA-Z0-9][a-zA-Z0-9._-]*$/;
    const RAW_ID = /^[a-zA-Z0-9]{17}$/;
    if (!TECHNICAL_NAME.test(actorId) && !RAW_ID.test(actorId)) {
        throw new Error(`Invalid Actor ID format: ${actorId}`);
    }
}

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

    if (response.status === 404) {
        throw new Error(`Actor '${actorId}' not found`);
    }

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
            console.error(`Warning: Timeout after ${timeout}s, actor still running`);
            return 'TIMED-OUT';
        }

        await new Promise(resolve => setTimeout(resolve, interval * 1000));
    }
}

async function downloadResults(token, datasetId, outputPath, format) {
    const url = `https://api.apify.com/v2/datasets/${datasetId}/items?format=json`;

    const response = await fetch(url, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'User-Agent': `${USER_AGENT}/download_${format}`,
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
        throw new Error('APIFY_TOKEN environment variable not found');
    }

    const actorId = 'apify/facebook-search-scraper';
    validateActorId(actorId);

    const parsedInput = {
        searchQuery: "electric tricycle 电动三轮车 Thailand 中国品牌",
        limit: 50,
        language: "zh"
    };

    const outputPath = join(process.cwd(), '2026-04-05_facebook_tricycle.json');

    console.log(`Starting actor: ${actorId}`);
    const { runId, datasetId } = await startActor(token, actorId, parsedInput);
    console.log(`Run ID: ${runId}`);
    console.log(`Dataset ID: ${datasetId}`);

    const status = await pollUntilComplete(token, runId, 300, 5);

    if (status !== 'SUCCEEDED') {
        throw new Error(`Actor run ${status} - See: https://console.apify.com/actors/runs/${runId}`);
    }

    const data = await downloadResults(token, datasetId, outputPath, 'json');
    console.log(`\nTotal results: ${data.length}`);
    
    if (data.length > 0) {
        console.log('\n--- Sample Results ---');
        for (let i = 0; i < Math.min(5, data.length); i++) {
            const item = data[i];
            console.log(`\n[${i+1}] ${item.text || item.title || JSON.stringify(item).substring(0, 200)}`);
        }
    }
}

main().catch((err) => {
    console.error(`Error: ${err.message}`);
    process.exit(1);
});