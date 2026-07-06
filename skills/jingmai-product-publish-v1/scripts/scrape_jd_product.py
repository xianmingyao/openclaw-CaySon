# -*- coding: utf-8 -*-
"""从京东商品页面抓取商品信息"""
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
    response.encoding = 'gbk'  # 京东用gbk编码
    
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取商品信息
    product_info = {}
    
    # 商品名称
    title = soup.find('div', class_='sku-name')
    if title:
        product_info['title'] = title.get_text(strip=True)
    
    # 价格
    price = soup.find('span', class_='price')
    if not price:
        price = soup.find('span', class_='p-price')
    if price:
        product_info['price'] = price.get_text(strip=True)
    
    # 品牌
    brand = soup.find('a', id='parameter-brand')
    if brand:
        product_info['brand'] = brand.get('title', '')
    
    # 商品编号
    product_id = soup.find('span', class_='product-id')
    if not product_id:
        # 从URL提取
        match = re.search(r'/(\d+)\.html', url)
        if match:
            product_info['product_id'] = match.group(1)
    
    # 规格参数
    spec_table = soup.find('div', class_='Ptable')
    if spec_table:
        specs = {}
        items = spec_table.find_all('div', class_='Ptable-item')
        for item in items:
            dt = item.find('dt', class_='Ptable-title')
            dd = item.find('dd', class_='Ptable-value')
            if dt and dd:
                specs[dt.get_text(strip=True)] = dd.get_text(strip=True)
        product_info['specs'] = specs
    
    # 商品详情
    detail = soup.find('div', class_='detail')
    if detail:
        product_info['detail'] = detail.get_text(strip=True)[:500]
    
    # 输出结果
    print("\n" + "=" * 60)
    print("商品信息")
    print("=" * 60)
    for key, value in product_info.items():
        if key != 'specs':
            print(f"{key}: {value}")
        else:
            print(f"{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
    
    # 保存到文件
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_product_info.txt', 'w', encoding='utf-8') as f:
        json.dump(product_info, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to jd_product_info.txt")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
