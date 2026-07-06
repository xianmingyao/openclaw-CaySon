#!/usr/bin/env python
import json, time
from pathlib import Path
from openai import OpenAI

MINIMAX_API_KEY = "sk-cp-3b3Ek6Vdna7iLAYz2kD6JiZL_W8x0j5TX8XIlqKex4JobdGEea4SESTayaD3FfAbc3HNteY8QZyFx9QeFm533E3pXQ4-ZW1iPEpGnr5Rl8DpmdgQX4B-xU8"
MODEL = "MiniMax-M2.5"

client = OpenAI(api_key=MINIMAX_API_KEY, base_url="https://api.minimax.chat/v1")
INPUT_DIR = Path(r"E:\workspace\knowledge-base")
WIKI_DIR = INPUT_DIR / "wiki"

files = list((WIKI_DIR / "概念").glob("*.md"))[:3]
print(f"Testing with {len(files)} files")

for f in files:
    content = f.read_text(encoding="utf-8", errors="replace")[:5000]
    file_rel = f.relative_to(INPUT_DIR)
    messages = [
        {"role": "system", "content": 'You are a graphify agent. Output ONLY valid JSON: {"nodes":[],"edges":[],"hyperedges":[]}'},
        {"role": "user", "content": f"=== FILE: {file_rel} ===\n{content}"}
    ]
    t0 = time.time()
    response = client.chat.completions.create(model=MODEL, messages=messages, temperature=0.1, max_tokens=2048, response_format={"type": "json_object"})
    elapsed = time.time() - t0
    raw = response.choices[0].message.content or ""
    print(f"Raw response: {raw[:200] if raw else 'EMPTY'}")
    if raw:
        result = json.loads(raw)
        print(f"{f.name}: {len(result.get('nodes', []))} nodes, {len(result.get('edges', []))} edges ({elapsed:.1f}s)")
    else:
        print(f"{f.name}: EMPTY RESPONSE")

print("Test complete!")
