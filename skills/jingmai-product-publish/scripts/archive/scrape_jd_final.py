# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import json
import re

url = 'https://item.jd.com/16793098028.html'

print("Launching browser...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 2560, 'height': 1392})
    page = context.new_page()
    
    page.goto(url, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(5000)
    
    product_info = {
        'product_id': '16793098028',
        'jd_url': url,
    }
    
    page_text = page.evaluate('document.body.innerText')
    
    # 商品名称 - 搜索B5440
    if 'B5440' in page_text:
        idx = page_text.find('B5440')
        product_info['title'] = page_text[max(0, idx-50):idx+30].replace('\n', ' ').strip()
        print(f"Title: {product_info['title']}")
    
    # 店铺 - 搜索旗舰店
    if '旗舰店' in page_text:
        idx = page_text.find('旗舰店')
        product_info['shop'] = page_text[max(0, idx-10):idx+4].replace('\n', '').strip()
        print(f"Shop: {product_info['shop']}")
    
    # 价格 - 搜索价格符号
    price_match = re.search(r'[￥¥]\s*([\d.]+)', page_text)
    if price_match:
        product_info['price'] = price_match.group(1)
        print(f"Price: {product_info['price']}")
    
    # 品牌 - 默认公牛
    product_info['brand'] = '公牛'
    print(f"Brand: {product_info['brand']}")
    
    # 保存完整页面用于调试
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_page_full.txt', 'w', encoding='utf-8') as f:
        f.write(page_text)
    print(f"Page text saved: {len(page_text)} chars")
    
    print("\n" + "="*60)
    print("商品信息:")
    print("="*60)
    print(json.dumps(product_info, ensure_ascii=False, indent=2))
    
    # 保存
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_product_data.json', 'w', encoding='utf-8') as f:
        json.dump(product_info, f, ensure_ascii=False, indent=2)
    print("\n数据已保存到 jd_product_data.json")
    
    browser.close()

print("\nDone!")
