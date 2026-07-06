# -*- coding: utf-8 -*-
"""
京麦商品批量上架测试脚本 v2.0
简化版，直接调用 MasterAgent
"""
import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, r"E:\workspace\skills\desktop-control-cli\desktop-control")

LOG_FILE = r"E:\workspace\scripts\batch_publish.log"

def log(msg):
    """统一日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = "[%s] %s" % (timestamp, msg)
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Log error: {e}")

async def publish_single(master, name, price, index):
    """上架单个商品"""
    log(f"开始上架 #{index}: {name} - {price}元")
    start_time = time.time()
    
    try:
        result = await master.publish(
            product_name=name,
            context="jingmai"
        )
        elapsed = time.time() - start_time
        
        success = result.get("success", False)
        error = None if success else result.get("summary", {}).get("error", "未知错误")
        
        return {
            "index": index,
            "name": name,
            "price": price,
            "success": success,
            "elapsed": round(elapsed, 1),
            "error": error,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        elapsed = time.time() - start_time
        log(f"  异常: {e}")
        import traceback
        traceback.print_exc()
        return {
            "index": index,
            "name": name,
            "price": price,
            "success": False,
            "elapsed": round(elapsed, 1),
            "error": str(e),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

async def main():
    # 清空日志
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")
    
    log("=" * 60)
    log("京麦商品批量上架测试 v2.0")
    log("=" * 60)
    
    # 测试商品列表（先测3个）
    test_products = [
        ("蓝牙耳机", 199),
        ("无线蓝牙音箱", 399),
        ("智能手环", 199),
    ]
    
    # 导入 MasterAgent
    try:
        from app.agents.master_agent import MasterAgent
        log("MasterAgent 导入成功")
    except Exception as e:
        log(f"MasterAgent 导入失败: {e}")
        return []
    
    # 创建 MasterAgent
    master = MasterAgent()
    log("MasterAgent 初始化成功")
    
    results = []
    success_count = 0
    fail_count = 0
    
    start_time = time.time()
    
    for i, (name, price) in enumerate(test_products, 1):
        log("-" * 40)
        result = await publish_single(master, name, price, i)
        results.append(result)
        
        if result["success"]:
            success_count += 1
            log(f"  -> 成功 ({result['elapsed']}s)")
        else:
            fail_count += 1
            log(f"  -> 失败: {result['error']}")
        
        # 间隔3秒
        if i < len(test_products):
            time.sleep(3)
    
    total_time = time.time() - start_time
    
    # 清理
    await master.close()
    
    # 生成报告
    report = f"""
================================================================================
                        京麦商品批量上架报告 v2.0
================================================================================
执行时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
商品总数: {len(test_products)}
成功上架: {success_count}
上架失败: {fail_count}
总耗时: {int(total_time // 60)}分{int(total_time % 60)}秒
成功率: {success_count * 100 // len(test_products) if test_products else 0}%

--------------------------------------------------------------------------------
详细结果:
--------------------------------------------------------------------------------
"""
    
    for r in results:
        status = "[OK]" if r["success"] else "[FAIL]"
        error_info = f" | Error: {r['error']}" if r["error"] else ""
        report += f"{status} #{r['index']:3d} | {r['name']:<10s} | {r['price']:6.0f} Yuan | {r['time']} | {r['elapsed']}s{error_info}\n"
    
    report += f"""
================================================================================
                                                                 完成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================================================
"""
    
    # 保存报告
    report_path = r"E:\workspace\scripts\batch_publish_report_v2.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    log(report)
    log(f"报告已保存: {report_path}")
    
    return results

if __name__ == "__main__":
    results = asyncio.run(main())
