#!/usr/bin/env python3
import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
}

# Check for Chinese AI news
print('=== Chinese AI News (from Baidu) ===')
url = 'https://cn.bing.com/search?q=AI+agent+%E8%BD%AF%E4%BB%B6%E5%BC%80%E5%8F%91'
r = requests.get(url, headers=headers, timeout=10)

# Try to extract readable content
text = r.text
# Remove HTML tags for cleaner output
text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)

# Find h2 or h3 titles
titles = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', text, flags=re.DOTALL)
for t in titles[:10]:
    clean = re.sub('<[^>]+>', '', t).strip()
    if len(clean) > 8:
        print(f'  - {clean}')

# Try to get article summaries
print('\n=== More AI Agent Content ===')
# Check VentureBeat for AI agent articles
url2 = 'https://venturebeat.com/category/ai/'
r2 = requests.get(url2, headers=headers, timeout=10)
text2 = re.sub(r'<script[^>]*>.*?</script>', '', r2.text, flags=re.DOTALL)
text2 = re.sub(r'<style[^>]*>.*?</style>', '', text2, flags=re.DOTALL)

# Find paragraphs that look like summaries
paras = re.findall(r'<p[^>]*>([\u4e00-\u9fff\w\s.,!?]{50,200})</p>', text2)
for p in paras[:5]:
    clean = re.sub('<[^>]+>', '', p).strip()
    if clean and len(clean) > 30:
        print(f'  - {clean[:150]}...')

# Check for specific article about agent at scale
print('\n=== Key Insight: AI Agents at Scale ===')
print('''
Based on current headlines:

1. INTUIT CASE STUDY: AI agents achieving 85% repeat usage rate
   - Key: Keeping humans involved in the loop

2. ENTERPRISE AI: KiloClaw for Organizations
   - Enables secure AI agents at scale
   - Addresses "shadow AI" concerns

3. SOFTWARE DEVELOPMENT TRANSFORMATION:
   - "When product managers ship code: AI just broke the software org chart"
   - "170% throughput at 80% headcount"
   - AI turning development "inside-out"

4. CODER AGENTS:
   - Claude Code leak reveals Anthropic's plans
   - OpenAI Codex with new plugins

These themes align with "万亿Agent 重新定义软件生死":
- Trillion AI agents (scale)
- Redefining software lifecycle (birth to death)
- Human-AI collaboration evolving
''')
