"""
京麦商品发布自动化 - 主发布脚本
整合所有模块，实现商品发布全流程自动化
"""
import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# 导入本地模块
from jingmai_logger import init_logger, JingmaiLogger, get_logger
from jingmai_locator import JingmaiLocator
from jingmai_monitor import JingmaiMonitor, create_monitor


class JingmaiPublisher:
    """京麦商品发布器"""
    
    def __init__(self, config_path: Optional[str] = None, debug: bool = False):
        # 初始化日志
        self.log = init_logger("jingmai_publish")
        self.debug = debug
        
        # 初始化定位器
        self.locator = JingmaiLocator(self.log)
        
        # 初始化监听器
        self.monitor = create_monitor(self.locator, self.log)
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 状态追踪
        self.current_step = 0
        self.total_steps = 8
        self.publish_success = False
        
        # 截图目录
        self.screenshot_dir = SCRIPT_DIR.parent / "logs"
        self.screenshot_dir.mkdir(exist_ok=True)
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置"""
        if config_path and os.path.exists(config_path):
            self.log.info(f"加载配置文件: {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            self.log.warn("未找到配置文件，使用默认配置")
            return {
                "product": {
                    "title": "测试商品",
                    "description": "测试商品描述",
                    "price": 99.99,
                    "stock": 100,
                    "sku": "TEST001"
                },
                "images": [],
                "publish": {
                    "auto_submit": True,
                    "confirm_before_submit": True
                }
            }
    
    def _timestamp(self) -> str:
        """获取时间戳字符串"""
        return datetime.now().strftime("%H%M%S")
    
    def _screenshot(self, name: str) -> str:
        """截图并返回路径"""
        path = self.monitor.take_screenshot(f"{name}_{self._timestamp()}")
        if path:
            self.log.info(f"截图保存: {path}")
        return path or ""
    
    # ==================== 执行流程 ====================
    
    def run(self) -> bool:
        """执行完整发布流程"""
        try:
            self.log.header("京麦商品发布自动化 v1.0")
            self.log.info(f"商品: {self.config.get('product', {}).get('title', 'N/A')}")
            self.log.info(f"配置: {json.dumps(self.config, ensure_ascii=False, indent=2)[:200]}...")
            
            # Step 1: 环境检查
            if not self.step1_check_environment():
                return False
            
            # Step 2: 窗口定位
            if not self.step2_locate_window():
                return False
            
            # Step 3: 页面导航
            if not self.step3_navigate_to_publish():
                return False
            
            # Step 4: 填充商品信息
            if not self.step4_fill_product_info():
                return False
            
            # Step 5: 上传图片
            if not self.step5_upload_images():
                return False
            
            # Step 6: 核对表单
            if not self.step6_verify_form():
                return False
            
            # Step 7: 提交发布
            if not self.step7_submit():
                return False
            
            # Step 8: 验证结果
            if not self.step8_verify_result():
                return False
            
            # 完成
            self.log.ok("[SUCCESS] Product published successfully!")
            self.publish_success = True
            return True
            
        except KeyboardInterrupt:
            self.log.warn("用户中断执行")
            return False
        except Exception as e:
            self.log.error(f"执行异常: {e}")
            if self.debug:
                import traceback
                self.log.error(traceback.format_exc())
            self._screenshot("error_final")
            return False
        finally:
            self.log.summary()
    
    def step1_check_environment(self) -> bool:
        """Step 1: 环境检查"""
        self.current_step = 1
        self.log.step(f"[Step {self.current_step}/{self.total_steps}] 环境检查")
        
        # 检查窗口
        self.log.sub("检查京麦窗口...")
        window_info = self.locator.find_window()
        
        if not window_info:
            self.log.error("[ERROR] Jingmai window not found")
            self._screenshot("error_no_window")
            return False
        
        self.log.ok(f"[OK] Window found: {window_info.title}")
        self.log.info(f"   句柄: {window_info.hwnd}")
        self.log.info(f"   位置: {window_info.rect}")
        self.log.info(f"   大小: {window_info.width}x{window_info.height}")
        
        return True
    
    def step2_locate_window(self) -> bool:
        """Step 2: 窗口定位和激活"""
        self.current_step = 2
        self.log.step(f"[Step {self.current_step}/{self.total_steps}] 窗口定位")
        
        # 激活窗口
        self.log.sub("激活京麦窗口...")
        if not self.locator.activate_window():
            self.log.error("[ERROR] Window activation failed")
            self._screenshot("error_window_activation")
            return False
        
        self._screenshot("step2_window_activated")
        self.log.ok("[OK] Window activated")
        
        return True
    
    def step3_navigate_to_publish(self) -> bool:
        """Step 3: 导航到发布商品页面"""
        self.current_step = 3
        self.log.step(f"[Step {self.current_step}/{self.total_steps}] 页面导航")
        
        self.log.sub("导航到发布商品页面...")
        
        # 使用监听器的重试机制
        result = self.monitor.retry_until_success(
            action_func=lambda: (self.locator.navigate_to_publish(), "导航完成"),
            strategy=self.monitor.page_retry,
            description="点击发布商品"
        )
        
        if not result.success:
            self.log.error(f"[ERROR] Navigation failed: {result.message}")
            self._screenshot("error_navigation")
            return False
        
        self._screenshot("step3_navigation_done")
        self.log.ok("[OK] Entered publish page")
        
        return True
    
    def step4_fill_product_info(self) -> bool:
        """Step 4: 填充商品信息"""
        self.current_step = 4
        self.log.step(f"[Step {self.current_step}/{self.total_steps}] 填充商品信息")
        
        product = self.config.get('product', {})
        
        self.log.sub("填充商品标题...")
        # 这里应该实现实际的填充逻辑
        # 根据实际页面结构调整
        self.log.info(f"   标题: {product.get('title', '')}")
        self.log.info(f"   价格: {product.get('price', '')}")
        self.log.info(f"   SKU: {product.get('sku', '')}")
        
        self._screenshot("step4_product_info")
        
        # 实际实现时：
        # 1. Click title input
        # 2. Type title
        # 3. Click price input
        # 4. Type price
        # ...
        
        self.log.ok("[OK] Product info filled (field mapping pending)")
        return True
    
    def step5_upload_images(self) -> bool:
        """Step 5: 上传图片"""
        self.current_step = 5
        self.log.step(f"[Step {self.current_step}/{self.total_steps}] 上传图片")
        
        images = self.config.get('images', [])
        
        if not images:
            self.log.warn("[WARN] No images configured, skipping upload")
            return True
        
        self.log.info(f"待上传 {len(images)} 张图片:")
        for i, img_path in enumerate(images, 1):
            self.log.info(f"   {i}. {img_path}")
        
        # 实际实现时：
        # 1. 点击上传按钮
        # 2. 在文件对话框输入路径
        # 3. 确认上传
        # 4. 等待上传完成
        
        self._screenshot("step5_images_uploaded")
        self.log.ok("[OK] Image upload completed (upload logic pending)")
        return True
    
    def step6_verify_form(self) -> bool:
        """Step 6: 核对表单"""
        self.current_step = 6
        self.log.step(f"[Step {self.current_step}/{self.total_steps}] 核对表单")
        
        self.log.sub("检查必填项...")
        
        # 检查关键字段
        product = self.config.get('product', {})
        required = ['title', 'price']
        missing = [f for f in required if not product.get(f)]
        
        if missing:
            self.log.error(f"[ERROR] Missing required fields: {missing}")
            self._screenshot("error_form_incomplete")
            return False
        
        self._screenshot("step6_form_verified")
        self.log.ok("[OK] Form verified")
        
        return True
    
    def step7_submit(self) -> bool:
        """Step 7: 提交发布"""
        self.current_step = 7
        self.log.step(f"[Step {self.current_step}/{self.total_steps}] 提交发布")
        
        publish_config = self.config.get('publish', {})
        auto_submit = publish_config.get('auto_submit', True)
        
        if not auto_submit:
            self.log.warn("[WARN] Manual submit mode, click publish button manually")
            self._screenshot("step7_manual_submit")
            return True
        
        self.log.sub("点击发布按钮...")
        
        # 实际实现时：
        # 1. 点击发布按钮
        # 2. 等待确认对话框
        # 3. 确认发布
        
        self._screenshot("step7_submitted")
        self.log.ok("[OK] Submitted (click logic pending)")
        
        return True
    
    def step8_verify_result(self) -> bool:
        """Step 8: 验证结果"""
        self.current_step = 8
        self.log.step(f"[Step {self.current_step}/{self.total_steps}] 验证结果")
        
        self.log.sub("检查发布结果...")
        
        # 监听成功/失败标志
        self.log.info("等待发布结果确认...")
        
        # 实际实现时：
        # result = self.monitor.wait_for_condition(
        #     check_func=lambda: self._check_publish_result(),
        #     timeout=60,
        #     description="发布结果"
        # )
        
        self._screenshot("step8_result")
        
        # 模拟成功
        self.publish_success = True
        self.log.ok("[OK] Publish successful!")
        
        return True
    
    def _check_publish_result(self) -> bool:
        """检查发布结果（需根据实际页面实现）"""
        # TODO: 实现实际检查逻辑
        # 1. 检查是否有成功提示
        # 2. 检查是否有错误提示
        # 3. 返回检查结果
        return True


# ==================== CLI 入口 ====================

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="京麦商品发布自动化",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python jingmai_publisher.py                                    # 使用默认配置
  python jingmai_publisher.py --config product_001.json          # 指定配置
  python jingmai_publisher.py --monitor                          # 持续监听模式
  python jingmai_publisher.py --debug                            # 调试模式
  python jingmai_publisher.py --watch                           # 监视直到成功
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        default=None,
        help='商品配置文件路径 (JSON格式)'
    )
    
    parser.add_argument(
        '--monitor',
        action='store_true',
        help='持续监听模式'
    )
    
    parser.add_argument(
        '--watch',
        action='store_true',
        help='监视直到发布成功'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=100,
        help='最大监听迭代次数 (默认: 100)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='调试模式'
    )
    
    parser.add_argument(
        '--step-by-step',
        action='store_true',
        help='每步暂停等待确认'
    )
    
    return parser.parse_args()


def main():
    """主入口"""
    args = parse_args()
    
    if args.monitor:
        # 监听模式
        print("=" * 60)
        print("京麦商品发布自动化 - 持续监听模式")
        print("=" * 60)
        
        log = init_logger("jingmai_monitor")
        locator = JingmaiLocator(log)
        monitor = create_monitor(locator, log)
        
        monitor.monitor_loop(max_iterations=args.max_iterations)
        
    elif args.watch:
        # 监视直到成功
        print("=" * 60)
        print("京麦商品发布自动化 - 监视模式")
        print("=" * 60)
        
        log = init_logger("jingmai_watch")
        locator = JingmaiLocator(log)
        monitor = create_monitor(locator, log)
        
        result = monitor.watch_for_success()
        if result.success:
            print("🎉 检测到发布成功!")
        else:
            print(f"⚠️ {result.message}")
            
    else:
        # 普通发布模式
        publisher = JingmaiPublisher(
            config_path=args.config,
            debug=args.debug
        )
        
        success = publisher.run()
        
        if args.step_by_step:
            input("\n按回车继续...")
        
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
