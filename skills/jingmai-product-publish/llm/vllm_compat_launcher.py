"""
Windows 兼容的 vLLM 启动入口。

当前环境中的 vLLM CLI/serve 入口会直接 import uvloop，
而 Windows/当前环境下未安装 uvloop，会导致服务进程启动即退出。
这里在导入 vLLM 前注入一个最小兼容模块，仅提供 uvloop.run，
等价回退到 asyncio.run。
"""

import asyncio
import sys
import types


def _install_uvloop_compat() -> None:
    if "uvloop" in sys.modules:
        return
    module = types.ModuleType("uvloop")
    module.run = asyncio.run
    sys.modules["uvloop"] = module


def main() -> None:
    _install_uvloop_compat()
    try:
        from vllm.entrypoints.cli.main import main as vllm_main
    except ModuleNotFoundError as exc:
        missing_name = getattr(exc, "name", "") or str(exc)
        raise SystemExit(f"vLLM runtime dependency missing: {missing_name}") from None

    sys.argv = [sys.argv[0], "serve", *sys.argv[1:]]
    try:
        vllm_main()
    except ModuleNotFoundError as exc:
        missing_name = getattr(exc, "name", "") or str(exc)
        raise SystemExit(f"vLLM runtime dependency missing: {missing_name}") from None


if __name__ == "__main__":
    main()
