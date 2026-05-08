# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"E:\workspace\skills\jingmai-product-publish")
from executor import Executor
from pathlib import Path

config_path = Path(r"E:\workspace\skills\jingmai-product-publish\data\b5440_huicai_plan_v2.json")
executor = Executor(config_path=config_path)

# Mark steps 1-4 as success
for i in range(4):
    executor.plan['plan'][i]['status'] = 'success'
    print(f"Marked step {i+1} as success")

executor.plan['current_step'] = 5
executor.plan['status'] = 'running'
executor.save_plan()
print(f"Plan updated: current_step = {executor.plan['current_step']}")
