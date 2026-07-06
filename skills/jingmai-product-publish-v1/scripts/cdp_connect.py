# -*- coding: utf-8 -*-
"""使用CDP连接京麦"""
import sys
import json
import subprocess

# 京麦进程信息
jm_pid = 65988
print(f"京麦进程ID: {jm_pid}")

# 尝试获取CDP端口
# 京麦通常使用随机端口，我们需要枚举
import win32process
import win32gui
import win32con
import win32api

def get_chrome_debug_urls(pid):
    """获取指定进程的调试URL"""
    # Chrome/Edge/CEF的CDP端口通过命名管道暴露
    import os
    pipe_pattern = f"\\\\.\\pipe\\chrome-debugging-port-{pid}"
    
    # 尝试WebDriver端口
    ports = [9222, 9223, 9224, 9225, 9226, 9227, 9228, 9229, 9230]
    
    for port in ports:
        try:
            import urllib.request
            url = f"http://localhost:{port}/json"
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req, timeout=1)
            data = json.loads(resp.read())
            print(f"找到CDP: http://localhost:{port}")
            print(f"页面: {data}")
            return port
        except:
            pass
    return None

# 方法1: 尝试localhost:9222
print("\n=== 尝试连接CDP端口 ===")
port = get_chrome_debug_urls(jm_pid)
if not port:
    print("未找到CDP端口，尝试其他方法...")

# 方法2: 直接枚举京麦的子进程
print("\n=== 京麦子进程 ===")
for line in subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq JM*'], encoding='utf-8', errors='ignore').split('\n'):
    if 'JM' in line:
        print(line)
