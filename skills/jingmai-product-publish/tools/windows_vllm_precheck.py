"""
原生 Windows vLLM 预检脚本。

用途：
1. 在安装/修复 GPU torch 之前，确认当前环境状态。
2. 在安装社区 vLLM Windows wheel 之后，确认 vllm._C / torch CUDA / 工具链是否可用。

运行：
    python tools/windows_vllm_precheck.py
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _run_command(command: list[str]) -> dict:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20,
            encoding="utf-8",
            errors="ignore",
        )
        return {
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": (result.stdout or "").strip(),
            "stderr": (result.stderr or "").strip(),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "stdout": "", "stderr": ""}


def _module_version(name: str) -> dict:
    try:
        module = importlib.import_module(name)
        return {
            "installed": True,
            "version": getattr(module, "__version__", "unknown"),
            "file": str(getattr(module, "__file__", "") or ""),
        }
    except Exception as exc:
        return {"installed": False, "error": str(exc)}


def _find_vllm_compiled_extension() -> list[str]:
    try:
        spec = importlib.util.find_spec("vllm")
        if not spec or not spec.submodule_search_locations:
            return []
        base = Path(list(spec.submodule_search_locations)[0])
        matches = []
        for pattern in ("_C*.pyd", "_C*.so", "_moe_C*.pyd", "_moe_C*.so"):
            matches.extend(str(path) for path in base.glob(pattern))
        return sorted(matches)
    except Exception:
        return []


def _torch_probe() -> dict:
    try:
        import torch

        return {
            "installed": True,
            "version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "torch_cuda": str(torch.version.cuda),
            "device_count": int(torch.cuda.device_count()),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "",
        }
    except Exception as exc:
        return {"installed": False, "error": str(exc)}


def _tool_probe(name: str) -> dict:
    path = shutil.which(name)
    payload = {"found": bool(path), "path": path or ""}
    if not path:
        return payload
    result = _run_command([name, "--version"])
    payload["version_output"] = result.get("stdout") or result.get("stderr") or ""
    payload["ok"] = result.get("ok", False)
    return payload


def _recommendation(report: dict) -> dict:
    torch_info = report["torch"]
    compiled = report["vllm_compiled_extensions"]
    tools = report["tools"]

    risks = []
    actions = []

    if not torch_info.get("installed"):
        risks.append("torch 未安装")
        actions.append("先安装 GPU 版 torch，而不是 CPU 版 torch")
    elif not torch_info.get("cuda_available"):
        risks.append("torch 仍不可见 CUDA")
        actions.append("优先安装官方 Windows PyTorch cu128 轮子做基线验证")

    if not compiled:
        risks.append("vllm._C 编译扩展不存在")
        actions.append("不要继续使用官方 pip vllm；改装社区 Windows wheel，并严格匹配其 release 说明")

    for required in ("cl", "cmake", "nvcc"):
        if not tools[required]["found"]:
            risks.append(f"{required} 不在 PATH")

    if not tools["cl"]["found"] or not tools["cmake"]["found"]:
        actions.append("安装 Visual Studio 2022 Build Tools + CMake，并重新打开开发者命令行")
    if not tools["nvcc"]["found"]:
        actions.append("安装 CUDA Toolkit；原生 Windows 强修建议先用 CUDA 12.8 作为基线")

    if not actions:
        actions.append("当前环境已具备继续测试原生 Windows vLLM 的基础条件")

    return {
        "preferred_torch_track": "cu128",
        "preferred_torch_reason": "当前官方 PyTorch Windows 轮子对 cu128 支持成熟，且你的 576.52 驱动可向下兼容 CUDA 12.8。",
        "important_note": "安装 vllm-windows 时，最终以所选 wheel/release 的 torch+CUDA 对齐要求为准；wheel 要求高于这里的通用建议。",
        "risks": risks,
        "next_actions": actions,
    }


def main() -> int:
    report = {
        "python": {
            "version": sys.version,
            "executable": sys.executable,
        },
        "platform": platform.platform(),
        "packages": {
            "vllm": _module_version("vllm"),
            "uvloop": _module_version("uvloop"),
            "xformers": _module_version("xformers"),
        },
        "torch": _torch_probe(),
        "vllm_compiled_extensions": _find_vllm_compiled_extension(),
        "tools": {
            "git": _tool_probe("git"),
            "ninja": _tool_probe("ninja"),
            "cl": _tool_probe("cl"),
            "cmake": _tool_probe("cmake"),
            "nvcc": _tool_probe("nvcc"),
        },
        "nvidia_smi": _run_command(["nvidia-smi"]),
    }
    report["recommendation"] = _recommendation(report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
