# -*- coding: utf-8 -*-
"""
京麦商品发布自动化 - 主脚本
使用UFO框架方式：JingmaiLocator + JingmaiMonitor
"""
import sys
import time
from pathlib import Path

# 添加脚本目录
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from jingmai_logger import init_logger, get_logger
from jingmai_locator import JingmaiLocator
from jingmai_monitor import JingmaiMonitor

def main():
    # 初始化
    log = init_logger("jingmai_publish")
    log.header("京麦商品发布自动化 v2.0 (UFO框架)")
    
    # 1. 查找窗口
    log.step("[Step 1] 查找京麦窗口")
    locator = JingmaiLocator(log)
    window = locator.find_window()
    
    if not window:
        log.error("未找到京麦窗口!")
        return False
    
    log.ok(f"找到窗口: {window.title}")
    
    # 2. 激活窗口
    log.step("[Step 2] 激活窗口")
    locator.activate_window()
    time.sleep(1)
    
    # 3. 导航到发布页面
    log.step("[Step 3] 导航到发布商品页面")
    locator.navigate_to_publish()
    time.sleep(2)
    
    # 4. 填写商品信息
    log.step("[Step 4] 填写商品信息")
    
    # 商品标题
    log.sub("填写商品标题")
    title_input = locator.find_element_by_name("商品标题")
    if title_input:
        title_input.set_edit_text("公牛BULL插座B5系列8位总控5米新国标防过载商业专用B5440")
        log.ok("商品标题已填写")
    
    # 品牌
    log.sub("选择品牌")
    brand_combo = locator.find_element_by_name("品牌")
    if brand_combo:
        brand_combo.select("公牛 (BULL)")
        log.ok("品牌已选择")
    
    time.sleep(1)
    
    # 5. 监听并重试
    log.step("[Step 5] 监听页面状态")
    monitor = JingmaiMonitor(locator, log)
    
    # 检查必填项进度
    result = monitor.wait_for_condition(
        check_func=lambda: locator.check_required_fields(),
        timeout=60,
        description="必填项检查"
    )
    
    if result.success:
        log.ok("必填项已填写完成!")
    else:
        log.warn(f"部分必填项未完成: {result.message}")
    
    # 6. 保存草稿
    log.step("[Step 6] 保存草稿")
    save_btn = locator.find_element_by_name("保存草稿")
    if save_btn:
        save_btn.click()
        log.ok("草稿已保存")
    
    log.header("自动化完成!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
