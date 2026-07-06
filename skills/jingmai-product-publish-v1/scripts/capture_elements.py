"""
京麦页面截图 + 元素坐标获取
"""
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-product-publish\scripts')

from jingmai_logger import init_logger
from jingmai_locator import JingmaiLocator
import time

log = init_logger("capture")
locator = JingmaiLocator(log)

log.header("京麦页面元素抓取")

# 1. 找窗口
window = locator.find_window()
if not window:
    log.error("Window not found")
    sys.exit(1)

log.ok(f"Window: {window.title}")
log.info(f"Position: {window.rect}")
log.info(f"Size: {window.width}x{window.height}")

# 2. 激活窗口
locator.activate_window()
time.sleep(0.5)

# 3. 截图
screenshot = locator.take_screenshot()
if screenshot:
    log.ok(f"Screenshot: {screenshot}")

log.info("")
log.info("=" * 50)
log.info("请告诉宁兄在页面上指认以下元素位置：")
log.info("=" * 50)
log.info("1. 类目选择器（点击位置）")
log.info("2. 已选类目显示")
log.info("3. 下一步按钮")
log.info("4. 其他关键元素")
log.info("")
log.info("我会根据他描述的位置记录坐标")
