#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统操作 Actions
"""
import asyncio
import json
import subprocess
from typing import Any, Dict, List

from loguru import logger

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)


class WaitAction(UFOBaseAction):
    """等待指定秒数"""
    name = "wait"
    description = "等待指定秒数"
    parameters = [
        ActionParameter(name="seconds", type=ParameterType.FLOAT, description="等待秒数", required=False, default=2.0),
    ]

    async def _execute(self, seconds: float = 2.0) -> ActionResult:
        await asyncio.sleep(seconds)
        return ActionResult(success=True, metadata={"waited_seconds": seconds})


class RunCommandAction(UFOBaseAction):
    """执行系统命令（cmd/powershell）"""
    name = "run_command"
    description = "执行系统命令（cmd/powershell），用于进程检测、应用启动等系统级操作"
    parameters = [
        ActionParameter(name="command", type=ParameterType.STRING, description="要执行的命令"),
        ActionParameter(name="shell", type=ParameterType.STRING, description="Shell 类型 (cmd/powershell)", required=False, default="cmd"),
    ]

    async def _execute(self, command: str, shell: str = "cmd") -> ActionResult:
        result = _run_system_command(command, shell=shell)
        data = {
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "returncode": result["returncode"],
        }
        if not result["success"]:
            return ActionResult(success=False, error=result["stderr"][:200], data=data)
        return ActionResult(success=True, data=data)


class CheckProcessAction(UFOBaseAction):
    """检查指定进程是否正在运行"""
    name = "check_process"
    description = "检查指定进程是否正在运行，返回进程信息"
    parameters = [
        ActionParameter(name="process_name", type=ParameterType.STRING, description="进程名（支持模糊匹配）"),
    ]

    async def _execute(self, process_name: str) -> ActionResult:
        proc_result = _check_process_running(process_name)
        return ActionResult(
            success=True,
            data={"process_info": proc_result},
        )


class NoAction(UFOBaseAction):
    """空操作，不执行任何动作"""
    name = "no_action"
    description = "空操作，不执行任何动作（用于步骤占位或跳过）"
    parameters = []

    async def _execute(self) -> ActionResult:
        return ActionResult(success=True, metadata={"action": "no_op"})


# ==================== 内部工具函数 ====================

def _run_system_command(command: str, shell: str = "cmd", timeout: int = 15) -> Dict[str, Any]:
    """执行系统命令并返回结果"""
    try:
        if shell == "powershell":
            # 强制 PowerShell 使用 UTF-8 输出编码，避免中文乱码
            command = f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {command}"
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command],
                capture_output=True, text=True, timeout=timeout,
                encoding="utf-8", errors="replace"
            )
        else:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, encoding="gbk", errors="replace"
            )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": f"命令执行超时 ({timeout}秒)", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def _check_process_running(process_name: str) -> Dict[str, Any]:
    """检查指定进程是否正在运行"""
    try:
        ps_cmd = (
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            f"Get-Process | Where-Object {{$_.ProcessName -like '*{process_name}*'}} | "
            "Select-Object Id, ProcessName | ConvertTo-Json -Depth 1"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace"
        )

        processes = []
        if result.stdout.strip():
            try:
                data = json.loads(result.stdout.strip())
                if isinstance(data, dict):
                    data = [data]
                for p in data:
                    processes.append({
                        "pid": p.get("Id", 0),
                        "name": p.get("ProcessName", ""),
                        "cmdline": p.get("CmdLine", "")
                    })
            except (json.JSONDecodeError, TypeError):
                pass

        return {
            "running": len(processes) > 0,
            "processes": processes,
            "match_count": len(processes)
        }
    except Exception as e:
        return {"running": False, "processes": [], "match_count": 0, "error": str(e)}
