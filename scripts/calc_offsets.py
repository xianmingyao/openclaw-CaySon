# -*- coding: utf-8 -*-
"""
图数-初始偏移量计算器
========================

数据点（图数 → 偏移）：
    10 → 635
     9 → 695   (+60)
     8 → 755   (+60)
     7 → 825   (+70)
     6 → 895   (+70)

差值规律：60, 60, 70, 70, 80, 80, 90, 90, 100, 100 ...
公式：step(i) = 60 + (i // 2) * 10    (i 从 0 开始)
        offset(n) = 635 + Σ step(i), i = 0..10-n-1
"""

# 原始数据点（用来验证公式）
KNOWN = {
    10: 635,
     9: 695,
     8: 755,
     7: 825,
     6: 895,
}


def calc_offset(n: int) -> int:
    """根据图数 n 计算初始偏移（内层循环实现累加步长）"""
    offset = 635
    # 内层：累加 0~10-n-1 步的步长
    for i in range(10 - n):
        step = 60 + (i // 2) * 10  # 60, 60, 70, 70, 80, 80, ...
        offset += step
    return offset


def main():
    # 外层：图数从 10 反推到 1
    print("图数-初始偏移对照表（完整内推）")
    print("=" * 30)
    for n in range(10, 0, -1):
        offset = calc_offset(n)
        print(f"  {n:>2} 个图  →  偏移 {offset}")

    # 验证原始数据
    print("\n数据点验证：")
    for n, expected in KNOWN.items():
        actual = calc_offset(n)
        mark = "✅" if actual == expected else "❌"
        print(f"  {n:>2} 个图  期望 {expected:>4}  实际 {actual:>4}  {mark}")


if __name__ == "__main__":
    main()
