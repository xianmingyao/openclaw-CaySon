# -*- coding: utf-8 -*-
"""查找京麦快捷方式路径"""
import os
import sys
import glob

desktop = os.path.join(os.path.expanduser("~"), "Desktop")

# 查找所有.lnk文件
lnk_files = glob.glob(os.path.join(desktop, "*.lnk"))

for f in lnk_files:
    # 尝试读取快捷方式目标
    try:
        import pythoncom
        from win32com.shell.shortcut import Shortcut
        s = Shortcut(f)
        target = s.GetPath()
        name = os.path.basename(f)
        if "jingmai" in target.lower() or "jingmai" in name.lower():
            print(f"找到京麦: {name}")
            print(f"  路径: {target}")
    except Exception as e:
        pass

# 也搜索常见安装目录
search_paths = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"E:\Program Files",
]

for base in search_paths:
    if os.path.exists(base):
        for root, dirs, files in os.walk(base):
            for d in dirs:
                if "jingmai" in d.lower():
                    print(f"找到目录: {os.path.join(root, d)}")
            for f in files:
                if "jingmai" in f.lower() and f.endswith(".exe"):
                    print(f"找到EXE: {os.path.join(root, f)}")
