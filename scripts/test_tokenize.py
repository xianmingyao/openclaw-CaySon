#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tokenize
import io

file_path = r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py'

with open(file_path, 'rb') as f:
    source = f.read()

# Try tokenizing
try:
    tokens = list(tokenize.tokenize(io.BytesIO(source).readline))
    print(f'Tokenization successful! Got {len(tokens)} tokens')
except tokenize.TokenError as e:
    print(f'TokenError: {e}')
except SyntaxError as e:
    print(f'SyntaxError during tokenization: {e}')
