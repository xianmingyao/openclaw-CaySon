# -*- coding: utf-8 -*-
import os
import sys
import re

# Set console encoding
sys.stdout.reconfigure(encoding='utf-8')

folder = r'E:\workspace\skills\desktop-control-cli'

# Find the docx file
for f in os.listdir(folder):
    if f.endswith('.docx'):
        docx_path = os.path.join(folder, f)
        print(f"Found: {f}")
        
        from docx import Document
        doc = Document(docx_path)
        
        print("\n=== 京麦商品上架流程 ===\n")
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                # Try to ensure proper encoding
                try:
                    print(text)
                except:
                    print(text.encode('gbk', errors='ignore').decode('gbk'))
        break
