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
    page.wait_for_timeout(5000)
    
    product_info = {
        'product_id': '16793098028',
        'jd_url': url,
    }
    
    # 1. 从页面文本中提取商品名称
    page_text = page.evaluate('document.body.innerText')
    
    # 商品名称 - 在标题位置
    title_match = re.search(r'公牛（[^\n]+B5440[^\n]+)', page_text)
    if title_match:
        product_info['title'] = title_match.group(1).strip()
        print(f"Title: {product_info['title']}")
    
    # 店铺
    shop_match = re.search(r'([^\n]+官方旗舰店)', page_text)
    if shop_match:
        product_info['shop'] = shop_match.group(1).strip()
        print(f"Shop: {product_info['shop']}")
    
    # 价格 - 尝试JavaScript获取
    try:
        # 京东价格通常在特定的JavaScript变量中
        price = page.evaluate('''
            () => {
                // 尝试多种方式获取价格
                const priceEl = document.querySelector('.p-price, .price, [class*="price"], #jdPricePriceDesc');
                if (priceEl) return priceEl.innerText;
                
                // 尝试从URL获取价格
                const priceText = document.body.innerText;
                const match = priceText.match(/￥\\s*([\\d.]+)/);
                if (match) return match[1];
                
                return null;
            }
        ''')
        if price:
            product_info['price'] = price
            print(f"Price: {price}")
    except Exception as e:
        print(f"Price error: {e}")
    
    # 品牌
    try:
        brand = page.evaluate('''
            () => {
                const brandEl = document.querySelector('[class*="brand"], [class*="brand-logo"]');
                if (brandEl) return brandEl.innerText;
                return '公牛';  // 默认值
            }
        ''')
        product_info['brand'] = brand
        print(f"Brand: {brand}")
    except Exception as e:
        product_info['brand'] = '公牛'
        print(f"Brand error: {e}, using default: 公牛")
    
    # 规格参数 - 尝试获取
    try:
        specs = {}
        # 尝试获取规格区域的内容
        spec_content = page.evaluate('''
            () => {
                const specs = {};
                const specEls = document.querySelectorAll('[class*="Ptable"], .parameter, [class*="spec"]');
                specEls.forEach(el => {
                    const text = el.innerText;
                    if (text.includes('：') || text.includes(':')) {
                        specs[el.className] = text.substring(0, 200);
                    }
                });
                return JSON.stringify(specs);
            }
        ''')
        if spec_content:
            product_info['specs_raw'] = spec_content
            print(f"Specs found: {len(spec_content)} chars")
    except Exception as e:
        print(f"Specs error: {e}")
    
    # 商品介绍/简述
    try:
        # 获取商品主图附近的内容
        desc = page.evaluate('''
            () => {
                const imgs = document.querySelectorAll('img');
                let maxSize = 0;
                let mainImg = '';
                imgs.forEach(img => {
                    const size = (img.width || 0) * (img.height || 0);
                    if (size > maxSize && img.src.includes('jdd')) {
                        maxSize = size;
                        mainImg = img.src;
                    }
                });
                return mainImg;
            }
        ''')
        product_info['main_image'] = desc
        print(f"Main image: {desc[:50] if desc else 'Not found'}...")
    except Exception as e:
        print(f"Image error: {e}")
    
    # 尝试获取商品详情
    try:
        detail_url = page.evaluate('''
            () => {
                const detailLink = document.querySelector('a[href*="detail"]');
                return detailLink ? detailLink.href : null;
            }
        ''')
        if detail_url:
            product_info['detail_url'] = detail_url
            print(f"Detail URL: {detail_url}")
    except Exception as e:
        print(f"Detail URL error: {e}")
    
    print("\n" + "="*60)
    print("商品信息:")
    print("="*60)
    print(json.dumps(product_info, ensure_ascii=False, indent=2))
    
    # 保存
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_product_data.json', 'w', encoding='utf-8') as f:
        json.dump(product_info, f, ensure_ascii=False, indent=2)
    print("\n数据已保存")
    
    browser.close()

print("\nDone!")
