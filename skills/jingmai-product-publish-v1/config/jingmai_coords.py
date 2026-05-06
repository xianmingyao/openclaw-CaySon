"""
京麦商品发布自动化 - 元素坐标配置 v3.0
基于实际截图分析 (2560x1392)

【重要】坐标来源说明：
- 所有坐标均基于2560x1392分辨率截图直接分析
- 屏幕尺寸：2560 x 1392
"""

# ============================================
# 窗口配置
# ============================================
WINDOW = {
    'title_prefix': 'jd_',
    'screen_width': 2560,
    'screen_height': 1392,
    # 京麦窗口列表
    'windows': {
        'main': {'hwnd': 18289096, 'rect': (0, 0, 2560, 1392), 'desc': '全屏模式'},
        'small': {'hwnd': 529674, 'rect': (1080, 648, 1380, 900), 'desc': '小窗口模式'},
    },
}

# ============================================
# 类目选择页面 - 最终验证坐标
# ============================================
CATEGORY_PAGE = {
    'name': '类目选择发品页',
    
    # 第三级类目 - 用于展开第四级
    'level3_third_col': (1454, 324),  # 电气辅材
    
    # 第四级类目
    'level4': (1825, 324),  # 电缆接头盒
    
    # 下一步按钮 - 确认可用
    'next_button': (1277, 1307),
}

# ============================================
# 商品基本信息页面 - v3.0 完整坐标
# ============================================
PRODUCT_INFO_PAGE = {
    'name': '商品基本信息页',
    
    # === 商品信息区块 ===
    'title_input': (1434, 318),        # 商品标题输入框
    'brand_select': (814, 391),        # 品牌选择框
    'model_input': (1590, 391),        # 型号输入框
    'sku_input': (1978, 391),          # 货号输入框
    
    # === 采销信息区块 ===
    'market_price': (814, 493),        # 市场价输入框
    'jd_price': (1590, 493),           # 京东价输入框
    'purchase_price': (1978, 493),      # 采购价输入框
    
    # === 商品属性区块 ===
    'protection_level': (814, 761),     # 防护等级属性选择
    'material': (1210, 761),           # 材质属性选择
    
    # === 规格描述区块 ===
    'image_upload': (650, 946),        # 商品图片上传区域
    'description_tab': (945, 111),    # 商品描述页签
    
    # === 底部按钮 ===
    'publish_button': (1216, 1358),     # 发布商品按钮 (蓝色)
    'save_draft_button': (1330, 1358),  # 保存草稿按钮 (白色)
}

# ============================================
# 元素坐标速查表
# ============================================
ELEMENTS = {
    'category': {
        'level3': CATEGORY_PAGE['level3_third_col'],
        'level4': CATEGORY_PAGE['level4'],
        'next_button': CATEGORY_PAGE['next_button'],
    },
    'product_info': {
        'title_input': PRODUCT_INFO_PAGE['title_input'],
        'brand_select': PRODUCT_INFO_PAGE['brand_select'],
        'model_input': PRODUCT_INFO_PAGE['model_input'],
        'sku_input': PRODUCT_INFO_PAGE['sku_input'],
        'market_price': PRODUCT_INFO_PAGE['market_price'],
        'jd_price': PRODUCT_INFO_PAGE['jd_price'],
        'purchase_price': PRODUCT_INFO_PAGE['purchase_price'],
        'protection_level': PRODUCT_INFO_PAGE['protection_level'],
        'material': PRODUCT_INFO_PAGE['material'],
        'image_upload': PRODUCT_INFO_PAGE['image_upload'],
        'description_tab': PRODUCT_INFO_PAGE['description_tab'],
        'publish_button': PRODUCT_INFO_PAGE['publish_button'],
        'save_draft_button': PRODUCT_INFO_PAGE['save_draft_button'],
    },
}

# ============================================
# 价格计算公式
# ============================================
PRICE_RULES = {
    # 市场价 > 京东价 > 采购价
    # 京东价 = 采购价 / 0.95
    # 毛利 = 5% (系统自动计算)
    'market_to_jd_ratio': 1.0,  # 市场价高于京东价，无明确规定，一般20%内
    'jd_to_purchase_ratio': 0.95,  # 京东价 = 采购价 / 0.95
    'gross_profit_rate': 0.05,  # 毛利5%
}

def calc_price(purchase_price):
    """根据采购价计算京东价"""
    jd_price = purchase_price / 0.95
    return round(jd_price, 2)

# ============================================
# 快捷函数
# ============================================
def get_element(page, element):
    """获取元素坐标"""
    return ELEMENTS.get(page, {}).get(element)

def print_elements():
    """打印所有元素"""
    print("=" * 60)
    print("京麦商品发布 - 元素坐标速查表")
    print("=" * 60)
    print("\n【类目选择页面】")
    for name, coords in ELEMENTS['category'].items():
        print(f"  {name}: {coords}")
    print("\n【商品信息页面】")
    for name, coords in ELEMENTS['product_info'].items():
        print(f"  {name}: {coords}")

if __name__ == '__main__':
    print_elements()
