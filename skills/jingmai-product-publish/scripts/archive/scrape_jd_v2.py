# -*- coding: utf-8 -*-
"""从京东商品页面抓取商品信息 - 改进版"""
import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://item.jd.com/16793098028.html"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

print(f"Fetching: {url}")

try:
    response = requests.get(url, headers=headers, timeout=15)
    response.encoding = 'gbk'
    
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. 商品名称 - 多种方式尝试
    title = None
    
    # 方式1: 搜索包含"名称"的标签
    for tag in soup.find_all(['div', 'h1', 'span', 'p']):
        text = tag.get_text(strip=True)
        if '德力西' in text and ('开关' in text or '插座' in text):
            title = text[:100]
            break
    
    # 方式2: 从script标签中提取
    if not title:
        scripts = soup.find_all('script')
        for script in scripts:
            text = script.string or ''
            if 'skuName' in text:
                match = re.search(r'skuName\s*[=:]\s*["\']([^"\']+)["\']', text)
                if match:
                    title = match.group(1)
                    break
    
    # 方式3: 直接搜索特定关键词
    if not title:
        for tag in soup.find_all(attrs={'class': re.compile(r'sku|goods|name|title', re.I)}):
            text = tag.get_text(strip=True)
            if len(text) > 5 and len(text) < 200:
                title = text
                break
    
    # 2. 价格
    price = None
    price_match = re.search(r'"tmanv":"(\d+\.?\d*)"', response.text)
    if price_match:
        price = price_match.group(1)
    
    # 3. 品牌
    brand = None
    brand_match = re.search(r'"brand"\s*:\s*"([^"]+)"', response.text)
    if brand_match:
        brand = brand_match.group(1)
    
    # 4. 商品编号
    product_id = re.search(r'/(\d+)\.html', url)
    if product_match := product_id:
        product_id = product_match.group(1)
    
    # 5. 店铺
    shop = None
    shop_match = re.search(r'"shopName"\s*:\s*"([^"]+)"', response.text)
    if shop_match:
        shop = shop_match.group(1)
    
    # 6. 规格参数
    specs = {}
    spec_section = soup.find('div', class_=re.compile(r'Ptable|spec|param', re.I))
    if spec_section:
        items = spec_section.find_all(['dt', 'dd'])
        for i in range(0, len(items)-1, 2):
            if items[i].get('class') and 'Ptable-title' in items[i].get('class'):
                key = items[i].get_text(strip=True)
                value = items[i+1].get_text(strip=True)
                specs[key] = value
    
    # 输出结果
    print("\n" + "=" * 60)
    print("商品信息")
    print("=" * 60)
    print(f"商品ID: {product_id}")
    print(f"商品标题: {title}")
    print(f"价格: {price}")
    print(f"品牌: {brand}")
    print(f"店铺: {shop}")
    print(f"规格参数: {specs}")
    
    # 保存
    result = {
        'url': url,
        'product_id': product_id,
        'title': title,
        'price': price,
        'brand': brand,
        'shop': shop,
        'specs': specs,
    }
    
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_product_info.txt', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to jd_product_info.txt")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
