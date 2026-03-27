#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shell / 文件系统 Actions

提供命令执行、文件操作、系统信息查询等能力。
参考 UFO 的 ShellCommand (shell_client.py)。
所有操作通过 subprocess + pathlib 实现，无额外依赖。
"""
import asyncio
import json
import os
import platform
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)


# ==================== 内部工具函数 ====================

def _run_shell(command: str, timeout: int = 30) -> Dict[str, Any]:
    """执行 Shell 命令"""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": f"命令超时 ({timeout}秒)", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def _run_powershell(command: str, timeout: int = 30) -> Dict[str, Any]:
    """执行 PowerShell 命令"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace",
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": f"命令超时 ({timeout}秒)", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


# ==================== Action 类 ====================

class RunShellAction(UFOBaseAction):
    """执行 Shell 命令（通用入口）"""
    name = "run_shell"
    description = "执行 Shell 命令并返回输出"
    parameters = [
        ActionParameter(name="command", type=ParameterType.STRING, description="要执行的 Shell 命令"),
        ActionParameter(name="timeout", type=ParameterType.INTEGER,
                         description="超时秒数", required=False, default=30),
    ]

    async def _execute(self, command: str, timeout: int = 30) -> ActionResult:
        result = _run_shell(command, timeout=timeout)
        return ActionResult(success=result["success"],
                           error=result["stderr"] if not result["success"] else None,
                           data={"stdout": result["stdout"], "returncode": result["returncode"]})


class ExecuteCommandAction(UFOBaseAction):
    """执行系统命令"""
    name = "execute_command"
    description = "执行系统命令（cmd 或 powershell）并返回结构化输出"
    parameters = [
        ActionParameter(name="command", type=ParameterType.STRING, description="要执行的命令"),
        ActionParameter(name="shell", type=ParameterType.STRING,
                         description="Shell 类型 (cmd/powershell)", required=False, default="cmd"),
        ActionParameter(name="timeout", type=ParameterType.INTEGER,
                         description="超时秒数", required=False, default=30),
    ]

    async def _execute(self, command: str, shell: str = "cmd", timeout: int = 30) -> ActionResult:
        if shell == "powershell":
            result = _run_powershell(command, timeout=timeout)
        else:
            result = _run_shell(command, timeout=timeout)
        return ActionResult(success=result["success"],
                           error=result["stderr"] if not result["success"] else None,
                           data={"stdout": result["stdout"], "returncode": result["returncode"]})


class ChangeDirectoryAction(UFOBaseAction):
    """切换工作目录"""
    name = "change_directory"
    description = "切换当前工作目录"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="目标目录路径"),
    ]

    async def _execute(self, path: str) -> ActionResult:
        try:
            p = Path(path).resolve()
            if not p.exists():
                return ActionResult(success=False, error=f"目录不存在: {path}")
            if not p.is_dir():
                return ActionResult(success=False, error=f"路径不是目录: {path}")
            os.chdir(p)
            return ActionResult(success=True, data={"cwd": str(p)})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetCurrentDirectoryAction(UFOBaseAction):
    """获取当前工作目录"""
    name = "get_current_directory"
    description = "获取当前工作目录路径"
    parameters = []

    async def _execute(self) -> ActionResult:
        return ActionResult(success=True, data={"cwd": os.getcwd()})


class ListFilesAction(UFOBaseAction):
    """列出目录中的文件和子目录"""
    name = "list_files"
    description = "列出指定目录中的文件和子目录"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING,
                         description="目录路径（默认当前目录）", required=False, default="."),
        ActionParameter(name="pattern", type=ParameterType.STRING,
                         description="文件名过滤模式 (如 *.txt)", required=False, default="*"),
        ActionParameter(name="recursive", type=ParameterType.BOOLEAN,
                         description="是否递归列出", required=False, default=False),
    ]

    async def _execute(self, path: str = ".", pattern: str = "*", recursive: bool = False) -> ActionResult:
        try:
            p = Path(path).resolve()
            if not p.is_dir():
                return ActionResult(success=False, error=f"不是目录: {path}")
            items = []
            if recursive:
                for item in p.rglob(pattern):
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else 0,
                    })
            else:
                for item in p.glob(pattern):
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else 0,
                    })
            # 限制返回数量
            items = items[:500]
            return ActionResult(success=True, data={"items": items, "count": len(items), "path": str(p)})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class CreateDirectoryAction(UFOBaseAction):
    """创建目录"""
    name = "create_directory"
    description = "创建目录（支持多层创建）"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="要创建的目录路径"),
        ActionParameter(name="exist_ok", type=ParameterType.BOOLEAN,
                         description="目录已存在时是否忽略错误", required=False, default=True),
    ]

    async def _execute(self, path: str, exist_ok: bool = True) -> ActionResult:
        try:
            p = Path(path)
            p.mkdir(parents=True, exist_ok=exist_ok)
            return ActionResult(success=True, data={"path": str(p.resolve())})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class RemoveFileAction(UFOBaseAction):
    """删除文件或目录"""
    name = "remove_file"
    description = "删除文件或目录"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="要删除的文件或目录路径"),
        ActionParameter(name="recursive", type=ParameterType.BOOLEAN,
                         description="删除目录时是否递归删除", required=False, default=False),
    ]

    async def _execute(self, path: str, recursive: bool = False) -> ActionResult:
        try:
            p = Path(path)
            if not p.exists():
                return ActionResult(success=False, error=f"路径不存在: {path}")
            if p.is_dir():
                if recursive:
                    import shutil
                    shutil.rmtree(p)
                else:
                    p.rmdir()
            else:
                p.unlink()
            return ActionResult(success=True, data={"removed": str(p)})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class CopyFileAction(UFOBaseAction):
    """复制文件或目录"""
    name = "copy_file"
    description = "复制文件或目录到目标路径"
    parameters = [
        ActionParameter(name="source", type=ParameterType.STRING, description="源文件或目录路径"),
        ActionParameter(name="destination", type=ParameterType.STRING, description="目标路径"),
    ]

    async def _execute(self, source: str, destination: str) -> ActionResult:
        try:
            src = Path(source)
            dst = Path(destination)
            if not src.exists():
                return ActionResult(success=False, error=f"源路径不存在: {source}")
            if src.is_dir():
                import shutil
                shutil.copytree(src, dst)
            else:
                import shutil
                shutil.copy2(src, dst)
            return ActionResult(success=True, data={"from": str(src), "to": str(dst)})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class MoveFileAction(UFOBaseAction):
    """移动/重命名文件或目录"""
    name = "move_file"
    description = "移动或重命名文件/目录"
    parameters = [
        ActionParameter(name="source", type=ParameterType.STRING, description="源路径"),
        ActionParameter(name="destination", type=ParameterType.STRING, description="目标路径"),
    ]

    async def _execute(self, source: str, destination: str) -> ActionResult:
        try:
            import shutil
            src = Path(source)
            dst = Path(destination)
            if not src.exists():
                return ActionResult(success=False, error=f"源路径不存在: {source}")
            shutil.move(str(src), str(dst))
            return ActionResult(success=True, data={"from": str(src), "to": str(dst)})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class ReadFileAction(UFOBaseAction):
    """读取文件内容"""
    name = "read_file"
    description = "读取文件内容"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="文件路径"),
        ActionParameter(name="encoding", type=ParameterType.STRING,
                         description="文件编码", required=False, default="utf-8"),
        ActionParameter(name="offset", type=ParameterType.INTEGER,
                         description="起始行号 (从 0 开始)", required=False, default=0),
        ActionParameter(name="limit", type=ParameterType.INTEGER,
                         description="最大读取行数", required=False, default=500),
    ]

    async def _execute(self, path: str, encoding: str = "utf-8", offset: int = 0, limit: int = 500) -> ActionResult:
        try:
            p = Path(path)
            if not p.exists():
                return ActionResult(success=False, error=f"文件不存在: {path}")
            lines = p.read_text(encoding=encoding, errors="replace").splitlines()
            selected = lines[offset:offset + limit]
            return ActionResult(success=True, data={
                "content": "\n".join(selected),
                "total_lines": len(lines),
                "returned_lines": len(selected),
                "offset": offset,
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class WriteFileAction(UFOBaseAction):
    """写入文件内容"""
    name = "write_file"
    description = "将内容写入文件（覆盖写入）"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="文件路径"),
        ActionParameter(name="content", type=ParameterType.STRING, description="要写入的内容"),
        ActionParameter(name="encoding", type=ParameterType.STRING,
                         description="文件编码", required=False, default="utf-8"),
        ActionParameter(name="append", type=ParameterType.BOOLEAN,
                         description="是否追加写入", required=False, default=False),
    ]

    async def _execute(self, path: str, content: str, encoding: str = "utf-8", append: bool = False) -> ActionResult:
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            mode = "a" if append else "w"
            p.write_text(content, encoding=encoding)
            return ActionResult(success=True, data={"path": str(p), "mode": "append" if append else "write"})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class CheckFileExistsAction(UFOBaseAction):
    """检查文件或目录是否存在"""
    name = "check_file_exists"
    description = "检查文件或目录是否存在"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="文件或目录路径"),
    ]

    async def _execute(self, path: str) -> ActionResult:
        p = Path(path)
        exists = p.exists()
        return ActionResult(success=True, data={
            "path": path,
            "exists": exists,
            "is_file": p.is_file() if exists else False,
            "is_dir": p.is_dir() if exists else False,
        })


class GetFileInfoAction(UFOBaseAction):
    """获取文件详细信息"""
    name = "get_file_info"
    description = "获取文件详细信息（大小、修改时间、创建时间等）"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="文件路径"),
    ]

    async def _execute(self, path: str) -> ActionResult:
        try:
            p = Path(path)
            if not p.exists():
                return ActionResult(success=False, error=f"路径不存在: {path}")
            stat = p.stat()
            return ActionResult(success=True, data={
                "path": str(p),
                "name": p.name,
                "extension": p.suffix,
                "is_file": p.is_file(),
                "is_dir": p.is_dir(),
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 3),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class FindFilesAction(UFOBaseAction):
    """搜索/查找文件"""
    name = "find_files"
    description = "在指定目录中搜索文件（支持通配符和名称过滤）"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING,
                         description="搜索根目录（默认当前目录）", required=False, default="."),
        ActionParameter(name="pattern", type=ParameterType.STRING,
                         description="文件名模式 (如 *.py, *.txt)", required=False, default="*"),
        ActionParameter(name="name_contains", type=ParameterType.STRING,
                         description="文件名包含的关键词", required=False, default=""),
        ActionParameter(name="max_results", type=ParameterType.INTEGER,
                         description="最大结果数", required=False, default=50),
    ]

    async def _execute(self, path: str = ".", pattern: str = "*", name_contains: str = "",
                       max_results: int = 50) -> ActionResult:
        try:
            p = Path(path).resolve()
            if not p.is_dir():
                return ActionResult(success=False, error=f"不是目录: {path}")
            results = []
            for item in p.rglob(pattern):
                if name_contains and name_contains.lower() not in item.name.lower():
                    continue
                results.append(str(item))
                if len(results) >= max_results:
                    break
            return ActionResult(success=True, data={"files": results, "count": len(results)})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetEnvironmentVariableAction(UFOBaseAction):
    """获取环境变量的值"""
    name = "get_environment_variable"
    description = "获取指定环境变量的值"
    parameters = [
        ActionParameter(name="name", type=ParameterType.STRING, description="环境变量名"),
    ]

    async def _execute(self, name: str) -> ActionResult:
        value = os.environ.get(name)
        return ActionResult(success=True, data={"name": name, "value": value, "exists": value is not None})


class SetEnvironmentVariableAction(UFOBaseAction):
    """设置环境变量的值"""
    name = "set_environment_variable"
    description = "设置环境变量的值（当前进程生效）"
    parameters = [
        ActionParameter(name="name", type=ParameterType.STRING, description="环境变量名"),
        ActionParameter(name="value", type=ParameterType.STRING, description="环境变量值"),
    ]

    async def _execute(self, name: str, value: str) -> ActionResult:
        os.environ[name] = value
        return ActionResult(success=True, data={"name": name, "value": value})


class GetSystemInfoAction(UFOBaseAction):
    """获取系统信息"""
    name = "get_system_info"
    description = "获取系统信息（操作系统、CPU、内存、磁盘等）"
    parameters = []

    async def _execute(self) -> ActionResult:
        try:
            import shutil

            info = {
                "os": platform.system(),
                "os_version": platform.version(),
                "os_release": platform.release(),
                "architecture": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "temp_dir": tempfile.gettempdir(),
                "user_home": os.path.expanduser("~"),
            }
            # 磁盘信息
            disk = shutil.disk_usage("/")
            info["disk_total_gb"] = round(disk.total / (1024 ** 3), 2)
            info["disk_used_gb"] = round(disk.used / (1024 ** 3), 2)
            info["disk_free_gb"] = round(disk.free / (1024 ** 3), 2)

            return ActionResult(success=True, data=info)
        except Exception as e:
            return ActionResult(success=False, error=str(e))
