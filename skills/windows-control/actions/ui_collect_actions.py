#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI 采集 Actions

提供窗口 UI 树、截图、控件信息等采集能力。
参考 UFO 的 UICollector (ui_mcp_server.py) 和 Host Agent 策略。
"""
import asyncio
import ctypes
import ctypes.wintypes
from typing import Any, Dict, List, Optional

from loguru import logger

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)

# ==================== Win32 常量 ====================
USER32 = ctypes.windll.user32
GDI32 = ctypes.windll.gdi32

SW_RESTORE = 9
SW_SHOW = 5
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E


def _enum_windows_proc(hwnd, results: list):
    """EnumWindows 回调: 收集所有可见窗口"""
    if USER32.IsWindowVisible(hwnd):
        length = USER32.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            USER32.SendMessageW(hwnd, WM_GETTEXT, length + 1, buf)
            title = buf.value.strip()
            if title:
                _, pid = ctypes.wintypes.DWORD(), ctypes.wintypes.DWORD()
                USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid), ctypes.byref(_))
                try:
                    exe_path = _get_process_exe(pid.value)
                    exe_name = exe_path.rsplit("\\", 1)[-1] if exe_path else ""
                except Exception:
                    exe_name = ""
                # 排除系统进程
                if exe_name and exe_name.lower() not in (
                    "explorer.exe", "searchhost.exe", "shellexperiencehost.exe",
                    "taskmgr.exe", "applicationframehost.exe",
                ):
                    rect = ctypes.wintypes.RECT()
                    USER32.GetWindowRect(hwnd, ctypes.byref(rect))
                    results.append({
                        "hwnd": hwnd,
                        "title": title,
                        "exe": exe_name,
                        "pid": pid.value,
                        "left": rect.left,
                        "top": rect.top,
                        "right": rect.right,
                        "bottom": rect.bottom,
                        "width": rect.right - rect.left,
                        "height": rect.bottom - rect.top,
                    })


def _get_process_exe(pid: int) -> str:
    """通过 PID 获取进程可执行文件路径"""
    import subprocess
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"(Get-Process -Id {pid}).Path"],
            capture_output=True, text=True, timeout=5,
            encoding="utf-8", errors="replace",
        )
        return result.stdout.strip()
    except Exception:
        return ""


# ==================== Action 类 ====================

class GetDesktopAppInfoAction(UFOBaseAction):
    """获取桌面上所有应用程序窗口信息"""
    name = "get_desktop_app_info"
    description = "获取桌面上所有可见应用程序窗口信息（标题、进程名、位置、大小）"
    parameters = []

    async def _execute(self) -> ActionResult:
        results = []
        WMENUM = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        USER32.EnumWindows(WMENUM(_enum_windows_proc), 0)
        # 使用回调收集
        callback = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        USER32.EnumWindows(callback(_enum_windows_proc), 0)
        # 直接收集方式
        apps = []
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

        def _collect(hwnd, _lparam):
            if USER32.IsWindowVisible(hwnd):
                length = USER32.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    USER32.SendMessageW(hwnd, WM_GETTEXT, length + 1, buf)
                    title = buf.value.strip()
                    if title:
                        _, pid = ctypes.wintypes.DWORD(), ctypes.wintypes.DWORD()
                        USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid), ctypes.byref(_))
                        rect = ctypes.wintypes.RECT()
                        USER32.GetWindowRect(hwnd, ctypes.byref(rect))
                        apps.append({
                            "hwnd": int(hwnd),
                            "title": title,
                            "pid": int(pid.value),
                            "left": rect.left, "top": rect.top,
                            "right": rect.right, "bottom": rect.bottom,
                            "width": rect.right - rect.left,
                            "height": rect.bottom - rect.top,
                        })
            return True

        USER32.EnumWindows(WNDENUMPROC(_collect), 0)
        return ActionResult(success=True, data={"apps": apps, "count": len(apps)})


class GetDesktopAppTargetInfoAction(UFOBaseAction):
    """获取桌面应用的 TargetInfo 格式信息（用于 Host Agent 选择窗口）"""
    name = "get_desktop_app_target_info"
    description = "获取桌面应用 TargetInfo 格式信息（id, name, 用于 Host Agent 选择窗口）"
    parameters = []

    async def _execute(self) -> ActionResult:
        apps = []
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

        def _collect(hwnd, _lparam):
            if USER32.IsWindowVisible(hwnd):
                length = USER32.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    USER32.SendMessageW(hwnd, WM_GETTEXT, length + 1, buf)
                    title = buf.value.strip()
                    if title:
                        _, pid = ctypes.wintypes.DWORD(), ctypes.wintypes.DWORD()
                        USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid), ctypes.byref(_))
                        exe = _get_process_exe(pid.value)
                        exe_name = exe.rsplit("\\", 1)[-1].replace(".exe", "") if exe else ""
                        if exe_name and exe_name.lower() not in ("explorer", "searchhost"):
                            apps.append({
                                "id": str(hwnd),
                                "name": title,
                                "process_name": exe_name,
                            })
            return True

        USER32.EnumWindows(WNDENUMPROC(_collect), 0)
        return ActionResult(success=True, data={"targets": apps, "count": len(apps)})


class CaptureWindowScreenshotAction(UFOBaseAction):
    """截取当前活动窗口的截图"""
    name = "capture_window_screenshot"
    description = "截取当前活动窗口的截图并返回图片数据"
    parameters = []

    async def _execute(self) -> ActionResult:
        try:
            from app.service.utils.screenshot import capture_screenshot, crop_to_active_window
            img, _, _ = capture_screenshot(label="window_capture")
            if img:
                import base64
                from io import BytesIO
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                return ActionResult(success=True, data={
                    "screenshot_base64": img_b64,
                    "width": img.width,
                    "height": img.height,
                })
            return ActionResult(success=False, error="截图失败")
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class CaptureDesktopScreenshotAction(UFOBaseAction):
    """截取整个桌面的截图"""
    name = "capture_desktop_screenshot"
    description = "截取整个桌面的截图并返回图片数据"
    parameters = []

    async def _execute(self) -> ActionResult:
        try:
            from app.service.utils.screenshot import capture_screenshot
            img, _, _ = capture_screenshot(label="desktop_capture", full_desktop=True)
            if img:
                import base64
                from io import BytesIO
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                return ActionResult(success=True, data={
                    "screenshot_base64": img_b64,
                    "width": img.width,
                    "height": img.height,
                })
            return ActionResult(success=False, error="截图失败")
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetUITreeAction(UFOBaseAction):
    """获取当前窗口的 UI 控件树"""
    name = "get_ui_tree"
    description = "获取当前窗口的 UI 控件树（XML 格式），使用 UIAutomation API"
    parameters = [
        ActionParameter(name="max_depth", type=ParameterType.INTEGER,
                         description="最大遍历深度", required=False, default=10),
    ]

    async def _execute(self, max_depth: int = 10) -> ActionResult:
        try:
            import subprocess
            # 使用 PowerShell 的 UIAutomation 模块获取控件树
            ps_script = """
$root = [System.Windows.Automation.AutomationElement]::RootElement
$treeWalker = [System.Windows.Automation.TreeWalker]::ControlViewWalker

function Get-UIElement {
    param($element, $depth, $maxDepth)
    if ($depth -gt $maxDepth) { return }
    $current = $element.Current
    $name = if ($current.Name) { $current.Name.Substring(0, [Math]::Min($current.Name.Length, 80)) } else { "" }
    $className = if ($current.ClassName) { $current.ClassName } else { "" }
    $controlType = $current.ControlType.ProgrammaticName
    $automationId = if ($current.AutomationId) { $current.AutomationId } else { "" }
    $isEnabled = $current.IsEnabled
    $indent = "  " * $depth

    # 过滤掉无意义的控件
    if ($controlType -notin @("Pane", "Window", "ScrollBar", "Thumb")) {
        $node = "$indent<Control Name=`"$name`" ClassName=`"$className`" ControlType=`"$controlType`" AutomationId=`"$automationId`" Enabled=`"$isEnabled`" />"
        $node
    }

    $child = $treeWalker.GetFirstChild($element)
    while ($child -ne $null) {
        Get-UIElement -element $child -depth ($depth + 1) -maxDepth $maxDepth
        $child = $treeWalker.GetNextSibling($child)
    }
}

# 找到前台窗口
$foreground = [System.Windows.Automation.AutomationElement]::FromHandle((Get-Process | Where-Object {$_.MainWindowHandle -ne 0} | Sort-Object -Property MainWindowHandle -Descending | Select-Object -First 1).MainWindowHandle)
if ($foreground) {
    Get-UIElement -element $foreground -depth 0 -maxDepth $maxDepth
}
"""
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, text=True, timeout=15,
                encoding="utf-8", errors="replace",
            )
            ui_tree = result.stdout.strip()
            if not ui_tree:
                return ActionResult(success=False, error="无法获取 UI 树，可能前台窗口无 UIAutomation 支持")

            # 计算 XML 行数
            line_count = len(ui_tree.split("\n"))
            return ActionResult(success=True, data={
                "ui_tree": ui_tree,
                "line_count": line_count,
                "format": "xml",
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetAppWindowInfoAction(UFOBaseAction):
    """获取当前活动窗口的详细信息"""
    name = "get_app_window_info"
    description = "获取当前活动窗口的详细信息（标题、类名、位置、大小、进程等）"
    parameters = []

    async def _execute(self) -> ActionResult:
        try:
            hwnd = USER32.GetForegroundWindow()
            if not hwnd:
                return ActionResult(success=False, error="无前台窗口")

            length = USER32.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0)
            buf = ctypes.create_unicode_buffer(length + 1)
            USER32.SendMessageW(hwnd, WM_GETTEXT, length + 1, buf)

            rect = ctypes.wintypes.RECT()
            USER32.GetWindowRect(hwnd, ctypes.byref(rect))

            _, pid = ctypes.wintypes.DWORD(), ctypes.wintypes.DWORD()
            USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid), ctypes.byref(_))

            # 获取窗口类名
            class_buf = ctypes.create_unicode_buffer(256)
            USER32.GetClassNameW(hwnd, class_buf, 256)

            exe_path = _get_process_exe(pid.value)

            return ActionResult(success=True, data={
                "hwnd": int(hwnd),
                "title": buf.value,
                "class_name": class_buf.value,
                "pid": int(pid.value),
                "exe_path": exe_path,
                "left": rect.left, "top": rect.top,
                "right": rect.right, "bottom": rect.bottom,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top,
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetAppWindowControlsInfoAction(UFOBaseAction):
    """获取当前窗口所有 UI 控件信息"""
    name = "get_app_window_controls_info"
    description = "获取当前窗口所有可交互 UI 控件的列表（名称、类型、位置、类名、AutomationId）"
    parameters = [
        ActionParameter(name="max_depth", type=ParameterType.INTEGER,
                         description="最大遍历深度", required=False, default=8),
    ]

    async def _execute(self, max_depth: int = 8) -> ActionResult:
        try:
            import subprocess
            ps_script = """
$root = [System.Windows.Automation.AutomationElement]::RootElement
$treeWalker = [System.Windows.Automation.TreeWalker]::ControlViewWalker

$controls = @()

function Collect-Controls {
    param($element, $depth, $maxDepth)
    if ($depth -gt $maxDepth) {{ return }}
    $current = $element.Current
    $name = if ($current.Name) {{ $current.Name }} else {{ "" }}
    $controlType = $current.ControlType.ProgrammaticName

    # 跳过无意义的容器控件
    $skip = @("Pane", "ScrollBar", "Thumb", "Separator", "Image")
    if ($controlType -notin $skip -and $name) {{
        $rect = $current.BoundingRectangle
        $controlInfo = @{{
            "name" = $name.Substring(0, [Math]::Min($name.Length, 100));
            "control_type" = $controlType;
            "class_name" = $current.ClassName;
            "automation_id" = $current.AutomationId;
            "is_enabled" = $current.IsEnabled;
            "is_visible" = (-not $current.IsOffscreen);
        }}
        if ($rect) {{
            $controlInfo["left"] = [int]$rect.X
            $controlInfo["top"] = [int]$rect.Y
            $controlInfo["width"] = [int]$rect.Width
            $controlInfo["height"] = [int]$rect.Height
        }}
        $controls += ,$controlInfo
    }}

    $child = $treeWalker.GetFirstChild($element)
    while ($child -ne $null) {{
        Collect-Controls -element $child -depth ($depth + 1) -maxDepth $maxDepth
        $child = $treeWalker.GetNextSibling($child)
    }}
}}

$foreground = [System.Windows.Automation.AutomationElement]::FromHandle((Get-Process | Where-Object {{$_.MainWindowHandle -ne 0}} | Sort-Object -Property MainWindowHandle -Descending | Select-Object -First 1).MainWindowHandle)
if ($foreground) {{
    Collect-Controls -element $foreground -depth 0 -maxDepth """ + str(max_depth) + """
    $controls | ConvertTo-Json -Depth 3
}}
"""
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, text=True, timeout=15,
                encoding="utf-8", errors="replace",
            )
            import json
            output = result.stdout.strip()
            if output:
                try:
                    controls = json.loads(output)
                    return ActionResult(success=True, data={
                        "controls": controls if isinstance(controls, list) else [controls],
                        "count": len(controls) if isinstance(controls, list) else 1,
                    })
                except json.JSONDecodeError:
                    return ActionResult(success=True, data={"controls": [], "count": 0, "raw": output})
            return ActionResult(success=False, error="无法获取控件信息")
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class GetAppWindowControlsTargetInfoAction(UFOBaseAction):
    """获取窗口控件树并以 TargetInfo 格式返回"""
    name = "get_app_window_controls_target_info"
    description = "获取窗口控件树并以 TargetInfo 格式返回（id, name, 用于 App Agent 操作控件）"
    parameters = [
        ActionParameter(name="max_depth", type=ParameterType.INTEGER,
                         description="最大遍历深度", required=False, default=8),
    ]

    async def _execute(self, max_depth: int = 8) -> ActionResult:
        try:
            # 复用 GetAppWindowControlsInfoAction 获取控件
            ctrl_action = GetAppWindowControlsInfoAction()
            ctrl_action._screenshot_scale = self._screenshot_scale
            ctrl_action._screen_size = self._screen_size
            ctrl_result = await ctrl_action.execute(max_depth=max_depth)

            if not ctrl_result.success:
                return ActionResult(success=False, error=ctrl_result.error)

            controls = ctrl_result.data.get("controls", [])
            # 转换为 TargetInfo 格式
            targets = []
            for i, ctrl in enumerate(controls):
                targets.append({
                    "id": str(i),
                    "name": ctrl.get("name", ""),
                    "control_type": ctrl.get("control_type", ""),
                    "class_name": ctrl.get("class_name", ""),
                    "automation_id": ctrl.get("automation_id", ""),
                    "is_enabled": ctrl.get("is_enabled", True),
                    "is_visible": ctrl.get("is_visible", True),
                    "left": ctrl.get("left", 0),
                    "top": ctrl.get("top", 0),
                    "width": ctrl.get("width", 0),
                    "height": ctrl.get("height", 0),
                })
            return ActionResult(success=True, data={"targets": targets, "count": len(targets)})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class AddControlListAction(UFOBaseAction):
    """手动添加控件列表到控制字典中"""
    name = "add_control_list"
    description = "手动添加控件信息到内部控件列表中，用于补充 UIAutomation 无法识别的控件"
    parameters = [
        ActionParameter(name="controls", type=ParameterType.ARRAY,
                         description="控件信息列表，每个控件包含 name, control_type, left, top, width, height"),
    ]

    async def _execute(self, controls: list = None) -> ActionResult:
        if not controls:
            return ActionResult(success=False, error="controls 参数不能为空")
        # 在单次会话中存储控件列表
        if not hasattr(self, "_stored_controls"):
            self._stored_controls = []
        self._stored_controls.extend(controls)
        return ActionResult(success=True, data={
            "added_count": len(controls),
            "total_count": len(self._stored_controls),
        })
