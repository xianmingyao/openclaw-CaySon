import requests
import re

# Search for the skills on various platforms
skills = [
    "Validator AI",
    "MaxVerdict", 
    "IdeaProof",
    "ValidIQ",
    "GovValid",
    "market-research skill",
    "product manager skill douyin"
]

# Search SkillHub for these
for skill in skills[:6]:
    url = f"https://clawhub.ai/skills/{skill.lower().replace(' ', '-')}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            print(f"FOUND on SkillHub: {skill}")
        else:
            print(f"Not on SkillHub: {skill}")
    except:
        print(f"Error checking: {skill}")

# Try to get video page with more info
print("\n--- Video Page ---")
r = requests.get(
    'https://www.douyin.com/video/7631043118246235398',
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    timeout=10
)
# Extract JSON data
match = re.search(r'window\.__INIT_PROPS__\s*=\s*({.*?});', r.text, re.DOTALL)
if match:
    print("Found init props")
else:
    # Look for title
    title_match = re.search(r'<title>(.*?)</title>', r.text)
    if title_match:
        print(f"Title: {title_match.group(1)}")
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)}")
