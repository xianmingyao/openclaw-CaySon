# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import json
import os

# 创建目录
output_dir = r'E:\workspace\skills\jingmai-product-publish\product_data'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)

url = 'https://item.jd.com/16793098028.html'

print(f"Target: {url}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    
    print("\nNavigating...")
    page.goto(url, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(5000)
    
    # 截图
    print("\n1. Taking screenshot...")
    screenshot_path = os.path.join(output_dir, 'product_page.png')
    page.screenshot(path=screenshot_path, full_page=False)
    print(f"   Saved: product_page.png")
    
    # 获取页面文本
    print("\n2. Getting page text...")
    page_text = page.evaluate('document.body.innerText')
    text_path = os.path.join(output_dir, 'page_text.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(page_text)
    print(f"   Saved: page_text.txt ({len(page_text)} chars)")
    
    # 获取商品基本信息
    print("\n3. Extracting product info...")
    
    # 从页面文本中提取关键信息
    lines = page_text.split('\n')
    product_info = {
        'jd_url': url,
        'product_id': '16793098028',
        'title': '',
        'brand': '公牛',
        'shop': '公牛官方旗舰店',
        'model': 'B5440',
        'attributes': {}
    }
    
    # 搜索关键行
    for i, line in enumerate(lines):
        if '公牛' in line and 'B5440' in line:
            product_info['title'] = line.strip()
            print(f"   Title: {line.strip()[:50]}...")
        if '旗舰店' in line:
            product_info['shop'] = line.strip()
            print(f"   Shop: {line.strip()}")
    
    # 提取属性
    keywords = ['材质', '规格', '型号', '防护', '颜色', '长度', '功率', '电压']
    for kw in keywords:
        for line in lines:
            if kw in line:
                product_info['attributes'][kw] = line.strip()
                print(f"   {kw}: {line.strip()[:30]}")
                break
    
    # 保存
    data_path = os.path.join(output_dir, 'product_data.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(product_info, f, ensure_ascii=False, indent=2)
    print(f"   Saved: product_data.json")
    
    browser.close()

print("\n" + "="*60)
print("SCRAPING COMPLETE!")
print("="*60)
print(f"\nData saved to: {output_dir}")
print("\nFiles created:")
for f in os.listdir(output_dir):
    fpath = os.path.join(output_dir, f)
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath)
        print(f"  - {f} ({size} bytes)")
