#!/usr/bin/env python
from pathlib import Path
from openai import OpenAI
import json
import re

MINIMAX_API_KEY = "sk-cp-3b3Ek6Vdna7iLAYz2kD6JiZL_W8x0j5TX8XIlqKex4JobdGEea4SESTayaD3FfAbc3HNteY8QZyFx9QeFm533E3pXQ4-ZW1iPEpGnr5Rl8DpmdgQX4B-xU8"
MODEL = "MiniMax-M2.5-highspeed"

client = OpenAI(api_key=MINIMAX_API_KEY, base_url="https://api.minimax.chat/v1")

files = list(Path(r"E:\workspace\knowledge-base\wiki\概念").glob("*.md"))[:3]
print(f"Testing with {len(files)} files")

for f in files:
    content = f.read_text(encoding="utf-8", errors="replace")[:3000]
    messages = [
        {"role": "system", "content": "You are a graphify agent. Output ONLY valid JSON."},
        {"role": "user", "content": f"=== FILE: {f.name} ===\n{content}"}
    ]
    response = client.chat.completions.create(model=MODEL, messages=messages, temperature=0.1, max_tokens=2048, response_format={"type": "json_object"})
    raw = response.choices[0].message.content or ""

    # Strip thinking content
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    json_start = raw.find("{")
    if json_start == -1:
        print(f"{f.name}: NO JSON FOUND, raw: {raw[:100]}")
        continue

    json_str = raw[json_start:]
    try:
        result = json.loads(json_str)
        print(f"{f.name}: {len(result.get('nodes', []))} nodes, {len(result.get('edges', []))} edges")
    except json.JSONDecodeError as e:
        print(f"{f.name}: JSON ERROR: {e}, raw: {raw[:200]}")

print("Test complete!")
