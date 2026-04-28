#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows Session 检测与迁移工具

解决 jingmai-cli 在 Session 0 运行时无法操作 Session 1 GUI 的问题。
提供 Session 检测、进程查找、Session 迁移等能力。
"""
import ctypes
import ctypes.wintypes
import os
import subprocess
from typing import Optional

from loguru import logger


class SessionDetector:
    """
    Windows Session 检测与迁移工具。

    用法：
        detector = SessionDetector()
        current = detector.detect_current_session()
        if current == 0:
            detector.try_migrate_to_interactive_session()
    """

    def detect_current_session(self) -> int:
        """
        返回当前进程所在的 Session ID。

        使用 Win32 API ProcessIdToSessionId 获取。

        Returns:
            int: Session ID（失败时返回 -1）
        """
        try:
            pid = os.getpid()
            session_id = ctypes.wintypes.DWORD()
            result = ctypes.windll.kernel32.ProcessIdToSessionId(
                pid, ctypes.byref(session_id)
            )
            if result:
                return session_id.value
            logger.warning(f"ProcessIdToSessionId 失败, pid={pid}")
            return -1
        except Exception as e:
            logger.error(f"检测当前 Session 失败: {e}")
            return -1

    def find_interactive_session(self) -> Optional[int]:
        """
        找到有用户桌面的交互式 Session ID。

        通过 `query session` 命令查找状态为 Active 的 Session。

        Returns:
            Optional[int]: 交互式 Session ID（通常是 1），失败返回 None
        """
        try:
            result = subprocess.run(
                ["query", "session"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                logger.warning(f"query session 失败: {result.stderr}")
                return None

            for line in result.stdout.strip().split("\n"):
                # 典型输出格式：
                #  SESSIONNAME       USERNAME        ID  STATE   TYPE
                # >rdp-tcp#0         Administrator   1   Active  rdpwd
                #  services                          0   Disc
                parts = line.split()
                if "Active" in parts:
                    try:
                        active_idx = parts.index("Active")
                        if active_idx >= 1:
                            session_id = int(parts[active_idx - 1])
                            logger.info(f"找到交互式 Session: {session_id}")
                            return session_id
                    except (ValueError, IndexError):
                        continue
            logger.warning("未找到 Active 状态的 Session")
            return None
        except FileNotFoundError:
            logger.warning("query 命令不可用（非 Windows Server / RDP 环境）")
            return None
        except Exception as e:
            logger.error(f"查找交互式 Session 失败: {e}")
            return None

    def find_process_session(self, process_name: str) -> Optional[int]:
        """
        查找指定进程所在的 Session ID。

        Args:
            process_name: 进程名，如 "Jingmai.exe"

        Returns:
            Optional[int]: Session ID，进程不存在返回 None
        """
        try:
            result = subprocess.run(
                ["tasklist", "/V", "/FI", f"IMAGENAME eq {process_name}", "/FO", "CSV"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return None

            lines = result.stdout.strip().split("\n")
            if len(lines) < 2:
                return None

            # CSV 格式：
            # "Image Name","PID","Session Name","Session#","Mem Usage","Status","User Name","CPU Time","Window Title"
            for line in lines[1:]:  # 跳过表头
                parts = line.strip().strip('"').split('","')
                if len(parts) >= 4:
                    try:
                        session_id = int(parts[3])
                        return session_id
                    except (ValueError, IndexError):
                        continue
            return None
        except Exception as e:
            logger.error(f"查找进程 Session 失败 ({process_name}): {e}")
            return None

    def is_same_session_as_process(self, process_name: str) -> bool:
        """
        判断当前进程与目标进程是否在同一 Session。

        Args:
            process_name: 目标进程名

        Returns:
            bool: 是否在同一 Session
        """
        target = self.find_process_session(process_name)
        if target is None:
            return False
        return target == self.detect_current_session()

    def try_migrate_to_interactive_session(self) -> bool:
        """
        尝试将当前进程迁移到交互式 Session。

        通过 schtasks 创建一次性计划任务在 Session 1 执行，然后退出当前进程。

        Returns:
            bool: 是否成功发起迁移（注意：当前进程会退出）
        """
        try:
            interactive = self.find_interactive_session()
            if interactive is None:
                logger.warning("无法找到交互式 Session，迁移失败")
                return False

            # 重新构建当前命令行，在目标 Session 执行
            import sys
            cmd = " ".join([f'"{sys.executable}"'] + [f'"{a}"' for a in sys.argv])

            # 使用 schtasks 在目标 Session 创建一次性任务
            task_name = f"jingmai_session_migrate_{os.getpid()}"
            create_result = subprocess.run(
                [
                    "schtasks", "/Create",
                    "/TN", task_name,
                    "/TR", cmd,
                    "/SC", "ONCE",
                    "/ST", "00:00",
                    "/RU", os.getenv("USERNAME", "Administrator"),
                    "/IT",  # 仅在用户登录时运行（交互式 Session）
                    "/F",   # 强制覆盖
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if create_result.returncode != 0:
                logger.warning(f"schtasks 创建失败: {create_result.stderr}")
                return False

            # 立即运行任务
            run_result = subprocess.run(
                ["schtasks", "/Run", "/TN", task_name],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if run_result.returncode != 0:
                logger.warning(f"schtasks 运行失败: {run_result.stderr}")
                return False

            logger.info(f"已在 Session {interactive} 启动新进程，当前进程将退出")

            # 清理计划任务
            subprocess.run(
                ["schtasks", "/Delete", "/TN", task_name, "/F"],
                capture_output=True,
                timeout=10,
            )

            # 退出当前进程
            os._exit(0)

        except Exception as e:
            logger.error(f"Session 迁移失败: {e}")
            return False

    def try_launch_in_target_session(self, exe_path: str, session_id: int) -> bool:
        """
        在指定 Session 启动目标程序。

        Args:
            exe_path: 可执行文件路径或名称
            session_id: 目标 Session ID

        Returns:
            bool: 是否成功启动
        """
        try:
            # 方案 1：直接在当前 Session 启动（如果进程不存在）
            # 如果当前 Session 就是目标 Session，直接 start
            current = self.detect_current_session()
            if current == session_id:
                subprocess.Popen(
                    ["start", "", exe_path],
                    shell=True,
                )
                logger.info(f"在当前 Session ({session_id}) 启动 {exe_path}")
                return True

            # 方案 2：通过 schtasks 在目标 Session 启动
            task_name = f"launch_{exe_path.replace('.', '_')}_{os.getpid()}"
            subprocess.run(
                [
                    "schtasks", "/Create",
                    "/TN", task_name,
                    "/TR", exe_path,
                    "/SC", "ONCE",
                    "/ST", "00:00",
                    "/RU", os.getenv("USERNAME", "Administrator"),
                    "/IT",
                    "/F",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            result = subprocess.run(
                ["schtasks", "/Run", "/TN", task_name],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # 清理
            subprocess.run(
                ["schtasks", "/Delete", "/TN", task_name, "/F"],
                capture_output=True,
                timeout=10,
            )

            if result.returncode == 0:
                logger.info(f"已在 Session {session_id} 启动 {exe_path}")
                return True
            else:
                logger.warning(f"在 Session {session_id} 启动 {exe_path} 失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"启动 {exe_path} 到 Session {session_id} 失败: {e}")
            return False
