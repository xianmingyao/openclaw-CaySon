# -*- coding: utf-8 -*-
"""
京麦商品批量上架脚本
循环上架100个商品，自动记录结果
"""
import subprocess
import time
import json
import os
import sys
from datetime import datetime

LOG_FILE = "E:\\workspace\\scripts\\batch_publish.log"

def log(msg):
    """统一的日志输出到文件"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (timestamp, msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

# 商品数据池
PRODUCTS = [
    ("蓝牙耳机", 199), ("无线蓝牙音箱", 399), ("智能手环", 199), ("移动电源", 129),
    ("数据线", 29), ("手机壳", 49), ("钢化膜", 19), ("充电器", 89),
    ("无线充电器", 159), ("车载支架", 79), ("耳机盒", 59), ("运动耳机", 299),
    ("降噪耳机", 599), ("游戏耳机", 349), ("头戴式耳机", 459), ("音响", 299),
    ("智能手表", 899), ("儿童手表", 399), ("手表表带", 69), ("计步器", 99),
    ("体脂秤", 149), ("血压计", 299), ("体温计", 69), ("血氧仪", 199),
    ("护眼仪", 299), ("按摩仪", 399), ("筋膜枪", 499), ("瑜伽垫", 129),
    ("哑铃", 199), ("跳绳", 69), ("俯卧撑架", 89), ("跑步机", 2999),
    ("电动牙刷", 299), ("冲牙器", 199), ("牙刷头", 49), ("漱口水", 39),
    ("加湿器", 199), ("除湿机", 599), ("空气净化器", 1299), ("电风扇", 299),
    ("电暖器", 399), ("电热毯", 199), ("热水袋", 69), ("保温杯", 99),
    ("电水壶", 149), ("榨汁机", 199), ("料理机", 299), ("豆浆机", 399),
    ("电饭煲", 299), ("电压力锅", 499), ("空气炸锅", 399), ("烤箱", 599),
    ("微波炉", 499), ("电磁炉", 299), ("电陶炉", 399), ("面条机", 299),
    ("面包机", 199), ("咖啡机", 599), ("电蒸锅", 299), ("电火锅", 249),
    ("吸尘器", 899), ("扫地机器人", 1999), ("拖把", 99), ("挂烫机", 299),
    ("电吹风", 199), ("剃须刀", 299), ("理发器", 149), ("美容仪", 599),
    ("蒸脸仪", 299), ("睫毛器", 99), ("指甲刀", 39), ("钥匙扣", 29),
    ("收纳盒", 79), ("化妆包", 69), ("旅行包", 199), ("双肩包", 299),
    ("钱包", 199), ("皮带", 129), ("围巾", 99), ("手套", 49),
    ("帽子", 79), ("雨伞", 89), ("雨衣", 69), ("雨靴", 99),
    ("背包", 299), ("手提包", 399), ("单肩包", 249), ("腰包", 129),
    ("行李箱", 599), ("密码锁", 49), ("转换插头", 39), ("充电宝", 199),
    ("自拍杆", 69), ("三脚架", 199), ("相机包", 299), ("镜头布", 19),
    ("内存卡", 99), ("读卡器", 39), ("数据线", 29), ("扩展坞", 299),
]

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def publish_product(name, price, index):
    """上架单个商品"""
    cmd = [
        sys.executable,
        "E:\\workspace\\skills\\desktop-control-cli\\desktop-control\\cli.py",
        "agents", "publish",
        name,
        "--price", str(price),
        "--category", "数码配件"
    ]
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=180
        )
        elapsed = time.time() - start_time
        
        # 检查是否成功
        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')
        success = "[SUCCESS]" in stdout or "[SUCCESS]" in stderr
        error = None
        if not success:
            for line in stderr.split('\n'):
                if "ERROR" in line or "失败" in line:
                    error = line.strip()
                    break
        
        return {
            "index": index,
            "name": name,
            "price": price,
            "success": success,
            "elapsed": round(elapsed, 1),
            "error": error,
            "time": get_timestamp()
        }
    except subprocess.TimeoutExpired:
        return {
            "index": index,
            "name": name,
            "price": price,
            "success": False,
            "elapsed": 180,
            "error": "超时",
            "time": get_timestamp()
        }
    except Exception as e:
        return {
            "index": index,
            "name": name,
            "price": price,
            "success": False,
            "elapsed": 0,
            "error": str(e),
            "time": get_timestamp()
        }

def main():
    # 清空日志文件
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")
    
    log("=" * 60)
    log("京麦商品批量上架 - 100个商品")
    log("=" * 60)
    
    results = []
    total = min(100, len(PRODUCTS))
    success_count = 0
    fail_count = 0
    
    start_time = time.time()
    
    for i, (name, price) in enumerate(PRODUCTS[:total], 1):
        log("上架第 %d/%d 个商品: %s - %d元" % (i, total, name, price))
        
        result = publish_product(name, price, i)
        results.append(result)
        
        if result["success"]:
            success_count += 1
            log("  -> 成功 (%ds)" % result['elapsed'])
        else:
            fail_count += 1
            log("  -> 失败: %s" % result['error'])
        
        # 间隔2秒
        if i < total:
            time.sleep(2)
    
    total_time = time.time() - start_time
    
    # 生成报告
    report = """
================================================================================
                        京麦商品批量上架报告
================================================================================
执行时间: %s
商品总数: %d
成功上架: %d
上架失败: %d
总耗时: %d分%d秒
成功率: %d%%

--------------------------------------------------------------------------------
详细结果:
--------------------------------------------------------------------------------
""" % (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total, success_count, fail_count,
        int(total_time // 60), int(total_time % 60),
        success_count * 100 // total if total > 0 else 0
    )
    
    for r in results:
        status = "[OK]" if r["success"] else "[FAIL]"
        error_info = " | Error: %s" % r['error'] if r["error"] else ""
        report += "%s #%3d | %-10s | %6.0f Yuan | %s | %ds%s\n" % (
            status, r['index'], r['name'], r['price'], r['time'], r['elapsed'], error_info
        )
    
    report += """
================================================================================
                                                                 完成时间: %s
================================================================================
""" % get_timestamp()
    
    # 保存报告
    report_path = "E:\\workspace\\scripts\\batch_publish_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    log(report)
    log("Report saved: %s" % report_path)
    
    return results

if __name__ == "__main__":
    main()
