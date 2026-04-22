import requests
import json

# Search SkillHub API for product manager related skills
search_terms = ["validator", "maxverdict", "ideaproof", "validiq", "govvalid", "market-research"]

base_url = "https://clawhub.ai/api/v1/skills"

for term in search_terms:
    url = f"{base_url}/{term}"
    try:
        r = requests.get(url, timeout=10)
        print(f"\n=== {term} ===")
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
        elif r.status_code == 404:
            # Try search endpoint
            search_url = f"{base_url}?search={term}"
            r2 = requests.get(search_url, timeout=10)
            print(f"Search status: {r2.status_code}")
            if r2.status_code == 200:
                results = r2.json()
                if isinstance(results, dict) and 'skills' in results:
                    for s in results['skills'][:3]:
                        print(f"  - {s.get('name', 'unknown')}: {s.get('description', '')[:100]}")
                elif isinstance(results, list):
                    for s in results[:3]:
                        print(f"  - {s.get('name', 'unknown') if isinstance(s, dict) else s}")
    except Exception as e:
        print(f"Error: {e}")
