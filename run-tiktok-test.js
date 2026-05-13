const { execSync } = require('child_process');
const path = require('path');

const scriptPath = path.join('E:', 'workspace', 'skills', 'apify-ultimate-scraper', 'reference', 'scripts', 'run_actor.js');
const actor = 'clockworks/tiktok-scraper';
const input = JSON.stringify({ search: 'github skills', limit: 5 });

try {
  const cmd = `node "${scriptPath}" --actor "${actor}" --input '${input}' --format json`;
  console.log('Running:', cmd);
  const result = execSync(cmd, { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
  console.log(result);
} catch (e) {
  console.error('Error:', e.message);
  if (e.stdout) console.log('Stdout:', e.stdout);
  if (e.stderr) console.error('Stderr:', e.stderr);
}
