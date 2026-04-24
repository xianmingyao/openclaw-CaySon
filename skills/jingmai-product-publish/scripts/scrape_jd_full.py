# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import json
import re

url = 'https://item.jd.com/16793098028.html'

print(f"Launching browser...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 2560, 'height': 1392})
    page = context.new_page()
    
    page.goto(url, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(5000)  # 更长等待时间
    
    product_info = {}
    
    # 1. 商品名称 - 尝试多种选择器
    selectors = [
        '[class*="sku-name"]',
        '[class*="product-name"]',
        'div[class*="title"]',
        '.item.glass-ui-style',
        '[class*="goodsInfo"] h1',
    ]
    for sel in selectors:
        try:
            title = page.eval_on_selector(sel, 'el => el.innerText', timeout=2000)
            if title and len(title) > 5:
                product_info['title'] = title.strip()
                print(f"Title [{sel}]: {title[:60]}...")
                break
        except:
            continue
    
    # 2. 价格 - 尝试多种选择器
    price_selectors = [
        '[class*="price"]',
        '[class*="p-price"]',
        '#price',
        '[class*="J-p-"]',
    ]
    for sel in price_selectors:
        try:
            price = page.eval_on_selector(sel, 'el => el.innerText', timeout=2000)
            if price and '￥' in price:
                product_info['price'] = price.strip()
                print(f"Price [{sel}]: {price}")
                break
            elif price and re.search(r'\d+', price):
                product_info['price'] = price.strip()
                print(f"Price [{sel}]: {price}")
                break
        except:
            continue
    
    # 3. 品牌 - 从页面内容中搜索
    try:
        page_content = page.content()
        brand_match = re.search(r'品牌[：:]\s*([^\s<]+)', page_content)
        if brand_match:
            product_info['brand'] = brand_match.group(1)
            print(f"Brand (regex): {product_info['brand']}")
    except Exception as e:
        print(f"Brand regex error: {e}")
    
    product_info['product_id'] = '16793098028'
    
    # 4. 规格参数 - 尝试P-table
    try:
        specs = {}
        spec_selectors = ['[class*="Ptable"]', '#product-detail-2', '[class*="detail"]']
        for sel in spec_selectors:
            try:
                spec_html = page.eval_on_selector(sel, 'el => el.innerHTML', timeout=2000)
                if spec_html and len(spec_html) > 100:
                    # 提取dt和dd
                    dt_matches = re.findall(r'<dt[^>]*>([^<]+)</dt>', spec_html)
                    dd_matches = re.findall(r'<dd[^>]*>([^<]+)</dd>', spec_html)
                    for i, dt in enumerate(dt_matches):
                        if i < len(dd_matches):
                            specs[dt.strip()] = dd_matches[i].strip()
                    if specs:
                        print(f"Specs [{sel}]: {len(specs)} items found")
                        break
            except:
                continue
        product_info['specs'] = specs
    except Exception as e:
        print(f"Specs error: {e}")
        product_info['specs'] = {}
    
    # 5. 获取完整页面文本用于调试
    try:
        all_text = page.evaluate('document.body.innerText')
        # 保存前2000字符用于分析
        with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_page_text.txt', 'w', encoding='utf-8') as f:
            f.write(all_text[:5000])
        print(f"\nPage text saved (first 5000 chars)")
    except Exception as e:
        print(f"Text save error: {e}")
    
    print("\n" + "="*60)
    print("商品完整信息:")
    print("="*60)
    print(json.dumps(product_info, ensure_ascii=False, indent=2))
    
    # 保存
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_product_data.json', 'w', encoding='utf-8') as f:
        json.dump(product_info, f, ensure_ascii=False, indent=2)
    print("\n数据已保存到 jd_product_data.json")
    
    browser.close()

print("\nDone!")
