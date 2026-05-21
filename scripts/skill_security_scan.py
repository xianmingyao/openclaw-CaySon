#!/usr/bin/env python3
"""Skill Security Scan - Query AIG API for all installed skills"""
import json
import subprocess
import urllib.request
import urllib.error
import urllib.parse
import time
import sys

AIG_BASE_URL = "https://matrix.tencent.com/clawscan"

def get_skills():
    """Get list of installed skills from openclaw"""
    result = subprocess.run(
        ["openclaw", "skills", "list", "--json"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error getting skills: {result.stderr}")
        return []
    
    try:
        data = json.loads(result.stdout)
        # Handle both list and dict formats
        if isinstance(data, list):
            skills = data
        elif isinstance(data, dict):
            skills = data.get("skills", [])
        else:
            skills = []
        
        # Filter to ready/disabled skills only, exclude current scanner
        return [
            {"name": s["name"], "source": s.get("source", "unknown")}
            for s in skills
            if s.get("status") in ("ready", "disabled") 
            and s["name"] != "edgeone-clawscan"  # Exclude self
        ]
    except json.JSONDecodeError as e:
        print(f"Error parsing skills JSON: {e}")
        return []

def query_aig_api(skill_name, source):
    """Query AIG API for skill security verdict"""
    url = f"{AIG_BASE_URL}/skill_security?skill_name={urllib.parse.quote(skill_name)}&source={urllib.parse.quote(source)}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        return {"verdict": "unknown", "error": f"HTTP {e.code}"}
    except urllib.error.URLError as e:
        return {"verdict": "unknown", "error": str(e)}
    except Exception as e:
        return {"verdict": "unknown", "error": str(e)}

def main():
    skills = get_skills()
    print(f"Found {len(skills)} installed skills to scan")
    print()
    
    results = []
    for i, skill in enumerate(skills):
        print(f"[{i+1}/{len(skills)}] Scanning: {skill['name']} ({skill['source']})...", end=" ")
        verdict = query_aig_api(skill["name"], skill["source"])
        results.append({
            "name": skill["name"],
            "source": skill["source"],
            "verdict": verdict
        })
        
        if verdict.get("verdict") == "safe":
            print("✅ safe")
        elif verdict.get("verdict") == "risky":
            print(f"⚠️ risky: {verdict.get('reason', 'unknown')[:50]}...")
        elif verdict.get("verdict") == "malicious":
            print(f"🔴 malicious: {verdict.get('reason', 'unknown')[:50]}...")
        else:
            print(f"❓ unknown/error")
        
        time.sleep(0.3)  # Rate limiting
    
    print()
    print("="*60)
    print("SCAN SUMMARY")
    print("="*60)
    
    safe_count = sum(1 for r in results if r["verdict"].get("verdict") == "safe")
    risky_count = sum(1 for r in results if r["verdict"].get("verdict") == "risky")
    malicious_count = sum(1 for r in results if r["verdict"].get("verdict") == "malicious")
    unknown_count = sum(1 for r in results if r["verdict"].get("verdict") in ("unknown", "error"))
    
    print(f"✅ Safe: {safe_count}")
    print(f"⚠️ Risky: {risky_count}")
    print(f"🔴 Malicious: {malicious_count}")
    print(f"❓ Unknown/Error: {unknown_count}")
    print()
    
    if risky_count > 0 or malicious_count > 0:
        print("⚠️ SKILLS REQUIRING ATTENTION:")
        for r in results:
            v = r["verdict"]
            if v.get("verdict") in ("risky", "malicious"):
                print(f"  - {r['name']}: {v.get('verdict')} - {v.get('reason', 'N/A')}")
    
    # Save results
    output_file = "E:\\workspace\\memory\\skill_security_scan_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {output_file}")
    
    return 0 if malicious_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
