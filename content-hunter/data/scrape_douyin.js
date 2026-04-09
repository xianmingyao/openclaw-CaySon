#!/usr/bin/env node
const { writeFileSync } = require('node:fs');

const APIFY_TOKEN = process.env.APIFY_TOKEN;
const actorId = 'clockworks~tiktok-hashtag-scraper';
const input = { hashtags: ['AI', '人工智能', 'AI技术', 'ChatGPT', '大模型'], maxItems: 100 };
const outputPath = `E:/workspace/content-hunter/data/douyin_raw_${Date.now()}.json`;

async function main() {
    console.log('Starting Douyin/TikTok AI scraper...');

    // Start actor run
    const startUrl = `https://api.apify.com/v2/acts/${actorId}/runs`;
    const startRes = await fetch(startUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${APIFY_TOKEN}` },
        body: JSON.stringify(input),
    });

    if (!startRes.ok) {
        const err = await startRes.text();
        console.error(`Start failed (${startRes.status}): ${err}`);
        process.exit(1);
    }

    const { data } = await startRes.json();
    const runId = data.id;
    const datasetId = data.defaultDatasetId;
    console.log(`Run started: ${runId}, dataset: ${datasetId}`);

    // Poll until done
    const statusUrl = `https://api.apify.com/v2/actor-runs/${runId}`;
    let status;
    while (true) {
        await new Promise(r => setTimeout(r, 5000));
        const sRes = await fetch(statusUrl, { headers: { 'Authorization': `Bearer ${APIFY_TOKEN}` } });
        const sData = await sRes.json();
        status = sData.data.status;
        console.log(`Status: ${status}`);
        if (['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'].includes(status)) break;
    }

    if (status !== 'SUCCEEDED') {
        console.error(`Run ended with status: ${status}`);
        process.exit(1);
    }

    // Download results
    const dlUrl = `https://api.apify.com/v2/datasets/${datasetId}/items?format=json`;
    const dlRes = await fetch(dlUrl, { headers: { 'Authorization': `Bearer ${APIFY_TOKEN}` } });
    const items = await dlRes.json();
    console.log(`Got ${items.length} items`);
    writeFileSync(outputPath, JSON.stringify(items, null, 2));
    console.log(`Saved to ${outputPath}`);
}

main().catch(e => { console.error(e); process.exit(1); });
