#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jingmai Agent CLI
Windows 桌面自动化 Agent 命令行工具

用法:
    python jingmai_cli.py run "任务描述"
    python jingmai_cli.py interactive
    python jingmai_cli.py batch tasks.txt
    python jingmai_cli.py memory create "记忆内容"
    python jingmai_cli.py memory search "关键词"
    python jingmai_cli.py rag query "查询问题"
    python jingmai_cli.py status
"""

import asyncio
import sys
import os
from pathlib import Path

# 修复 Windows 终端编码
if sys.platform == 'win32':
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


class JingmaiCLI:
    """Jingmai Agent CLI 主类"""

    VERSION = "v1.0.0"

    def __init__(self):
        self.services_initialized = False

    async def initialize_services(self):
        """初始化所有服务"""
        print("[*] 初始化服务...")
        # 实际项目中这里会初始化 LLMManager, AgentFactory, MemoryManager 等
        self.services_initialized = True
        print("[✓] 服务初始化完成")

    def print_help(self):
        """打印帮助信息"""
        help_text = f"""
Jingmai Agent CLI {self.VERSION}
Windows 桌面自动化 Agent 命令行工具

用法:
    jingmai run <任务描述>          运行单个任务
    jingmai interactive             交互式模式
    jingmai batch <文件>            批量执行任务
    jingmai memory create <内容>    创建记忆
    jingmai memory search <关键词>  搜索记忆
    jingmai memory stats            记忆统计
    jingmai memory clear            清空记忆
    jingmai rag query <问题>        RAG 查询
    jingmai rag stats               RAG 统计
    jingmai skills list             列出技能
    jingmai skills search <关键词>  搜索技能
    jingmai status                  系统状态
    jingmai --help                  显示帮助

选项:
    -t, --title       任务标题
    -c, --complexity  复杂度 (simple/medium/complex)
    -p, --priority    优先级 (1-10)
    -a, --agent       Agent 类型 (ufo_agent/rag_agent/planner_agent)
    -s, --max-steps   最大执行步数
    -v, --verbose     详细输出
    -j, --json        JSON 格式输出

示例:
    jingmai run "打开记事本"
    jingmai run "整理桌面" -t "文件整理" -c simple
    jingmai interactive
    jingmai batch tasks.txt
    jingmai memory create "用户偏好深色模式" -t long -p high
    jingmai memory search "偏好"
    jingmai rag query "如何配置系统"
    jingmai status -v
"""
        print(help_text)

    async def cmd_run(self, description: str, **kwargs):
        """运行单个任务"""
        if not self.services_initialized:
            await self.initialize_services()

        title = kwargs.get('title') or description[:50]
        complexity = kwargs.get('complexity', 'medium')
        priority = kwargs.get('priority', 5)
        agent = kwargs.get('agent', 'ufo_agent')
        max_steps = kwargs.get('max_steps', 10)

        print(f"[*] 创建任务: {title}")
        print(f"[*] 描述: {description}")
        print(f"[*] Agent: {agent}, 复杂度: {complexity}, 优先级: {priority}")

        # 模拟任务执行
        print(f"[*] 执行任务 (最大步数: {max_steps})...")

        # 实际项目中这里会调用 AgentFactory 创建 Agent 并执行
        for step in range(1, max_steps + 1):
            await asyncio.sleep(0.1)
            print(f"    Step {step}/{max_steps}: 执行中...")

        print(f"[✓] 任务完成!")
        print(f"    结果: 任务已成功执行")

    async def cmd_interactive(self, **kwargs):
        """交互式模式"""
        if not self.services_initialized:
            await self.initialize_services()

        agent = kwargs.get('agent', 'ufo_agent')
        print(f"[*] 进入交互式模式 (Agent: {agent})")
        print("[*] 输入 'exit' 或 'quit' 退出")
        print("-" * 50)

        while True:
            try:
                description = input("\n→ 任务: ").strip()

                if description.lower() in ['exit', 'quit', 'q']:
                    print("[*] 再见!")
                    break

                if not description:
                    continue

                await self.cmd_run(description, **kwargs)
                print()

            except (EOFError, KeyboardInterrupt):
                print("\n[*] 再见!")
                break

    async def cmd_batch(self, file_path: str = None, **kwargs):
        """批量执行任务"""
        if not self.services_initialized:
            await self.initialize_services()

        tasks = []

        # 读取任务文件
        if file_path:
            path = Path(file_path)
            if path.exists():
                content = path.read_text(encoding='utf-8')
                if path.suffix == '.json':
                    import json
                    tasks = json.loads(content)
                else:
                    tasks = [line.strip() for line in content.split('\n') if line.strip()]
            else:
                print(f"[✗] 文件不存在: {file_path}")
                return
        else:
            print("[*] 从标准输入读取任务 (Ctrl+D 结束):")
            tasks = [line.strip() for line in sys.stdin if line.strip()]

        total = len(tasks)
        print(f"[*] 共 {total} 个任务")

        completed = 0
        failed = 0

        for i, task in enumerate(tasks, 1):
            try:
                if isinstance(task, dict):
                    desc = task.get('description', '')
                else:
                    desc = str(task)

                print(f"\n[{i}/{total}] 执行: {desc[:50]}...")
                await self.cmd_run(desc, **kwargs)
                completed += 1
                print(f"[✓] 成功")

            except Exception as e:
                failed += 1
                print(f"[✗] 失败: {str(e)}")

        print(f"\n[*] 执行完成: 成功 {completed}, 失败 {failed}")

    async def cmd_memory(self, action: str, content: str = None, **kwargs):
        """记忆管理"""
        if not self.services_initialized:
            await self.initialize_services()

        if action == 'create' and content:
            memory_type = kwargs.get('type', 'short')
            key = kwargs.get('key')
            priority = kwargs.get('priority', 'medium')
            tags = kwargs.get('tags', [])
            ttl = kwargs.get('ttl')

            print(f"[*] 创建记忆...")
            print(f"    类型: {memory_type}")
            print(f"    内容: {content}")
            print(f"[✓] 记忆创建成功 (ID: mem_001)")

        elif action == 'search' and content:
            top_k = kwargs.get('top_k', 5)
            memory_type = kwargs.get('type')

            print(f"[*] 搜索记忆: {content}")
            print(f"    类型: {memory_type or '全部'}")
            print(f"    Top-K: {top_k}")
            # 模拟搜索结果
            print(f"\n[✓] 找到 2 条结果:")
            print(f"    1. mem_001 (short) - 用户偏好设置... [score: 0.95]")
            print(f"    2. mem_002 (long) - 系统配置信息... [score: 0.87]")

        elif action == 'stats':
            print("[*] 记忆统计:")
            print(f"    短期记忆: 10 条")
            print(f"    长期记忆: 5 条")
            print(f"    工作记忆: 3 条")
            print(f"    总计: 18 条")

        elif action == 'clear':
            confirm = input("确定要清空所有记忆? (y/N): ")
            if confirm.lower() == 'y':
                print("[✓] 记忆已清空")
            else:
                print("[*] 取消清空")

    async def cmd_rag(self, action: str, query: str = None, **kwargs):
        """RAG 查询"""
        if not self.services_initialized:
            await self.initialize_services()

        if action == 'query' and query:
            top_k = kwargs.get('top_k', 5)
            rerank = kwargs.get('rerank', False)

            print(f"[*] RAG 查询: {query}")
            print(f"    Top-K: {top_k}, Rerank: {rerank}")
            print(f"\n[✓] 查询结果:")
            print(f"    根据知识库，系统配置说明如下...")
            print(f"    来源: doc_001.md [score: 0.92]")

        elif action == 'stats':
            print("[*] RAG 统计:")
            print(f"    向量总数: 1,234")
            print(f"    文档总数: 56")
            print(f"    集合: jingmai_knowledge")

    async def cmd_skills(self, action: str, query: str = None, **kwargs):
        """技能管理"""
        if not self.services_initialized:
            await self.initialize_services()

        if action == 'list':
            category = kwargs.get('category')
            verbose = kwargs.get('verbose', False)

            print("[*] 技能列表:")
            if verbose:
                print(f"    1. ufo_actions (v2.0.0) [automation]")
                print(f"       Windows UI 自动化操作技能")
                print(f"       操作: click, type, scroll, drag, open_app...")
                print(f"    2. memory_manager (v1.0.0) [system]")
                print(f"       记忆管理技能")
                print(f"       操作: create, search, stats, clear")
            else:
                print(f"    1. ufo_actions (automation)")
                print(f"    2. memory_manager (system)")
                print(f"    3. rag_service (knowledge)")
                print(f"    总计: 3 个技能")

        elif action == 'search' and query:
            top_k = kwargs.get('top_k', 5)

            print(f"[*] 搜索技能: {query}")
            print(f"\n[✓] 找到 1 条结果:")
            print(f"    ufo_actions (v2.0.0) [automation]")
            print(f"    Windows UI 自动化操作技能")

    async def cmd_status(self, **kwargs):
        """系统状态"""
        verbose = kwargs.get('verbose', False)
        json_output = kwargs.get('json', False)

        if json_output:
            import json
            status = {
                "timestamp": "2026-04-08T14:58:00",
                "version": self.VERSION,
                "services": {
                    "llm_manager": True,
                    "agent_factory": True,
                    "memory_manager": True,
                    "rag_service": True,
                    "skill_registry": True
                },
                "stats": {
                    "memory": {"total": 18},
                    "skills": {"total": 3},
                    "rag": {"vectors": 1234, "documents": 56}
                }
            }
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print(f"Jingmai Agent CLI {self.VERSION}")
            print("=" * 50)
            print("[*] 服务状态:")
            print(f"    LLM Manager:     ✓ 已连接")
            print(f"    Agent Factory:   ✓ 就绪")
            print(f"    Memory Manager:  ✓ 已连接")
            print(f"    RAG Service:     ✓ 已连接")
            print(f"    Skill Registry: ✓ 已加载")
            print()
            print("[*] 统计:")
            print(f"    记忆: 18 条")
            print(f"    技能: 3 个")
            print(f"    RAG 向量: 1,234")


async def main():
    """主入口"""
    cli = JingmaiCLI()

    args = sys.argv[1:]

    if not args or '--help' in args or '-h' in args:
        cli.print_help()
        return

    if '--version' in args or '-v' in args:
        print(f"Jingmai Agent CLI {cli.VERSION}")
        return

    command = args[0] if args else 'help'

    # 解析命令和参数
    if command == 'run':
        # jingmai run "任务描述" [-t title] [-c complexity] [-p priority] [-a agent] [-s max_steps]
        desc = ' '.join([a for a in args[1:] if not a.startswith('-')])
        kwargs = {}

        if '-t' in args or '--title' in args:
            idx = args.index('-t') if '-t' in args else args.index('--title')
            kwargs['title'] = args[idx + 1] if idx + 1 < len(args) else None

        if '-c' in args or '--complexity' in args:
            idx = args.index('-c') if '-c' in args else args.index('--complexity')
            kwargs['complexity'] = args[idx + 1] if idx + 1 < len(args) else 'medium'

        if '-p' in args or '--priority' in args:
            idx = args.index('-p') if '-p' in args else args.index('--priority')
            kwargs['priority'] = int(args[idx + 1]) if idx + 1 < len(args) else 5

        if '-a' in args or '--agent' in args:
            idx = args.index('-a') if '-a' in args else args.index('--agent')
            kwargs['agent'] = args[idx + 1] if idx + 1 < len(args) else 'ufo_agent'

        if '-s' in args or '--max-steps' in args:
            idx = args.index('-s') if '-s' in args else args.index('--max-steps')
            kwargs['max_steps'] = int(args[idx + 1]) if idx + 1 < len(args) else 10

        await cli.cmd_run(desc, **kwargs)

    elif command == 'interactive':
        kwargs = {}
        if '-a' in args or '--agent' in args:
            idx = args.index('-a') if '-a' in args else args.index('--agent')
            kwargs['agent'] = args[idx + 1] if idx + 1 < len(args) else 'ufo_agent'
        await cli.cmd_interactive(**kwargs)

    elif command == 'batch':
        file_path = args[1] if len(args) > 1 and not args[1].startswith('-') else None
        await cli.cmd_batch(file_path)

    elif command == 'memory':
        if len(args) < 2:
            print("[✗] 请指定记忆操作: create/search/stats/clear")
            return
        action = args[1]
        content = args[2] if len(args) > 2 else None
        kwargs = {}

        if '-t' in args or '--type' in args:
            idx = args.index('-t') if '-t' in args else args.index('--type')
            kwargs['type'] = args[idx + 1] if idx + 1 < len(args) else 'short'

        if '-k' in args or '--key' in args:
            idx = args.index('-k') if '-k' in args else args.index('--key')
            kwargs['key'] = args[idx + 1] if idx + 1 < len(args) else None

        if '-p' in args or '--priority' in args:
            idx = args.index('-p') if '-p' in args else args.index('--priority')
            kwargs['priority'] = args[idx + 1] if idx + 1 < len(args) else 'medium'

        if '--top-k' in args:
            idx = args.index('--top-k')
            kwargs['top_k'] = int(args[idx + 1]) if idx + 1 < len(args) else 5

        await cli.cmd_memory(action, content, **kwargs)

    elif command == 'rag':
        if len(args) < 2:
            print("[✗] 请指定 RAG 操作: query/stats")
            return
        action = args[1]
        query = args[2] if len(args) > 2 else None
        kwargs = {}

        if '--top-k' in args:
            idx = args.index('--top-k')
            kwargs['top_k'] = int(args[idx + 1]) if idx + 1 < len(args) else 5

        if '-r' in args or '--rerank' in args:
            kwargs['rerank'] = True

        await cli.cmd_rag(action, query, **kwargs)

    elif command == 'skills':
        if len(args) < 2:
            print("[✗] 请指定技能操作: list/search")
            return
        action = args[1]
        query = args[2] if len(args) > 2 else None
        kwargs = {}

        if '-c' in args or '--category' in args:
            idx = args.index('-c') if '-c' in args else args.index('--category')
            kwargs['category'] = args[idx + 1] if idx + 1 < len(args) else None

        if '-v' in args or '--verbose' in args:
            kwargs['verbose'] = True

        if '--top-k' in args:
            idx = args.index('--top-k')
            kwargs['top_k'] = int(args[idx + 1]) if idx + 1 < len(args) else 5

        await cli.cmd_skills(action, query, **kwargs)

    elif command == 'status':
        kwargs = {'verbose': '-v' in args or '--verbose' in args, 'json': '-j' in args or '--json' in args}
        await cli.cmd_status(**kwargs)

    else:
        print(f"[✗] 未知命令: {command}")
        print("[*] 使用 --help 查看帮助")


if __name__ == '__main__':
    asyncio.run(main())
