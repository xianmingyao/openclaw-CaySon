"""
京麦商品发布自动化 - CLI 入口
统一命令行接口
"""
import argparse
import json
import sys
from pathlib import Path


def cmd_publish(args):
    """发布商品"""
    from agents.factory import AgentFactory

    factory = AgentFactory()
    planner = factory.create_planner()

    # 加载商品数据
    if args.file:
        product_data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    elif args.data:
        product_data = json.loads(args.data)
    else:
        print("错误: 需要 --file 或 --data 提供商品数据")
        sys.exit(1)

    # 规划
    plan_result = planner.run(product_data=product_data)
    if not plan_result.get("success"):
        print(f"规划失败: {plan_result.get('error')}")
        sys.exit(1)

    print(f"规划完成: {plan_result['total_steps']} 步")

    # 执行
    executor = factory.create_executor()
    result = executor.run(plan=plan_result["plan"], task_id=plan_result["task_id"])

    if result["success"]:
        print(f"发布成功!")
    else:
        print(f"发布失败: {result.get('error')}")
        sys.exit(1)


def cmd_plan(args):
    """仅规划，不执行"""
    from agents.factory import AgentFactory

    factory = AgentFactory()
    planner = factory.create_planner()

    if args.file:
        product_data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    elif args.data:
        product_data = json.loads(args.data)
    else:
        print("错误: 需要 --file 或 --data")
        sys.exit(1)

    result = planner.run(product_data=product_data)
    if result.get("success"):
        print(json.dumps(result["plan"], ensure_ascii=False, indent=2))
    else:
        print(f"规划失败: {result.get('error')}")
        sys.exit(1)


def cmd_think(args):
    """LLM 思考/分析"""
    from agents.factory import AgentFactory

    factory = AgentFactory()
    thinker = factory.create_thinker()

    result = thinker.run(question=args.question, screenshot_path=args.screenshot or "")
    if result.get("success"):
        print(result["response"])
    else:
        print(f"思考失败: {result.get('error')}")
        sys.exit(1)


def cmd_actions(args):
    """列出所有已注册动作"""
    from actions import ActionRegistry
    print(ActionRegistry.summary())


def cmd_db_init(args):
    """初始化数据库"""
    from init_db import init_db
    db = init_db()
    print(f"数据库初始化完成: {db.db_type}")


def cmd_memory_cleanup(args):
    """清理过期记忆"""
    from memory.manager import MemoryManager
    memory = MemoryManager()
    stats = memory.cleanup()
    print(f"清理完成: {stats}")


def main():
    parser = argparse.ArgumentParser(
        description="京麦商品发布自动化 v2.0",
        prog="jingmai",
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    # publish
    p = sub.add_parser("publish", help="发布商品")
    p.add_argument("--file", "-f", help="商品数据 JSON 文件路径")
    p.add_argument("--data", "-d", help="商品数据 JSON 字符串")
    p.set_defaults(func=cmd_publish)

    # plan
    p = sub.add_parser("plan", help="仅生成执行计划")
    p.add_argument("--file", "-f", help="商品数据 JSON 文件路径")
    p.add_argument("--data", "-d", help="商品数据 JSON 字符串")
    p.set_defaults(func=cmd_plan)

    # think
    p = sub.add_parser("think", help="LLM 思考分析")
    p.add_argument("--question", "-q", required=True, help="问题")
    p.add_argument("--screenshot", "-s", default="", help="截图路径")
    p.set_defaults(func=cmd_think)

    # actions
    p = sub.add_parser("actions", help="列出已注册动作")
    p.set_defaults(func=cmd_actions)

    # db init
    p = sub.add_parser("db-init", help="初始化数据库")
    p.set_defaults(func=cmd_db_init)

    # memory cleanup
    p = sub.add_parser("memory-cleanup", help="清理过期记忆")
    p.set_defaults(func=cmd_memory_cleanup)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
