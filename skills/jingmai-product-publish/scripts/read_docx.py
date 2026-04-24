# -*- coding: utf-8 -*-
import os
import sys
from docx import Document

folder = r'E:\workspace\skills\desktop-control-cli'
docx_file = None

for f in os.listdir(folder):
    if f.endswith('.docx') and 'jingmai' in f.lower():
        docx_file = os.path.join(folder, f)
        break
    elif f.endswith('.docx') and '\u4eac\u9ea6' in f:
        docx_file = os.path.join(folder, f)
        break

if not docx_file:
    # Try to find by listing all files
    for f in os.listdir(folder):
        if 'docx' in f.lower():
            print(f"Found: {f}")
            docx_file = os.path.join(folder, f)
            break

if docx_file:
    print(f"Reading: {docx_file}")
    doc = Document(docx_file)
    for para in doc.paragraphs:
        if para.text.strip():
            print(para.text)
else:
    print("File not found!")
