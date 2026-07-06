"""CLI 入口包 — 从 command.py 重新导出，保持向后兼容。"""

from __future__ import annotations

from jm_ufo_agent.cli.command import (
    DashboardState,
    ProgressDashboard,
    build_parser,
    main,
    render_dashboard,
    render_live_dashboard,
    stream_dashboard_from_jsonl,
)

__all__ = [
    "DashboardState",
    "ProgressDashboard",
    "build_parser",
    "main",
    "render_dashboard",
    "render_live_dashboard",
    "stream_dashboard_from_jsonl",
]
