"""
vLLM 服务预热与自启动管理。
"""
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

from loguru import logger

from llm.vllm import VLLMProvider


def _is_local_base_url(base_url: str) -> bool:
    host = (urlparse(str(base_url or "")).hostname or "").strip().lower()
    return host in {"", "localhost", "127.0.0.1", "0.0.0.0"}


def _extract_vllm_port(base_url: str) -> int:
    parsed = urlparse(str(base_url or ""))
    if parsed.port:
        return int(parsed.port)
    return 8001


def _build_vllm_command(settings) -> list[str]:
    custom = str(getattr(settings, "VLLM_LAUNCH_COMMAND", "") or "").strip()
    if custom:
        return shlex.split(custom, posix=False)

    entrypoint_module = "vllm.entrypoints.openai.api_server"
    if os.name == "nt":
        entrypoint_module = "llm.vllm_compat_launcher"

    command = [
        sys.executable,
        "-m",
        entrypoint_module,
        "--model",
        str(settings.VLLM_MODEL),
        "--host",
        "127.0.0.1",
        "--port",
        str(_extract_vllm_port(settings.VLLM_BASE_URL)),
    ]
    extra_args = str(getattr(settings, "VLLM_EXTRA_ARGS", "") or "").strip()
    if extra_args:
        command.extend(shlex.split(extra_args, posix=False))
    return command


def _warmup_vllm(provider: VLLMProvider) -> bool:
    try:
        provider.invoke("ping", max_tokens=8, temperature=0)
        return True
    except Exception as exc:
        logger.warning(f"[vLLMService] warmup failed: {exc}")
        return False


def _probe_local_vllm_runtime() -> Dict[str, Any]:
    probe_code = """
import asyncio
import json
import sys
import types

result = {"ok": False, "missing": [], "stage": "", "error": ""}

try:
    try:
        import uvloop  # noqa: F401
    except Exception as exc:
        result["missing"].append("uvloop")
        result["uvloop_error"] = str(exc)
        if sys.platform == "win32":
            module = types.ModuleType("uvloop")
            module.run = asyncio.run
            sys.modules["uvloop"] = module

    import vllm  # noqa: F401
    result["stage"] = "vllm_imported"
    import vllm._C  # noqa: F401
    result["ok"] = True
except Exception as exc:
    result["error"] = str(exc)
    if "vllm._C" in str(exc):
        result["missing"].append("vllm._C")
print(json.dumps(result, ensure_ascii=False))
"""
    try:
        completed = subprocess.run(
            [sys.executable, "-c", probe_code],
            capture_output=True,
            text=True,
            timeout=20,
            encoding="utf-8",
            errors="ignore",
        )
        stdout = (completed.stdout or "").strip()
        if stdout:
            import json

            payload = json.loads(stdout)
            payload["returncode"] = completed.returncode
            return payload
        return {
            "ok": False,
            "missing": [],
            "stage": "probe_no_output",
            "error": (completed.stderr or "").strip() or f"returncode={completed.returncode}",
            "returncode": completed.returncode,
        }
    except Exception as exc:
        return {"ok": False, "missing": [], "stage": "probe_exception", "error": str(exc)}


def ensure_vllm_ready(settings) -> Dict[str, Any]:
    provider = VLLMProvider(
        base_url=settings.VLLM_BASE_URL,
        model=settings.VLLM_MODEL,
        timeout=settings.LLM_TIMEOUT,
    )
    report: Dict[str, Any] = {
        "ready": False,
        "started": False,
        "warmup_success": False,
        "reason": "",
        "pid": None,
        "log_file": "",
        "command": [],
    }

    if provider.health_check():
        report["ready"] = True
        report["reason"] = "already_healthy"
        report["warmup_success"] = _warmup_vllm(provider)
        return report

    if not bool(getattr(settings, "VLLM_AUTOSTART_ENABLED", False)):
        report["reason"] = "autostart_disabled"
        return report

    if not _is_local_base_url(settings.VLLM_BASE_URL):
        report["reason"] = "non_local_base_url"
        return report

    runtime_probe = _probe_local_vllm_runtime()
    report["runtime_probe"] = runtime_probe
    if not runtime_probe.get("ok"):
        missing = ",".join(runtime_probe.get("missing", []) or []) or "unknown"
        report["reason"] = f"runtime_missing:{missing}"
        report["runtime_error"] = runtime_probe.get("error", "")
        return report

    command = _build_vllm_command(settings)
    log_path = Path(settings.LOG_DIR) / "vllm-startup.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    report["command"] = command
    report["log_file"] = str(log_path.resolve())

    creationflags = 0
    for flag_name in ("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP", "CREATE_NO_WINDOW"):
        creationflags |= int(getattr(subprocess, flag_name, 0) or 0)

    log_handle = log_path.open("a", encoding="utf-8")
    try:
        process = subprocess.Popen(
            command,
            cwd=str(Path(__file__).resolve().parent.parent),
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
        )
    finally:
        log_handle.close()

    report["started"] = True
    report["pid"] = process.pid
    report["reason"] = "started"
    logger.info(f"[vLLMService] start requested pid={process.pid} command={command}")

    deadline = time.time() + float(getattr(settings, "VLLM_STARTUP_TIMEOUT", 240) or 240)
    poll_interval = float(getattr(settings, "VLLM_STARTUP_POLL_INTERVAL", 2.0) or 2.0)
    while time.time() < deadline:
        if provider.health_check():
            report["ready"] = True
            report["reason"] = "started_and_healthy"
            report["warmup_success"] = _warmup_vllm(provider)
            return report
        if process.poll() is not None:
            report["reason"] = f"process_exited:{process.returncode}"
            try:
                if log_path.exists():
                    tail_lines = log_path.read_text(encoding="utf-8", errors="ignore").splitlines()[-8:]
                    if tail_lines:
                        report["log_tail"] = "\n".join(tail_lines)
            except Exception:
                pass
            return report
        time.sleep(poll_interval)

    report["reason"] = "startup_timeout"
    return report
