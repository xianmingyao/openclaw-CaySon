# -*- coding: utf-8 -*-
"""查找京麦CDP端口"""
import subprocess
import re
import os

# 京麦进程ID
jm_pid = 65988

print(f"查找京麦 (PID: {jm_pid}) 的CDP端口...")

# 方法1: 检查京麦的远程调试端口
# 京麦通常在启动时会打开一个调试端口
# 通过检查 netstat 查找连接到浏览器的端口

try:
    result = subprocess.check_output(
        f'netstat -ano | findstr "{jm_pid}"',
        encoding='utf-8',
        shell=True
    )
    print("=== 网络连接 ===")
    for line in result.split('\n'):
        if 'LISTENING' in line or 'ESTABLISHED' in line:
            print(line)
except:
    pass

# 方法2: 检查环境变量
print("\n=== 检查京麦环境变量 ===")
try:
    from pywinauto.process_info import Process
    import win32process
    
    handle = win32process.OpenProcess(win32process.PROCESS_QUERY_INFORMATION | win32process.PROCESS_VM_READ, False, jm_pid)
    env = win32process.GetEnvironmentVariables(handle)
    
    for key, value in env.items():
        if 'DEBUG' in key.upper() or 'PORT' in key.upper():
            print(f"{key}: {value}")
except Exception as e:
    print(f"获取环境变量失败: {e}")

# 方法3: 尝试常见端口
print("\n=== 尝试常见CDP端口 ===")
import urllib.request
import urllib.error

common_ports = [9222, 9223, 9224, 9225, 9226, 9227, 9228, 9229, 
                9333, 9444, 9555, 9666, 9777, 9888, 9999,
                19222, 19223, 19224, 19225]

for port in common_ports:
    try:
        url = f"http://localhost:{port}/json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Chrome'})
        resp = urllib.request.urlopen(req, timeout=0.5)
        data = resp.read().decode()
        if 'webSocketDebuggerUrl' in data or 'devtoolsFrontendUrl' in data:
            print(f"✅ 找到CDP: localhost:{port}")
            print(data[:200])
            break
        else:
            print(f"端口 {port} 无CDP响应")
    except urllib.error.URLError:
        pass
    except Exception as e:
        pass

print("\n=== 完成 ===")
