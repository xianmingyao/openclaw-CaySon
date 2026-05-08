# -*- coding: utf-8 -*-
"""Debug SKU product name field - show ALL elements"""
import sys
sys.path.insert(0, r"E:\workspace\skills\jingmai-product-publish")

from actions._uia_helpers import find_jingmai_uia_window
from actions.form import _scroll_to_sku_section, _find_edit_elements
import time

def debug_sku_all():
    window = find_jingmai_uia_window()
    if not window:
        print('No window found')
        return

    # Scroll to SKU section
    _scroll_to_sku_section()
    time.sleep(0.5)

    # Find ALL edit elements in SKU region
    print("ALL Edit elements in SKU region (top 520-720, any left):")
    for elem, name, rect in _find_edit_elements():
        top = rect.top
        if 520 <= top <= 720:
            print(f"  name='{name}', top={top}, left={rect.left}, right={rect.right}, bottom={rect.bottom}")
            # Try to get current value
            try:
                current_val = elem.get_value()
                print(f"    current value: '{current_val}'")
            except Exception as e:
                print(f"    get_value error: {e}")

    print("\n--- Trying set_edit_text on '请输入' at left>=1800 ---")
    for elem, name, rect in _find_edit_elements():
        top = rect.top
        left = rect.left
        if 520 <= top <= 720 and left >= 1800 and '请输入' in name:
            print(f"Found: name='{name}', left={left}, top={top}")
            try:
                # Clear and set new value
                test_title = "公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插 【8位】总控1.6米（新国标防过载）B5440"
                elem.set_edit_text(test_title)
                time.sleep(0.3)
                new_val = elem.get_value()
                print(f"  Set to: '{new_val}'")
                if test_title in new_val:
                    print(f"  SUCCESS - value matches!")
                else:
                    print(f"  FAIL - value mismatch!")
            except Exception as e:
                print(f"  ERROR: {e}")

if __name__ == "__main__":
    debug_sku_all()
