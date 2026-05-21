import urllib.request
import urllib.parse
import json
import time

skills = [
    "agent-browser","agent-reach","ai-social-pro","apify-ultimate-scraper","auto-publisher",
    "browser-automation","canvas","caveman","claude-code-runner","cloudbase","competitive-analysis",
    "competitor-teardown","content-generator","content-hunter","context-product-manager",
    "CPO Chief Product Officer","cron-mastery","customer-persona","desktop-control",
    "desktop-control-1-0-0","diagnose","diagram-generator","diagram-maker","doubao-chat",
    "douyin-transcribe","easy-opencode","edgeone-clawscan","evomap",
    "feature-requirements-clarification","feishu-doc","feishu-drive","feishu-perm",
    "feishu-smart-doc-writer","feishu-wiki","filesystem","find-skills","free-ai-video-editor",
    "free-video-editor","Frontend Design","frontend-design","frontend-design-pro","github",
    "grill-me","hd-infoimage","healthcheck","huashu-nuwa","jianying","jingmai-product-publish",
    "Market Research","mcporter","mem0","memory-dream","memory-hygiene","Mobile",
    "multi-agent-collaboration","multi-search-engine","nano-banana-pro","node-connect",
    "node-inspect-debugger","Office","openclaw-ledger","opencli","opencli-agent",
    "opencli-explorer","opencli-oneshot","opencode","opencode-acp-control","opencode-cli",
    "opencode-controller","openmaic","phoenixclaw-ledger","playwright-cli",
    "playwright-scraper-skill","prd-writer","Product Manager","product-strategy",
    "python-debugpy","ralph-loop","react-best-practices","remotion-video-toolkit",
    "requirements-analysis","searxng","Self-Improving Proactive Agent",
    "Self-Improving Agent Proactive Self-Reflection","shorts-editor","simplify",
    "skill-creator","social-content","social-media-agent","social-media-manager",
    "social-media-publish","spike","taskflow","taskflow-inbox-triage","triple-memory",
    "ui-design","ui-ux-pro-max","user-research","video-frames","video-maker-free","weather",
    "web-access","web-monitor","web-scraper-as-a-service","wechat","wechat-article-scraper",
    "wechat-mp-cn","wechat-video-editor","wiki-knowledge-base","windows-control","wireframe"
]

base_url = "https://matrix.tencent.com/clawscan/skill_security"
results = []

for skill in skills:
    params = urllib.parse.urlencode({"skill_name": skill, "source": "clawhub"})
    url = f"{base_url}?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OpenClaw-Security-Scan/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = json.loads(resp.read().decode())
            verdict = content.get("verdict", "unknown")
            reason = content.get("reason", "")
            results.append({"skill": skill, "verdict": verdict, "reason": reason})
            print(f"[{verdict}] {skill}")
    except Exception as e:
        results.append({"skill": skill, "verdict": "unknown", "reason": f"Error: {e}"})
        print(f"[unknown] {skill} - Error: {e}")
    time.sleep(0.3)  # rate limiting

# Save to CSV
with open(r"E:\workspace\scripts\skill_scan_results.csv", "w", encoding="utf-8") as f:
    f.write("Skill,Verdict,Reason\n")
    for r in results:
        reason = r["reason"].replace('"', '""')
        f.write(f'"{r["skill"]}","{r["verdict"]}","{reason}"\n')

print(f"\nDone. {len(results)} skills scanned. Results saved.")
