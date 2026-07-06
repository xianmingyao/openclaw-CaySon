#!/usr/bin/env python3
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish')
from jingmai_publish.desktop.uia_adapter import RealWindowsUIAAdapter
import time

adapter = RealWindowsUIAAdapter(screenshot_dir='resources/screenshots')
window_handle = '19271502'

# 探测额定电压选项
print('=== 探测 额定电压 ===')
result = adapter.probe_select_options_by_label(window_handle, '额定电压')
print(f'success: {result["success"]}')
print(f'options: {result.get("options", [])}')

time.sleep(0.5)

# 探测电缆长度选项
print()
print('=== 探测 电缆长度 ===')
result = adapter.probe_select_options_by_label(window_handle, '电缆长度')
print(f'success: {result["success"]}')
print(f'options: {result.get("options", [])}')
