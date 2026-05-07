#!/usr/bin/env python
from pathlib import Path
from openai import OpenAI
import json

client = OpenAI(
    api_key="sk-cp-3b3Ek6Vdna7iLAYz2kD6JiZL_W8x0j5TX8XIlqKex4JobdGEea4SESTayaD3FfAbc3HNteY8QZyFx9QeFm533E3pXQ4-ZW1iPEpGnr5Rl8DpmdgQX4B-xU8",
    base_url="https://api.minimax.chat/v1"
)

f = list(Path(r"E:\workspace\knowledge-base\wiki\概念").glob("*.md"))[0]
content = f.read_text(encoding="utf-8", errors="replace")[:3000]

messages = [
    {"role": "system", "content": "You are a graphify agent. Output ONLY valid JSON."},
    {"role": "user", "content": f"=== FILE: {f.name} ===\n{content}"}
]

response = client.chat.completions.create(
    model="MiniMax-M2.5-highspeed",
    messages=messages,
    temperature=0.1,
    max_tokens=2048,
    response_format={"type": "json_object"}
)
raw = response.choices[0].message.content or ""
print(f"Raw (first 300): {raw[:300]}")

if raw.strip():
    result = json.loads(raw)
    print(f"Nodes: {len(result.get('nodes', []))}, Edges: {len(result.get('edges', []))}")
else:
    print("Empty response")
