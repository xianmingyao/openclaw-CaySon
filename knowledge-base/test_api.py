#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test MiniMax API connection"""
from openai import OpenAI

MINIMAX_API_KEY = "sk-cp-3b3Ek6Vdna7iLAYz2kD6JiZL_W8x0j5TX8XIlqKex4JobdGEea4SESTayaD3FfAbc3HNteY8QZyFx9QeFm533E3pXQ4-ZW1iPEpGnr5Rl8DpmdgQX4B-xU8"
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"
MODEL = "MiniMax-M2.5-highspeed"

client = OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)

print("Testing MiniMax API...")
try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Say 'OK' in one word"}],
        max_tokens=10,
        timeout=30  # 30 second timeout
    )
    print(f"Response: {response.choices[0].message.content}")
    print("API test SUCCESS!")
except Exception as e:
    print(f"API test FAILED: {e}")
