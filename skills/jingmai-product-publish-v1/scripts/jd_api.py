# -*- coding: utf-8 -*-
"""从京东API获取商品信息"""
import requests
import json

product_id = "16793098028"

# 京东价格API
price_url = f"https://p.3.cn/prices/mgets?skuIds=J_{product_id}"
print(f"Price API: {price_url}")

try:
    response = requests.get(price_url, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    prices = response.json()
    if prices:
        print("\n价格信息:")
        for p in prices:
            print(f"  商品ID: {p.get('id')}")
            print(f"  价格: {p.get('p')}")
            print(f"  类型: {p.get('t')}")
except Exception as e:
    print(f"Error: {e}")

# 京东商品信息API
print("\n" + "=" * 60)
info_url = f"https://c0.3.cn/stock?skuId={product_id}&area=1_72_4139_0&venderId=1000004127&shopId=1000004127&cat=737%2C744%2C1105&productionId=100008816&weight=0.65kg&dim=1"
print(f"Stock API: {info_url}")

try:
    response = requests.get(info_url, timeout=10)
    response.encoding = 'utf-8'
    data = response.json()
    
    print("\n商品库存信息:")
    print(f"  商品名: {data.get('stockInfo', {}).get('skuName', 'N/A')}")
    print(f"  品牌: {data.get('stockInfo', {}).get('brandName', 'N/A')}")
    print(f"  店铺: {data.get('stockInfo', {}).get('shopName', 'N/A')}")
    
    # 保存
    with open(r'E:\workspace\skills\jingmai-product-publish\logs\jd_product_info.txt', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to jd_product_info.txt")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
