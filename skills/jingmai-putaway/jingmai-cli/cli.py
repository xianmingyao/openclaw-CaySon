#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI 主入口
提供命令行工具接口
"""

import asyncio
import sys
import os
import warnings
from pathlib import Path
import click
from loguru import logger

# 抑制 PyInstaller 和 Pydantic V1 兼容性警告（不影响功能）
warnings.filterwarnings("ignore", category=UserWarning, module="pyimod02_importers")

# 修复 Windows 终端编码问题，防止 GBK 编码无法处理 Unicode 字符
if sys.platform == 'win32':
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 添加项目根目录到 Python 路径
ROOT_PATH = Path(__file__).parent
sys.path.insert(0, str(ROOT_PATH))

from config import settings


def _ensure_interactive_session():
    """
    启动时检查 Session，必要时迁移到交互式 Session。
    仅在 Windows 上且 SESSION_MODE != manual 时触发。
    """
    if sys.platform != 'win32':
        return

    from config import settings as _settings
    if _settings.SESSION_MODE == "manual":
        return

    try:
        from app.service.utils.session_detector import SessionDetector
        detector = SessionDetector()
        current = detector.detect_current_session()
        interactive = detector.find_interactive_session()

        if current <= 0 or interactive is None:
            return  # 无法检测或已在正确 Session

        if current == interactive:
            logger.debug(f"[Session] 已在交互式 Session {current}，无需迁移")
            return

        logger.warning(f"[Session] 当前在 Session {current}，交互式桌面在 Session {interactive}")
        if _settings.SESSION_MODE == "auto":
            detector.try_migrate_to_interactive_session()
            # 注意：如果迁移成功，当前进程会退出，不会执行到这里
            logger.warning("[Session] 迁移未成功，将在当前 Session 运行（GUI 操作可能失败）")
        elif _settings.SESSION_MODE == "force_same":
            logger.error("[Session] force_same 模式且不在交互式 Session，建议手动在远程桌面运行")
    except Exception as e:
        logger.warning(f"[Session] 检查失败（不影响非 GUI 命令）: {e}")


def _cleanup_before_run():
    """
    运行前清理

    1. 清空 resources/screenshots 目录的图片
    2. 清空 logs/app.log 和 logs/main.log 的内容
    3. 清空 resources/harness/opinion.md 的内容
    """
    import glob

    ROOT_PATH = Path(__file__).parent.parent

    # 1. 清空 screenshots 目录
    screenshots_dir = ROOT_PATH / "resources" / "screenshots"
    if screenshots_dir.exists():
        screenshot_files = list(screenshots_dir.glob("*.png")) + list(screenshots_dir.glob("*.jpg"))
        deleted_count = 0
        for file in screenshot_files:
            try:
                file.unlink()
                deleted_count += 1
            except Exception as e:
                logger.warning(f"删除截图文件失败 {file}: {e}")
        if deleted_count > 0:
            logger.info(f"[清理] 删除了 {deleted_count} 个截图文件")
        else:
            logger.debug("[清理] screenshots 目录为空，无需删除")

    # 2. 清空日志文件
    log_files = [
        ROOT_PATH / "logs" / "app.log",
        ROOT_PATH / "logs" / "main.log",
    ]

    for log_file in log_files:
        if log_file.exists():
            try:
                # 清空文件内容而不是删除文件
                with open(log_file, "w", encoding="utf-8") as f:
                    f.truncate(0)
                logger.info(f"[清理] 已清空日志文件: {log_file.name}")
            except Exception as e:
                logger.warning(f"清空日志文件失败 {log_file}: {e}")
        else:
            logger.debug(f"[清理] 日志文件不存在: {log_file}")

    # 3. 清空 opinion.md 内容（使用统一资源路径工具）
    # try:
    #     from app.service.utils.resource_path import get_resource_path
    #     opinion_path = get_resource_path("resources/harness/opinion.md")
    #
    #     if opinion_path.exists():
    #         try:
    #             with open(opinion_path, "w", encoding="utf-8") as f:
    #                 f.truncate(0)
    #             logger.info(f"[清理] 已清空 opinion.md 内容")
    #         except Exception as e:
    #             logger.warning(f"清空 opinion.md 失败 {opinion_path}: {e}")
    #     else:
    #         logger.debug(f"[清理] opinion.md 文件不存在: {opinion_path}")
    # except ImportError:
    #     # 如果资源路径工具不可用，回退到传统方式
    #     opinion_path = ROOT_PATH / "resources" / "harness" / "opinion.md"
    #     if opinion_path.exists():
    #         try:
    #             with open(opinion_path, "w", encoding="utf-8") as f:
    #                 f.truncate(0)
    #             logger.info(f"[清理] 已清空 opinion.md 内容")
    #         except Exception as e:
    #             logger.warning(f"清空 opinion.md 失败 {opinion_path}: {e}")
    #     else:
    #         logger.debug(f"[清理] opinion.md 文件不存在: {opinion_path}")


async def ensure_agent_factory():
    """
    确保 agent_factory 已注册到容器中
    初始化 LLM 管理器和 Agent 工厂
    """
    from dependencies.container import get_container
    from app.service.llm.manager import LLMManager
    from app.service.agents.factory import AgentFactory

    container = get_container()

    # 确保 llm_manager 已注册
    if not container.has("llm_manager"):
        llm_manager = LLMManager()
        await llm_manager.initialize()
        container.register_instance("llm_manager", llm_manager)

    # 确保 agent_factory 已注册
    if not container.has("agent_factory"):
        llm_manager = container.get("llm_manager")
        agent_factory = AgentFactory(llm_manager)
        container.register_instance("agent_factory", agent_factory)

    return container.get("agent_factory")


async def ensure_services_initialized():
    """
    确保所有必要的服务已初始化
    这是一个便捷函数，用于在执行命令前自动初始化服务
    """
    from dependencies.container import get_container
    from app.service.register.service_initializer import initialize_cli_services

    container = get_container()

    # 检查是否已经初始化过
    if not container.has("agent_factory"):
        await initialize_cli_services()


@click.group()
@click.version_option(version=settings.APP_VERSION)
def cli():
    """
    Jingmai Agent CLI - 智能体自动化系统命令行工具

    使用方法:
        jingmai run [OPTIONS]      运行单个任务
        jingmai interactive [OPTIONS]  交互式模式
        jingmai batch [OPTIONS]    批量执行任务
        jingmai status [OPTIONS]   查看系统状态
    """
    _ensure_interactive_session()


@cli.command()
@click.argument("description", nargs=-1, required=True)
@click.option("--title", "-t", help="任务标题")
@click.option(
    "--complexity",
    "-c",
    type=click.Choice(["simple", "medium", "complex"]),
    default="medium",
    help="任务复杂度",
)
@click.option("--priority", "-p", type=int, default=5, help="任务优先级 (1-10)")
@click.option(
    "--agent",
    "-a",
    type=click.Choice(["ufo_agent", "rag_agent", "planner_agent"]),
    default="ufo_agent",
    help="Agent 类型",
)
@click.option("--max-steps", "-s", type=int, default=settings.MAX_TASK_STEPS, help="最大执行步数")
def run(description, title, complexity, priority, agent, max_steps):
    """
    运行单个任务

    DESCRIPTION: 任务描述

    示例:
        jingmai run "打开记事本并输入Hello World"
        jingmai run "整理桌面文件" -t "文件整理" -c simple -p 3 -a ufo_agent
    """
    async def _run():
        try:
            # 确保服务已初始化
            await ensure_services_initialized()

            from dependencies.container import get_container
            from dependencies.database import get_database
            from app.service.common.base import CommonService

            # 合并描述
            desc_text = (
                " ".join(description) if isinstance(description, tuple) else description
            )
            task_title = title or desc_text[:50]

            # 获取数据库会话
            db = get_database()

            async with db.get_async_session() as session:
                # 创建任务
                common_service = CommonService()
                task = await common_service.create_task(
                    title=task_title,
                    description=desc_text,
                    complexity=complexity,
                    priority=priority,
                    session=session,
                )
                await session.commit()

                click.echo(f"✓ 创建任务: {task.id}")
                click.echo(f"  标题: {task.title}")
                click.echo(f"  描述: {task.description}")

                # 获取 Agent
                agent_factory = await ensure_agent_factory()

                if not agent_factory:
                    click.echo("✗ Agent 工厂未初始化", err=True)
                    sys.exit(1)

                agent_instance = agent_factory.create_agent(agent)

                if not agent_instance:
                    click.echo(f"✗ 不支持的 Agent 类型: {agent}", err=True)
                    sys.exit(1)

                # 执行任务
                click.echo(f"\n→ 执行任务 (Agent: {agent}, 最大步数: {max_steps})...")

                execution = await agent_instance.execute(task, session, max_steps=max_steps)

                await session.commit()

                # 显示结果
                if execution.state.value == "completed":
                    click.echo(f"\n✓ 任务完成!")
                    if execution.output_data:
                        result = execution.output_data.get("result", "")
                        click.echo(f"  结果: {result}")
                else:
                    click.echo(f"\n✗ 任务失败")
                    if execution.error_message:
                        click.echo(f"  错误: {execution.error_message}")

                # 显示执行详情
                click.echo(f"\n执行详情:")
                click.echo(f"  执行ID: {execution.id}")
                click.echo(f"  状态: {execution.state.value}")
                click.echo(f"  总步数: {execution.total_steps}")
                if execution.duration:
                    click.echo(f"  耗时: {execution.duration:.2f}秒")

        except Exception as e:
            import traceback
            logger.error(f"运行任务失败: {str(e)}\n{traceback.format_exc()}")
            click.echo(f"✗ 运行任务失败: {str(e)}", err=True)
            click.echo(f"详细错误:\n{traceback.format_exc()}", err=True)
            sys.exit(1)
        finally:
            # 清理数据库连接，防止 aiomysql 连接池在 event loop 关闭后报错
            try:
                db = get_database()
                await db.close()
            except Exception:
                pass

    asyncio.run(_run())


@cli.command()
@click.option(
    "--agent",
    "-a",
    type=click.Choice(["ufo_agent", "rag_agent", "planner_agent"]),
    default="ufo_agent",
    help="默认 Agent 类型",
)
def interactive(agent):
    """
    交互式模式

    示例:
        jingmai interactive
        jingmai interactive -a rag_agent
    """
    click.echo(f"进入交互式模式 (默认 Agent: {agent})")
    click.echo("输入 'exit' 或 'quit' 退出")
    click.echo("-" * 50)

    # 先初始化服务
    async def init_services():
        from app.service.register.service_initializer import initialize_cli_services
        await initialize_cli_services()

    asyncio.run(init_services())

    while True:
        try:
            # 读取用户输入
            description = click.prompt("→ 任务", type=str)

            if description.lower() in ["exit", "quit", "q"]:
                click.echo("再见!")
                break

            if not description.strip():
                continue

            # 执行任务
            async def _run_interactive():
                from dependencies.database import get_database
                from app.service.common.base import CommonService

                db = get_database()

                async with db.get_async_session() as session:
                    common_service = CommonService()
                    task = await common_service.create_task(
                        title=description[:50],
                        description=description,
                        complexity="medium",
                        priority=5,
                        session=session,
                    )
                    await session.commit()

                    agent_factory = await ensure_agent_factory()

                    if agent_factory:
                        agent_instance = agent_factory.create_agent(agent)
                        if agent_instance:
                            execution = await agent_instance.execute(task, session)
                            await session.commit()

                            if execution.state.value == "completed":
                                click.echo(f"✓ 完成")
                            else:
                                click.echo(
                                    f"✗ 失败: {execution.error_message or '未知错误'}"
                                )
                        else:
                            click.echo(f"✗ Agent 创建失败")
                    else:
                        click.echo("✗ Agent 工厂未初始化")

            asyncio.run(_run_interactive())

        except (EOFError, KeyboardInterrupt):
            click.echo("\n再见!")
            break
        except Exception as e:
            logger.error(f"执行失败: {str(e)}")
            click.echo(f"✗ 执行失败: {str(e)}", err=True)


@cli.command()
@click.argument("file", type=click.Path(exists=True), required=False)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "txt", "csv"]),
    default="txt",
    help="文件格式",
)
def batch(file, format):
    """
    批量执行任务

    FILE: 任务文件路径（可选，默认从标准输入读取）

    示例:
        jingmai batch tasks.txt
        jingmai batch -f json tasks.json
        echo "任务1\n任务2\n任务3" | jingmai batch
    """

    async def _run_batch():
        tasks = []

        # 读取任务
        if file:
            with open(file, "r", encoding="utf-8") as f:
                if format == "json":
                    import json

                    data = json.load(f)
                    tasks = data if isinstance(data, list) else [data]
                elif format == "csv":
                    import csv

                    reader = csv.DictReader(f)
                    tasks = list(reader)
                else:  # txt
                    tasks = [line.strip() for line in f if line.strip()]
        else:
            # 从标准输入读取
            click.echo("请输入任务（每行一个，Ctrl+D 结束）:")
            tasks = [line.strip() for line in sys.stdin if line.strip()]

        total = len(tasks)
        click.echo(f"共 {total} 个任务")

        # 执行任务
        from dependencies.database import get_database
        from app.service.common.base import CommonService

        db = get_database()

        completed = 0
        failed = 0

        async with db.get_async_session() as session:
            agent_factory = await ensure_agent_factory()

            if not agent_factory:
                click.echo("✗ Agent 工厂未初始化", err=True)
                sys.exit(1)

            for i, task_data in enumerate(tasks, 1):
                try:
                    # 解析任务数据
                    if isinstance(task_data, dict):
                        description = task_data.get("description", "")
                        title = task_data.get("title", description[:50])
                        complexity = task_data.get("complexity", "medium")
                        priority = task_data.get("priority", 5)
                        agent_type = task_data.get("agent", "ufo_agent")
                    else:
                        description = str(task_data)
                        title = description[:50]
                        complexity = "medium"
                        priority = 5
                        agent_type = "ufo_agent"

                    if not description:
                        continue

                    # 创建并执行任务
                    common_service = CommonService()
                    task = await common_service.create_task(
                        title=title,
                        description=description,
                        complexity=complexity,
                        priority=priority,
                        session=session,
                    )
                    await session.commit()

                    agent = agent_factory.create_agent(agent_type)

                    if agent:
                        execution = await agent.execute(task, session)
                        await session.commit()

                        if execution.state.value == "completed":
                            completed += 1
                            click.echo(f"[{i}/{total}] ✓ {title[:30]}")
                        else:
                            failed += 1
                            click.echo(
                                f"[{i}/{total}] ✗ {title[:30]} - {execution.error_message or '失败'}"
                            )
                    else:
                        failed += 1
                        click.echo(f"[{i}/{total}] ✗ {title[:30]} - Agent 创建失败")

                except Exception as e:
                    failed += 1
                    logger.error(f"任务执行失败: {str(e)}")
                    click.echo(f"[{i}/{total}] ✗ {str(task_data)[:30]} - {str(e)}")

        # 显示统计
        click.echo(f"\n执行完成:")
        click.echo(f"  总计: {total}")
        click.echo(f"  成功: {completed}")
        click.echo(f"  失败: {failed}")

    asyncio.run(_run_batch())


# ==================== Memory 命令组 ====================


@cli.group()
def memory():
    """记忆管理命令"""
    pass


@memory.command("create")
@click.argument("content")
@click.option(
    "--type",
    "-t",
    type=click.Choice(["short", "long", "working"]),
    default="short",
    help="记忆类型",
)
@click.option("--key", "-k", help="记忆键")
@click.option(
    "--priority",
    "-p",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default="medium",
    help="优先级",
)
@click.option("--tags", "-g", multiple=True, help="标签")
@click.option("--ttl", type=int, help="过期时间（秒）")
def memory_create(content, type, key, priority, tags, ttl):
    """创建记忆"""

    async def _run():
        try:
            from dependencies.container import get_container
            from dependencies.database import get_database
            from app.service.memory.schemas import (
                MemoryCreateRequest,
                MemoryType,
                MemoryPriority,
            )

            container = get_container()
            memory_manager = container.get("memory_manager")

            if not memory_manager:
                click.echo("✗ 记忆管理器未初始化", err=True)
                sys.exit(1)

            request = MemoryCreateRequest(
                type=MemoryType(type),
                content=content,
                key=key,
                priority=MemoryPriority(priority),
                tags=list(tags),
                ttl=ttl,
            )

            memory = await memory_manager.create_memory(request)

            click.echo(f"✓ 创建记忆成功")
            click.echo(f"  ID: {memory.id}")
            click.echo(f"  类型: {memory.type.value}")
            click.echo(f"  内容: {memory.content[:100]}")

        except Exception as e:
            logger.error(f"创建记忆失败: {str(e)}")
            click.echo(f"✗ 创建记忆失败: {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(_run())


@memory.command("search")
@click.argument("query")
@click.option(
    "--type", "-t", type=click.Choice(["short", "long", "working"]), help="记忆类型"
)
@click.option("--top-k", "-k", type=int, default=5, help="返回结果数量")
@click.option("--tags", "-g", multiple=True, help="标签过滤")
def memory_search(query, type, top_k, tags):
    """搜索记忆"""

    async def _run():
        try:
            from dependencies.container import get_container
            from app.service.memory.schemas import MemorySearchRequest, MemoryType

            container = get_container()
            memory_manager = container.get("memory_manager")

            if not memory_manager:
                click.echo("✗ 记忆管理器未初始化", err=True)
                sys.exit(1)

            search_request = MemorySearchRequest(
                query=query,
                type=MemoryType(type) if type else None,
                top_k=top_k,
                tags=list(tags) if tags else None,
            )

            results = await memory_manager.search_memories(search_request)

            click.echo(f"找到 {len(results)} 条记忆:\n")
            for i, result in enumerate(results, 1):
                click.echo(f"{i}. [{result.type.value}] {result.content[:80]}")
                if result.tags:
                    click.echo(f"   标签: {', '.join(result.tags)}")
                if result.score:
                    click.echo(f"   相关度: {result.score:.2f}")
                click.echo()

        except Exception as e:
            logger.error(f"搜索记忆失败: {str(e)}")
            click.echo(f"✗ 搜索记忆失败: {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(_run())


@memory.command("stats")
def memory_stats():
    """显示记忆统计"""

    async def _run():
        try:
            from dependencies.container import get_container

            container = get_container()
            memory_manager = container.get("memory_manager")

            if not memory_manager:
                click.echo("✗ 记忆管理器未初始化", err=True)
                sys.exit(1)

            stats = await memory_manager.get_statistics()

            click.echo("记忆统计:")
            click.echo(f"  短期记忆: {stats['short_term_count']}")
            click.echo(f"  长期记忆: {stats['long_term_count']}")
            click.echo(f"  工作记忆: {stats['working_memory_count']}")
            click.echo(f"  总计: {stats['total_count']}")

        except Exception as e:
            logger.error(f"获取统计失败: {str(e)}")
            click.echo(f"✗ 获取统计失败: {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(_run())


@memory.command("clear")
@click.option(
    "--type", "-t", type=click.Choice(["short", "long", "working"]), help="记忆类型"
)
def memory_clear(type):
    """清空记忆"""

    async def _run():
        try:
            from dependencies.container import get_container
            from app.service.memory.base import MemoryType

            container = get_container()
            memory_manager = container.get("memory_manager")

            if not memory_manager:
                click.echo("✗ 记忆管理器未初始化", err=True)
                sys.exit(1)

            if type == "working":
                await memory_manager.clear_working_memory()
                click.echo("✓ 工作记忆已清空")
            else:
                click.echo("✗ 暂不支持清空其他类型的记忆", err=True)

        except Exception as e:
            logger.error(f"清空记忆失败: {str(e)}")
            click.echo(f"✗ 清空记忆失败: {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(_run())


# ==================== RAG 命令组 ====================


@cli.group()
def rag():
    """RAG 知识库管理命令"""
    pass


@rag.command("query")
@click.argument("query")
@click.option("--top-k", "-k", type=int, default=5, help="返回结果数量")
@click.option("--rerank", "-r", is_flag=True, help="启用重排序")
def rag_query(query, top_k, rerank):
    """查询知识库"""

    async def _run():
        try:
            from dependencies.container import get_container
            from dependencies.database import get_database
            from app.service.rag.schemas import ServiceRAGQuery

            container = get_container()
            rag_service = container.get("rag_service")

            if not rag_service:
                click.echo("✗ RAG 服务未初始化", err=True)
                sys.exit(1)

            db = get_database()

            async with db.get_async_session() as session:
                service_query = ServiceRAGQuery(
                    query=query, top_k=top_k, use_rerank=rerank
                )

                response = await rag_service.query(service_query, session)

                click.echo(f"查询结果:\n")
                click.echo(f"答案: {response.answer}\n")

                if response.sources:
                    click.echo(f"来源 ({len(response.sources)} 条):")
                    for i, source in enumerate(response.sources, 1):
                        click.echo(f"{i}. [{source.score:.2f}] {source.content[:100]}")

        except Exception as e:
            logger.error(f"RAG 查询失败: {str(e)}")
            click.echo(f"✗ RAG 查询失败: {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(_run())


@rag.command("stats")
def rag_stats():
    """显示知识库统计"""

    async def _run():
        try:
            from dependencies.container import get_container
            from dependencies.database import get_database

            container = get_container()
            rag_service = container.get("rag_service")

            if not rag_service:
                click.echo("✗ RAG 服务未初始化", err=True)
                sys.exit(1)

            db = get_database()

            async with db.get_async_session() as session:
                stats = await rag_service.get_statistics(session)

                click.echo("知识库统计:")
                click.echo(f"  总文档数: {stats.get('total_documents', 0)}")
                click.echo(f"  总块数: {stats.get('total_chunks', 0)}")
                click.echo(f"  总向量数: {stats.get('total_vectors', 0)}")

        except Exception as e:
            logger.error(f"获取统计失败: {str(e)}")
            click.echo(f"✗ 获取统计失败: {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(_run())


# ==================== Skills 命令组 ====================


@cli.group()
def skills():
    """技能管理命令"""
    pass


@skills.command("list")
@click.option("--category", "-c", help="按类别筛选")
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
def skills_list(category, verbose):
    """列出可用技能"""

    async def _run():
        try:
            from dependencies.container import get_container
            from app.service.skills.skill import SkillCategory

            container = get_container()
            skill_registry = container.get("skill_registry")

            if not skill_registry:
                click.echo("✗ 技能注册表未初始化", err=True)
                sys.exit(1)

            # 获取所有技能
            all_skills = skill_registry.list_all()

            # 过滤
            if category:
                try:
                    cat = SkillCategory(category.upper())
                    all_skills = [s for s in all_skills if s.category == cat]
                except ValueError:
                    click.echo(f"✗ 无效的类别: {category}", err=True)
                    sys.exit(1)

            click.echo(f"可用技能 ({len(all_skills)} 个):\n")

            for skill in all_skills:
                click.echo(f"• {skill.name} (v{skill.version})")
                if verbose:
                    click.echo(f"  描述: {skill.description}")
                    click.echo(f"  类别: {skill.category.value}")
                    if skill.actions:
                        click.echo(f"  动作: {', '.join(skill.actions.keys())}")
                click.echo()

        except Exception as e:
            logger.error(f"列出技能失败: {str(e)}")
            click.echo(f"✗ 列出技能失败: {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(_run())


@skills.command("search")
@click.argument("query")
@click.option("--top-k", "-k", type=int, default=5, help="返回结果数量")
def skills_search(query, top_k):
    """搜索技能"""

    async def _run():
        try:
            from dependencies.container import get_container

            container = get_container()
            skill_registry = container.get("skill_registry")

            if not skill_registry:
                click.echo("✗ 技能注册表未初始化", err=True)
                sys.exit(1)

            results = await skill_registry.search_skills(query, top_k=top_k)

            click.echo(f"找到 {len(results)} 个技能:\n")

            for i, skill in enumerate(results, 1):
                click.echo(f"{i}. {skill.name} (v{skill.version})")
                click.echo(f"   {skill.description}")
                if skill.category:
                    click.echo(f"   类别: {skill.category.value}")
                click.echo()

        except Exception as e:
            logger.error(f"搜索技能失败: {str(e)}")
            click.echo(f"✗ 搜索技能失败: {str(e)}", err=True)
            sys.exit(1)

    asyncio.run(_run())


# ==================== Status 命令增强 ====================


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="显示详细信息")
@click.option("--json", "-j", "as_json", is_flag=True, help="以 JSON 格式输出")
@click.option("--init", "-i", is_flag=True, help="初始化所有服务后再检查状态")
def status(verbose, as_json, init):
    """
    查看系统状态

    示例:
        jingmai status
        jingmai status -v
        jingmai status --json
        jingmai status -i    # 初始化服务后检查
    """

    async def _run_status():
        # 服务初始化状态标记
        services_initialized = False

        # 定义智能服务检查函数
        async def smart_check_service(service_name, check_func):
            """智能服务检查：如果服务未注册，先尝试初始化"""
            nonlocal services_initialized

            # 如果服务还没初始化过，先尝试全局初始化
            if not services_initialized:
                try:
                    from dependencies.container import get_container
                    container = get_container()

                    # 检查核心服务是否已注册
                    core_services = ["llm_manager", "agent_factory", "memory_manager", "rag_service", "skill_registry"]
                    has_any_core = any(container.has(s) for s in core_services)

                    if not has_any_core:
                        # 没有核心服务，执行初始化
                        from app.service.register.service_initializer import initialize_cli_services
                        if not init:  # 避免重复输出
                            click.echo("正在自动初始化 CLI 服务...")
                        await initialize_cli_services()
                        if not init:
                            click.echo("")
                        services_initialized = True
                except Exception as init_error:
                    logger.warning(f"服务自动初始化失败: {str(init_error)}")

            # 执行服务检查
            return await check_func()

        status_data = {"timestamp": None, "services": {}}

        from datetime import datetime

        status_data["timestamp"] = datetime.now().isoformat()

        def _print_status(name, status, detail=""):
            if as_json:
                status_data["services"][name] = {"status": status, "detail": detail}
            else:
                # 使用 ASCII 友好的符号，确保在所有平台上正确显示
                if status == "ok":
                    symbol = "[OK]"
                    text = detail or "正常"
                elif status == "warning":
                    symbol = "[WARN]"
                    text = detail or "可选服务未启用"
                else:  # error
                    symbol = "[ERR]"
                    text = detail or "异常"
                click.echo(f"{symbol} {name}: {text}")

        # 如果指定了 --init 参数，先初始化所有服务
        if init:
            click.echo("正在初始化 CLI 服务...")
            from app.service.register.service_initializer import initialize_cli_services
            await initialize_cli_services()
            click.echo("")
            services_initialized = True

        # 检查数据库
        async def check_database():
            from dependencies.database import get_database
            db = get_database()
            return ("ok", None)

        try:
            status, detail = await smart_check_service("database", check_database)
            _print_status("数据库", status, detail or "")
        except Exception as e:
            _print_status("数据库", "error", str(e))

        # 检查 Redis
        async def check_redis():
            from dependencies.redis import get_redis_client
            redis = get_redis_client()
            client = await redis.get_client()
            await client.ping()
            return ("ok", None)

        try:
            status, detail = await smart_check_service("redis", check_redis)
            _print_status("Redis", status, detail or "")
        except Exception as e:
            _print_status("Redis", "error", str(e))

        # 检查 Milvus（可选服务）
        async def check_milvus():
            from dependencies.container import get_container
            container = get_container()
            if container.has("milvus_client"):
                milvus_client = container.get("milvus_client")
                return ("ok", None)
            else:
                return ("warning", "未启用（可选）")

        try:
            status, detail = await smart_check_service("milvus", check_milvus)
            _print_status("Milvus", status, detail or "")
        except Exception as e:
            _print_status("Milvus", "error", str(e))

        # 检查 LLM
        async def check_llm():
            from dependencies.container import get_container
            container = get_container()
            llm_manager = container.get("llm_manager")

            if llm_manager:
                providers = llm_manager.get_available_providers()
                return ("ok", f"提供者: {', '.join(providers)}")
            else:
                return ("error", "未初始化")

        try:
            status, detail = await smart_check_service("llm", check_llm)
            _print_status("LLM 服务", status, detail or "")
        except Exception as e:
            _print_status("LLM 服务", "error", str(e))

        # 检查向量存储（可选服务）
        async def check_vector_store():
            from dependencies.container import get_container
            container = get_container()
            if container.has("vector_store"):
                vector_store = container.get("vector_store")
                return ("ok", None)
            else:
                return ("warning", "未启用（可选）")

        try:
            status, detail = await smart_check_service("vector_store", check_vector_store)
            _print_status("向量存储", status, detail or "")
        except Exception as e:
            _print_status("向量存储", "error", str(e))

        # 检查 OSS 存储（可选服务）
        async def check_oss_storage():
            from dependencies.container import get_container
            container = get_container()
            if container.has("oss_storage"):
                oss_storage = container.get("oss_storage")
                return ("ok", None)
            else:
                return ("warning", "未启用（可选）")

        try:
            status, detail = await smart_check_service("oss_storage", check_oss_storage)
            _print_status("OSS 存储", status, detail or "")
        except Exception as e:
            _print_status("OSS 存储", "error", str(e))

        # 检查记忆管理器
        async def check_memory_manager():
            from dependencies.container import get_container
            container = get_container()
            memory_manager = container.get("memory_manager")

            if memory_manager:
                stats = await memory_manager.get_statistics()
                return ("ok", f"总计: {stats['total_count']}")
            else:
                return ("error", "未初始化")

        try:
            status, detail = await smart_check_service("memory_manager", check_memory_manager)
            _print_status("记忆管理", status, detail or "")
        except Exception as e:
            _print_status("记忆管理", "error", str(e))

        # 检查 RAG 服务
        async def check_rag_service():
            from dependencies.container import get_container
            container = get_container()
            rag_service = container.get("rag_service")

            if rag_service:
                return ("ok", None)
            else:
                return ("error", "未初始化")

        try:
            status, detail = await smart_check_service("rag_service", check_rag_service)
            _print_status("RAG 服务", status, detail or "")
        except Exception as e:
            _print_status("RAG 服务", "error", str(e))

        # 检查技能注册表
        async def check_skill_registry():
            from dependencies.container import get_container
            container = get_container()
            skill_registry = container.get("skill_registry")

            if skill_registry:
                all_skills = skill_registry.list_skills()
                return ("ok", f"已注册: {len(all_skills)} 个")
            else:
                return ("error", "未初始化")

        try:
            status, detail = await smart_check_service("skill_registry", check_skill_registry)
            _print_status("技能注册表", status, detail or "")
        except Exception as e:
            _print_status("技能注册表", "error", str(e))

        import json
        # 显示任务统计
        if verbose:
            try:
                from dependencies.database import get_database
                from sqlalchemy import select, func
                from models.task import Task

                db = get_database()

                async with db.get_async_session() as session:
                    result = await session.execute(
                        select(Task.status, func.count(Task.id)).group_by(Task.status)
                    )

                    if as_json:
                        task_stats = {status: count for status, count in result.all()}
                        status_data["tasks"] = task_stats
                    else:
                        click.echo(f"\n任务统计:")
                        for status, count in result.all():
                            click.echo(f"  {status}: {count}")

            except Exception as e:
                logger.error(f"获取任务统计失败: {str(e)}")

        # JSON 输出
        if as_json:
            click.echo(json.dumps(status_data, indent=2, ensure_ascii=False))

    asyncio.run(_run_status())


if __name__ == "__main__":
    _cleanup_before_run()
    cli()


__all__ = ["cli"]
