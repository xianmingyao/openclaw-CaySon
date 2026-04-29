# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import json
import os
import re
import requests

# 创建目录
output_dir = r'E:\workspace\skills\jingmai-product-publish\product_data'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
os.makedirs(os.path.join(output_dir, 'specs'), exist_ok=True)

url = 'https://item.jd.com/16793098028.html'

print(f"Target: {url}")
print(f"Output: {output_dir}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    
    # 隐藏webdriver
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    """)
    
    print("\nNavigating...")
    page.goto(url, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(5000)
    
    # 1. 获取商品详情页HTML
    print("\n1. Extracting page HTML...")
    page_html = page.content()
    html_path = os.path.join(output_dir, 'page_source.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"   Saved: page_source.html")
    
    # 2. 获取商品图片
    print("\n2. Scraping product images...")
    images_info = []
    
    # 获取图片URL列表
    try:
        main_images = page.evaluate('''() => {
            const images = [];
            document.querySelectorAll('img').forEach((img, i) => {
                if (img.src && img.src.includes('jdd') && img.width > 100) {
                    images.push({
                        index: i,
                        src: img.src,
                        alt: img.alt || '',
                        width: img.width,
                        height: img.height
                    });
                }
            });
            return images;
        }''')
        print(f"   Found {len(main_images)} images")
        
        # 下载前10张图片
        for i, img_info in enumerate(main_images[:10]):
            try:
                img_url = img_info['src']
                if img_url and not img_url.startswith('data:'):
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200:
                        ext = os.path.splitext(img_url)[1] or '.jpg'
                        filename = f'product_img_{i+1}{ext}'
                        filepath = os.path.join(output_dir, 'images', filename)
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        print(f"   Downloaded: {filename}")
                        images_info.append({
                            'index': i+1,
                            'filename': filename,
                            'url': img_url
                        })
            except Exception as e:
                print(f"   Error downloading image {i}: {e}")
    except Exception as e:
        print(f"   Error getting images: {e}")
    
    # 3. 获取商品描述
    print("\n3. Extracting product description...")
    description = page.evaluate('''() => {
        let desc = '';
        const body = document.body.innerText;
        const scripts = document.querySelectorAll('script');
        for (const script of scripts) {
            const text = script.textContent || '';
            if (text.includes('colorSize') || text.includes('specification')) {
                desc += text.substring(0, 2000);
                break;
            }
        }
        return desc.substring(0, 5000);
    }''')
    
    desc_path = os.path.join(output_dir, 'description.txt')
    with open(desc_path, 'w', encoding='utf-8') as f:
        f.write(description)
    print(f"   Saved: description.txt ({len(description)} chars)")
    
    # 4. 获取商品属性
    print("\n4. Extracting product attributes...")
    attributes = page.evaluate('''() => {
        const attrs = {
            '防护等级': '',
            '材质': '',
            '颜色': '',
            '规格': '',
            '型号': '',
            '品牌': '',
            '插座类型': '',
            '线缆长度': '',
            '额定功率': '',
            '额定电压': ''
        };
        const body = document.body.innerText;
        const patterns = [
            [/防护等级[：:][^\n]+/, '防护等级'],
            [/材质[：:][^\n]+/, '材质'],
            [/颜色[：:][^\n]+/, '颜色'],
            [/规格[：:][^\n]+/, '规格'],
            [/型号[：:][^\n]+/, '型号'],
            [/品牌[：:][^\n]+/, '品牌'],
            [/插座类型[：:][^\n]+/, '插座类型'],
            [/线缆长度[：:][^\n]+/, '线缆长度'],
            [/额定功率[：:][^\n]+/, '额定功率'],
            [/额定电压[：:][^\n]+/, '额定电压']
        ];
        patterns.forEach(([pattern, key]) => {
            const match = body.match(pattern);
            if (match) {
                attrs[key] = match[0].split(/[：:]/)[1] || '';
            }
        });
        return attrs;
    }''')
    
    attrs_path = os.path.join(output_dir, 'attributes.json')
    with open(attrs_path, 'w', encoding='utf-8') as f:
        json.dump(attributes, f, ensure_ascii=False, indent=2)
    print(f"   Saved: attributes.json")
    
    # 5. 保存商品数据汇总
    print("\n5. Saving product data summary...")
    product_data = {
        'jd_url': url,
        'product_id': '16793098028',
        'title': '公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插 【8位】总控5米（新国标防过载）B5440',
        'brand': '公牛',
        'shop': '公牛官方旗舰店',
        'model': 'B5440',
        'attributes': attributes,
        'images': images_info,
        'price': {
            'jd_price': 70,
            'purchase_price': 66.5,
            'market_price': 82.35
        }
    }
    
    data_path = os.path.join(output_dir, 'product_data.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(product_data, f, ensure_ascii=False, indent=2)
    print(f"   Saved: product_data.json")
    
    # 6. 截图商品页面
    print("\n6. Taking screenshot...")
    screenshot_path = os.path.join(output_dir, 'product_page.png')
    page.screenshot(path=screenshot_path, full_page=False)
    print(f"   Saved: product_page.png")
    
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
if os.path.exists(os.path.join(output_dir, 'images')):
    for f in os.listdir(os.path.join(output_dir, 'images')):
        print(f"  - images/{f}")
