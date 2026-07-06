"""`python -m jm_ufo_agent` 入口。"""

from __future__ import annotations

from jm_ufo_agent.cli.command import main


if __name__ == "__main__":
    # 统一复用 CLI main，避免模块入口和 console script 行为分叉。
    # main 内部默认走 dry-run backend，不会触碰真实京麦窗口。
    # 返回码直接交给 SystemExit，方便 CI 判断执行结果。
    raise SystemExit(main())
