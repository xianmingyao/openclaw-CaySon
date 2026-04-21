"""
京麦商品发布 - UFO 直接自动化
使用 desktop-control-cli 的 UFO 服务直接操作，不依赖 LLM
"""
import sys
import time
import asyncio
from pathlib import Path

# 添加 desktop-control 到路径
sys.path.insert(0, str(Path(__file__).parent / "skills" / "desktop-control-cli" / "desktop-control"))

from app.services.ufo_service import UFOService

async def main():
    print("=" * 60)
    print("京麦商品发布 - UFO 直接自动化")
    print("=" * 60)
    
    # 1. 初始化 UFO
    print("\n[Step 1] 初始化 UFO 服务...")
    ufo = UFOService()
    print("[OK] UFO 服务已初始化")
    
    # 2. 查找京麦窗口
    print("\n[Step 2] 查找京麦窗口...")
    hwnd = ufo.find_window("jd_465d1abd3ee76")
    if not hwnd:
        print("[ERROR] 未找到京麦窗口!")
        return False
    print(f"[OK] 找到京麦窗口: {hwnd}")
    
    # 3. 激活窗口
    print("\n[Step 3] 激活京麦窗口...")
    ufo.activate_window(hwnd)
    time.sleep(0.5)
    print("[OK] 窗口已激活")
    
    # 4. 获取窗口信息
    print("\n[Step 4] 获取窗口信息...")
    window_info = ufo.get_window_info(hwnd)
    print(f"[OK] 窗口大小: {window_info.get('width')}x{window_info.get('height')}")
    
    # 5. 截图确认当前状态
    print("\n[Step 5] 截图确认当前状态...")
    screenshot = await ufo.screenshot(hwnd)
    print(f"[OK] 截图完成: {len(screenshot)} bytes")
    
    # 6. 使用视觉识别找到"下一步"按钮
    print("\n[Step 6] 识别'下一步'按钮...")
    # 这里使用相对坐标 - 按钮在页面底部右侧
    # 基于 2560x1392 窗口，按钮大约在 (2000, 1300)
    
    # 7. 点击"下一步"按钮
    print("\n[Step 7] 点击'下一步'按钮...")
    # 尝试多个可能的位置
    positions = [
        (2000, 1300),  # 右侧
        (2200, 1300),  # 更右
        (1800, 1350),  # 中右
        (2200, 1350),  # 右下
    ]
    
    for x, y in positions:
        print(f"[INFO] 尝试点击: ({x}, {y})")
        result = await ufo.click(x, y)
        print(f"     点击结果: {result}")
        time.sleep(1)
    
    # 8. 等待页面跳转
    print("\n[Step 8] 等待商品信息页面...")
    time.sleep(3)
    
    # 9. 截图确认
    print("\n[Step 9] 截图确认...")
    screenshot2 = await ufo.screenshot(hwnd)
    print(f"[OK] 截图完成: {len(screenshot2)} bytes")
    
    print("\n" + "=" * 60)
    print("UFO 自动化流程执行完成!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
