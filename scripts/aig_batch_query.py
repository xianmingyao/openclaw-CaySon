import urllib.request, json, concurrent.futures

skills = [
    ('auto-publisher','clawhub'),
    ('cloudbase','clawhub'),
    ('content-hunter','clawhub'),
    ('doubao-chat','clawhub'),
    ('douyin-transcribe-skill','clawhub'),
    ('feishu-smart-doc-writer','clawhub'),
    ('frontend-design','clawhub'),
    ('nano-banana-pro','clawhub'),
    ('opencli-skills','clawhub'),
    ('phoenixclaw-ledger','clawhub'),
    ('playwright-scraper-skill','clawhub'),
    ('skill-9','clawhub'),
    ('summarize','clawhub'),
    ('video-summary','clawhub'),
    ('wechat','clawhub'),
    ('wechat-article-scraper','clawhub'),
    ('wechat-mp-cn','clawhub'),
]

base = 'https://matrix.tencent.com/clawscan'
results = {}

def fetch(sk, src):
    try:
        url = base + '/skill_security?skill_name=' + sk + '&source=' + src
        r = urllib.request.urlopen(url, timeout=10)
        return (sk, json.loads(r.read().decode()))
    except Exception as e:
        return (sk, {'verdict': 'unknown', 'reason': str(e)})

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch, s, src): s for s, src in skills}
    for f in concurrent.futures.as_completed(futs):
        k, v = f.result()
        results[k] = v

for k, v in results.items():
    reason = v.get('reason', '')
    print(k + ': ' + v['verdict'] + ' | ' + reason)
