# -*- coding: utf-8 -*-
"""读取上架表格"""
import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel(r'C:\Users\Administrator\.openclaw\media\inbound\湖南上架表格---3d1a1330-8d02-4896-af00-272e57cf31e1.xlsx', engine='openpyxl')

print("=== 列名 ===")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print("\n=== 数据 ===")
for i, row in df.iterrows():
    print(f"Row {i}: {list(row.values)}")
