# -*- coding: utf-8 -*-
"""Debug SKU product name field element"""
import sys
sys.path.insert(0, r"E:\workspace\skills\jingmai-product-publish")

from actions._uia_helpers import find_jingmai_uia_window, iter_named_descendants
from actions.form import _scroll_to_sku_section, _find_edit_elements
import time

def debug_sku_element():
    window = find_jingmai_uia_window()
    if not window:
        print('No window found')
        return

    # Scroll to SKU section
    _scroll_to_sku_section()
    time.sleep(0.5)

    # Find all edit elements in SKU region
    print("Edit elements in SKU region (left >= 1800, top 520-720):")
    for elem, name, rect in _find_edit_elements():
        left = rect.left
        top = rect.top
        right = rect.right
        bottom = rect.bottom
        if left >= 1800 and 520 <= top <= 720:
            print(f"  name='{name}', top={top}, left={left}, right={right}, bottom={bottom}")
            print(f"  element type: {type(elem)}")
            print(f"  has set_edit_text: {hasattr(elem, 'set_edit_text')}")
            
            # Try to get current value
            try:
                current_val = elem.get_value()
                print(f"  current value: '{current_val}'")
            except Exception as e:
                print(f"  get_value error: {e}")
            
            # Try to use set_edit_text
            try:
                elem.set_edit_text("TEST_INPUT")
                print(f"  set_edit_text SUCCESS")
                time.sleep(0.3)
                # Verify
                new_val = elem.get_value()
                print(f"  after set, value: '{new_val}'")
            except Exception as e:
                print(f"  set_edit_text ERROR: {e}")

if __name__ == "__main__":
    debug_sku_element()
