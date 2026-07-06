"""交互式 dashboard 入口 — 从 command.py 重新导出，保持向后兼容。"""

from __future__ import annotations

from jm_ufo_agent.cli.command import render_dashboard, render_live_dashboard, stream_dashboard_from_jsonl

__all__ = ["render_dashboard", "render_live_dashboard", "stream_dashboard_from_jsonl"]
