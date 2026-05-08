# -*- coding: utf-8 -*-
"""Debug SKU product name field"""
import sys
sys.path.insert(0, r"E:\workspace\skills\jingmai-product-publish")

from actions._uia_helpers import find_jingmai_uia_window, iter_named_descendants
import time

window = find_jingmai_uia_window()
if window:
    # Scroll to SKU section first
    import pyautogui
    pyautogui.moveTo(1800, 1000)
    for _ in range(12):
        pyautogui.scroll(700)
        time.sleep(0.05)
    time.sleep(0.5)

    # Find Edit elements in SKU region
    print("Edit elements in SKU region (left < 1800, top 520-720):")
    for candidate in iter_named_descendants(window, control_types=['Edit'], limit=80):
        name = candidate.get('name', '') or ''
        rect = candidate.get('rect')
        if rect:
            top = rect.top
            left = rect.left
            right = rect.right
            bottom = rect.bottom
            if left < 1800 and 520 <= top <= 720:
                print(f"  name='{name}', top={top}, left={left}, right={right}, bottom={bottom}")
else:
    print('No window found')
