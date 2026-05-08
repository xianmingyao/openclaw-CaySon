# -*- coding: utf-8 -*-
"""Debug SKU product name field - wider search"""
import sys
sys.path.insert(0, r"E:\workspace\skills\jingmai-product-publish")

from actions._uia_helpers import find_jingmai_uia_window, iter_named_descendants
import time

def scroll_to_sku_section():
    import pyautogui
    pyautogui.moveTo(1800, 1000)
    # Scroll to top first
    for _ in range(12):
        pyautogui.scroll(700)
        time.sleep(0.05)
    time.sleep(0.3)
    # Then scroll down to SKU section
    for _ in range(2):
        pyautogui.scroll(-550)
        time.sleep(0.25)

window = find_jingmai_uia_window()
if window:
    scroll_to_sku_section()
    time.sleep(0.5)

    print("ALL Edit elements in middle region (top 300-800):")
    for candidate in iter_named_descendants(window, control_types=['Edit'], limit=80):
        name = candidate.get('name', '') or ''
        rect = candidate.get('rect')
        if rect:
            top = rect.top
            left = rect.left
            right = rect.right
            bottom = rect.bottom
            if 300 <= top <= 800:
                print(f"  name='{name}', top={top}, left={left}, right={right}, bottom={bottom}")
else:
    print('No window found')
