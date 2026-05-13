#!/usr/bin/env node
import { execSync } from 'child_process';

const scriptPath = 'E:/workspace/skills/apify-ultimate-scraper/reference/scripts/run_actor.js';
const actor = 'clockworks/tiktok-scraper';
const input = JSON.stringify({ search: 'github skills', limit: 5 });

const cmd = `node "${scriptPath}" --actor="${actor}" --input=${input} --format=json`;
console.log('CMD:', cmd);

try {
  const result = execSync(cmd, { 
    encoding: 'utf8', 
    maxBuffer: 10 * 1024 * 1024,
    shell: true
  });
  console.log('Result:', result);
} catch (e) {
  console.error('Error:', e.message);
  if (e.stdout) console.log('Stdout:', e.stdout);
  if (e.stderr) console.error('Stderr:', e.stderr);
}
