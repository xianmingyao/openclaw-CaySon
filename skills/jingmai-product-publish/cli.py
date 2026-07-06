"""根目录 CLI 入口 — 从 jm_ufo_agent.cli.command 重新导出。"""

from jm_ufo_agent.cli.command import main  # noqa: F401

if __name__ == "__main__":
    raise SystemExit(main())
