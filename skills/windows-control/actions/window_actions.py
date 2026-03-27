#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
窗口操作 Actions
"""
import asyncio
from typing import Any, Dict, List, Optional

from loguru import logger

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)
from app.service.actions.system_actions import _run_system_command, _check_process_running
from app.service.utils.window import get_foreground_process_name, wait_for_target_window


class OpenAppAction(UFOBaseAction):
    """打开或切换到指定应用程序（自动检测进程、任务栏、系统托盘）"""
    name = "open_app"
    description = "打开或切换到指定应用程序（自动检测进程、任务栏、系统托盘）"
    parameters = [
        ActionParameter(name="app_name", type=ParameterType.STRING, description="应用程序名称"),
        ActionParameter(name="search_keyword", type=ParameterType.STRING, description="系统搜索关键词", required=False, default=""),
    ]

    async def _execute(self, app_name: str, search_keyword: str = "") -> ActionResult:
        result = _open_or_focus_app(app_name, search_keyword or None)
        metadata = {"app_action": result["action"], "detail": result["detail"]}
        if not result["success"]:
            return ActionResult(success=False, error=result["detail"], metadata=metadata)
        # 打开应用后等待窗口出现并验证前台窗口
        await asyncio.sleep(2)
        _fg_proc = get_foreground_process_name()
        _target_proc = app_name.lower()
        if _fg_proc and _target_proc:
            if _target_proc in _fg_proc or _fg_proc in _target_proc:
                logger.info(f"[{self.name}] 窗口验证通过: 前台进程 '{_fg_proc}' 匹配目标 '{_target_proc}'")
            else:
                logger.warning(f"[{self.name}] 窗口验证失败: 前台进程 '{_fg_proc}' 不匹配目标 '{_target_proc}'")
                _wait_ok, _, _ = await wait_for_target_window(process_name=_target_proc, timeout=3.0)
                if not _wait_ok:
                    metadata["detail"] += " (警告: 窗口验证未确认目标进程在前台)"
        return ActionResult(success=True, metadata=metadata)


# ==================== 内部工具函数 ====================

def _get_taskbar_apps() -> List[str]:
    """获取 Windows 任务栏中可见的应用窗口标题列表"""
    try:
        result = subprocess_run_ps(
            "(Get-Process | Where-Object {$_.MainWindowTitle -ne '' -and $_.ProcessName -ne 'explorer'} | "
            "Select-Object -ExpandProperty MainWindowTitle) | ConvertTo-Json -Depth 1"
        )
        titles = []
        if result.stdout.strip():
            import json
            try:
                data = json.loads(result.stdout.strip())
                if isinstance(data, list):
                    titles = [t for t in data if t]
                elif isinstance(data, str):
                    titles = [data]
            except json.JSONDecodeError:
                pass
        return titles
    except Exception:
        return []


def _get_tray_apps() -> List[str]:
    """获取 Windows 系统托盘中的后台应用名称列表"""
    try:
        result = subprocess_run_ps(
            "$shell = New-Object -ComObject Shell.Application; "
            "$tray = $shell.NameSpace('shell:Notification'); "
            "($tray.Items() | Select-Object -ExpandProperty Name) -join ', '"
        )
        names = []
        if result.stdout.strip():
            names = [n.strip() for n in result.stdout.strip().split(",") if n.strip()]
        return names
    except Exception:
        return []


def subprocess_run_ps(command: str, timeout: int = 10) -> Any:
    """执行 PowerShell 命令的快捷方式"""
    import subprocess
    # 强制 PowerShell 使用 UTF-8 输出编码，避免中文窗口标题乱码
    command = f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {command}"
    return subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True, text=True, timeout=timeout,
        encoding="utf-8", errors="replace"
    )


def _try_restore_process_window(app_name: str) -> Dict[str, Any]:
    """尝试从进程恢复/激活应用窗口"""
    activate_cmd = (
        f"$proc = (Get-Process | Where-Object {{$_.ProcessName -like '*{app_name}*'}} | Select-Object -First 1); "
        "if ($proc) { "
        "  try { "
        "    $hwnd = $proc.MainWindowHandle; "
        "    if ($hwnd -eq 0) { "
        "      Start-Process -FilePath $proc.Path; "
        "      'started_new_instance' "
        "    } else { "
        "      Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32Api { [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); public static extern bool SetForegroundWindow(IntPtr hWnd); }'; "
        "      [Win32Api]::ShowWindow($hwnd, 6); Start-Sleep -Milliseconds 400; "
        "      [Win32Api]::ShowWindow($hwnd, 9); Start-Sleep -Milliseconds 300; "
        "      [Win32Api]::SetForegroundWindow($hwnd); "
        "      'restored_and_activated' "
        "    } "
        "  } catch { 'activation_failed:' + $_.Exception.Message } "
        "} else { 'process_not_found' }"
    )
    result = _run_system_command(activate_cmd, shell="powershell")
    stdout = result.get("stdout", "").strip()
    logger.info(f"[open_app] 恢复窗口结果: {stdout}")

    if "restored_and_activated" in stdout:
        return {"success": True, "action": "restored_from_tray", "detail": f"应用 '{app_name}' 窗口已从后台恢复到前台"}
    elif "started_new_instance" in stdout:
        return {"success": True, "action": "started_new_instance", "detail": f"应用 '{app_name}' 进程在运行但无窗口句柄，已启动新实例"}

    # 最后手段：Start-Process 重新启动
    start_cmd = f"Start-Process -FilePath (Get-Process -Name '*{app_name}*' | Select-Object -First 1).Path"
    result = _run_system_command(start_cmd, shell="powershell", timeout=10)
    if result["success"]:
        return {"success": True, "action": "started_from_existing_process", "detail": f"应用 '{app_name}' 进程在运行，已尝试通过 Start-Process 重新启动"}

    return {"success": False, "action": "restore_failed", "detail": f"无法恢复应用 '{app_name}' 的窗口"}


def _try_launch_app(app_name: str, search: str) -> Dict[str, Any]:
    """通过快捷方式搜索、ms-search、常见安装路径等方式启动应用"""
    logger.info(f"[open_app] 方法A: 搜索开始菜单快捷方式 (keyword='{search}')")
    search_cmd = (
        f"Get-ChildItem -Path 'C:\\Users\\*\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu' -Recurse -Filter '*{search}*.lnk' -ErrorAction SilentlyContinue | "
        f"Select-Object -First 1 -ExpandProperty FullName"
    )
    result = _run_system_command(search_cmd, shell="powershell")
    if result["success"] and result["stdout"].strip():
        lnk_path = result["stdout"].strip()
        launch_result = _run_system_command(f"Start-Process '{lnk_path}'", shell="powershell")
        if launch_result["success"]:
            return {"success": True, "action": "launched_via_shortcut", "detail": f"通过快捷方式启动 '{search}' ({lnk_path})"}

    # 方法 B: ms-search
    logger.info(f"[open_app] 方法B: 使用 ms-search 启动 (keyword='{search}')")
    ms_cmd = f"Start-Process 'ms-search:{search}'"
    result = _run_system_command(ms_cmd, shell="powershell")
    if result["success"]:
        return {"success": True, "action": "launched_via_ms_search", "detail": f"通过 ms-search 启动 '{search}'"}

    # 方法 C: 常见安装路径
    logger.info(f"[open_app] 方法C: 常见安装路径搜索 (app='{app_name}')")
    common_paths = [
        f"C:\\Program Files\\*{app_name}*\\*.exe",
        f"C:\\Program Files (x86)\\*{app_name}*\\*.exe",
        f"C:\\Users\\*\\AppData\\Local\\*{app_name}*\\*.exe",
    ]
    for path_pattern in common_paths:
        find_cmd = f"(Get-Item -Path '{path_pattern}' -ErrorAction SilentlyContinue | Select-Object -First 1).FullName"
        result = _run_system_command(find_cmd, shell="powershell")
        if result["success"] and result["stdout"].strip():
            exe_path = result["stdout"].strip()
            launch_result = _run_system_command(f"Start-Process '{exe_path}'", shell="powershell")
            if launch_result["success"]:
                return {"success": True, "action": "launched_via_path", "detail": f"通过安装路径启动 '{exe_path}'"}

    return {"success": False, "action": "launch_failed", "detail": f"无法启动应用 '{app_name}'"}


def _open_or_focus_app(app_name: str, search_keyword: Optional[str] = None) -> Dict[str, Any]:
    """
    打开或聚焦到指定应用程序

    执行流程（按优先级依次检测）:
    1. 任务栏可见窗口: 检查是否有可见窗口 → 激活前置
    2. 系统托盘: 检查底部右侧托盘区域 → 从托盘恢复窗口
    3. 进程检测: 检查进程是否运行 → 尝试唤出或启动新实例
    4. 系统搜索: 搜索快捷方式 → ms-search → 常见安装路径
    """
    search = search_keyword or app_name
    app_lower = app_name.lower()
    search_lower = search.lower()

    # 步骤 1: 检查任务栏可见窗口
    logger.info(f"[open_app] 步骤1/4: 检查任务栏可见窗口 (app='{app_name}')")
    window_titles = _get_taskbar_apps()
    logger.info(f"[open_app] 任务栏可见窗口 ({len(window_titles)}): {window_titles[:10]}")

    matched_title = None
    for title in window_titles:
        if app_lower in title.lower() or search_lower in title.lower():
            matched_title = title
            break

    if matched_title:
        logger.info(f"[open_app] 在任务栏找到匹配窗口: '{matched_title}'，尝试激活前置")
        cmd = (
            f"$w = (Get-Process | Where-Object {{$_.ProcessName -like '*{app_name}*' -and $_.MainWindowTitle -ne ''}} | "
            f"Select-Object -First 1); "
            f"if ($w) {{ (New-Object -ComObject WScript.Shell).AppActivate($w.MainWindowTitle); 'activated' }} "
            f"else {{ 'no_window' }}"
        )
        result = _run_system_command(cmd, shell="powershell")
        if "activated" in result.get("stdout", ""):
            return {"success": True, "action": "activated_existing_window", "detail": f"应用 '{app_name}' 在任务栏有可见窗口 '{matched_title}'，已激活前置"}
        logger.warning(f"[open_app] 步骤1 激活失败，继续下一步...")

    # 步骤 2: 检查系统托盘
    logger.info(f"[open_app] 步骤2/4: 检查系统托盘区域 (app='{app_name}')")
    tray_apps = _get_tray_apps()
    matched_tray = None
    for tray_name in tray_apps:
        if app_lower in tray_name.lower() or search_lower in tray_name.lower():
            matched_tray = tray_name
            break
    if matched_tray:
        process_info = _check_process_running(app_name)
        if process_info["running"]:
            restore_result = _try_restore_process_window(app_name)
            if restore_result["success"]:
                restore_result["detail"] = f"应用 '{app_name}' 在系统托盘 '{matched_tray}' 运行，已从后台恢复到前台"
                return restore_result
        logger.warning(f"[open_app] 步骤2 恢复失败，继续下一步...")

    # 步骤 3: 检查进程中是否运行
    logger.info(f"[open_app] 步骤3/4: 检查进程列表 (app='{app_name}')")
    process_info = _check_process_running(app_name)
    if process_info["running"]:
        restore_result = _try_restore_process_window(app_name)
        if restore_result["success"]:
            return restore_result
        logger.warning(f"[open_app] 步骤3 唤出失败，继续下一步...")

    # 步骤 4: 通过系统搜索启动应用
    logger.info(f"[open_app] 步骤4/4: 系统搜索并启动应用 (keyword='{search}')")
    launch_result = _try_launch_app(app_name, search)
    if launch_result["success"]:
        return launch_result

    logger.error(f"[open_app] 所有步骤均失败，无法打开应用 '{app_name}'")
    return {"success": False, "action": "failed", "detail": f"无法启动应用 '{app_name}'，请确认应用名称正确或手动启动"}
