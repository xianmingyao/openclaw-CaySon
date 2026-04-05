const { spawn } = require('child_process');
const path = require('path');

const inputJson = JSON.stringify({
  searchQuery: "electric tricycle Thailand 中国品牌",
  limit: 20
});

const args = [
  path.join('E:', 'workspace', 'skills', 'apify-ultimate-scraper', 'reference', 'scripts', 'run_actor.js'),
  '--actor', 'apify/facebook-search-scraper',
  '--input', inputJson,
  '--output', '2026-04-05_facebook_tricycle.json',
  '--format', 'json'
];

console.log('Running with args:', args);

const proc = spawn('node', args, {
  env: { ...process.env, APIFY_TOKEN: process.env.APIFY_TOKEN },
  stdio: 'inherit'
});

proc.on('close', (code) => {
  process.exit(code);
});