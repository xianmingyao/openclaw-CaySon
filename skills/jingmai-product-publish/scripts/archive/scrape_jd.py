# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import json

url = 'https://item.jd.com/16793098028.html'

print(f"Launching browser...")
print(f"Navigating to: {url}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 2560, 'height': 1392})
    page = context.new_page()
    
    page.goto(url, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(3000)
    
    product_info = {}
    
    # 商品名称
    try:
        title = page.eval_on_selector('[class*="sku-name"]', 'el => el.innerText')
        product_info['title'] = title
        print(f"Title: {title[:50]}...")
    except Exception as e:
        print(f"Title error: {e}")
        product_info['title'] = None
    
    # 价格
    try:
        price = page.eval_on_selector('[class*="p-price"]', 'el => el.innerText')
        product_info['price'] = price
        print(f"Price: {price}")
    except Exception as e:
        print(f"Price error: {e}")
        product_info['price'] = None
    
    # 品牌
    try:
        brand = page.eval_on_selector('[class*="brand"] a', 'el => el.innerText')
        product_info['brand'] = brand
        print(f"Brand: {brand}")
    except Exception as e:
        print(f"Brand error: {e}")
        product_info['brand'] = None
    
    product_info['product_id'] = '16793098028'
    
    # 规格参数
    try:
        specs = {}
        spec_section = page.query_selector('[class*="Ptable"]')
        if spec_section:
            items = spec_section.query_selector_all('[class*="Ptable-item"]')
            for item in items:
                key_el = item.query_selector('dt')
                value_el = item.query_selector('dd')
                if key_el and value_el:
                    key = key_el.inner_text()
                    value = value_el.inner_text()
                    specs[key] = value
        product_info['specs'] = specs
        print(f"Specs count: {len(specs)}")
    except Exception as e:
        print(f"Specs error: {e}")
        product_info['specs'] = {}
    
    # 店铺
    try:
        shop = page.eval_on_selector('[class*="shop-name"]', 'el => el.innerText')
        product_info['shop'] = shop
        print(f"Shop: {shop}")
    except Exception as e:
        print(f"Shop error: {e}")
        product_info['shop'] = None
    
    print("\n" + "="*60)
    print("商品完整信息:")
    print("="*60)
    print(json.dumps(product_info, ensure_ascii=False, indent=2))
    
    # 保存到文件
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_product_data.json', 'w', encoding='utf-8') as f:
        json.dump(product_info, f, ensure_ascii=False, indent=2)
    print("\n数据已保存到 jd_product_data.json")
    
    browser.close()

print("\nDone!")
