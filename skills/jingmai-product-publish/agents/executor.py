"""
京麦商品发布自动化 - Executor Agent (ReAct 执行循环)

三种经典范式协同工作（参考 DataWhale Hello-Agents 第四章）:
  ┌─────────────────────────────────────────────────────────────┐
  │ Plan-and-Solve: plan 命令生成结构化执行计划                    │
  │     ↓                                                       │
  │ ReAct: execute 命令逐步执行，每步完整循环:                     │
  │   Act(执行) → Screenshot(截图) → Observe(视觉分析) → Reflect │
  │     ↓                                                       │
  │ Reflection: 失败时递进式重试（3级: 直接重试→退避→清缓存重定位） │
  └─────────────────────────────────────────────────────────────┘

每一步的执行流程:
  1. Act: 执行动作
  2. Screenshot: 截图当前窗口
  3. Observe: LLM 视觉分析截图，判断操作是否成功
  4. Reflect: 根据观察结果决定重试或继续
  5. 成功 → 标记步骤完成 → 更新计划文件 → 执行下一步
  6. 失败 → 递进重试最多 3 次 → 仍失败则中止

验证降级策略（三级）:
  1. LLM 可用 → 截图 + LLM 视觉分析
  2. LLM 不可用 → 信任 action_result 的 success 字段
  3. 截图失败 → 标记 "未验证" 但不阻断
"""
import json
import random
import time
from typing import Any, Callable, Dict, List, Optional

from actions import ActionRegistry
from agents.base import BaseAgent


# 递进式重试最大次数
REACT_MAX_RETRIES = 3


class ExecutorAgent(BaseAgent):
    """执行 Agent — ReAct 循环（每步截图 + 视觉验证 + 递进重试）"""

    def __init__(self, settings=None):
        super().__init__(name="Executor", settings=settings)
        self._locator = None
        self._task_id = ""
        self._plan_file = ""           # 计划文件路径（用于实时更新步骤状态）
        self._original_plan_data = {}   # 原始计划数据（保留 task_id 等元信息）
        self._on_progress: Optional[Callable] = None  # CLI 进度回调
        self._last_recovery_error = ""
        self._recovery_attempts: Dict[int, List[Dict[str, Any]]] = {}
        self._risk_stats: Dict[str, Any] = {}
        self._vision_fallback_stats: Dict[str, Any] = {}

    def run(self, plan: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        self._task_id = kwargs.get("task_id", "")
        self._plan_file = kwargs.get("plan_file", "")
        self._original_plan_data = kwargs.get("original_plan_data", {})
        self._on_progress = kwargs.get("on_progress")
        self._resume_step_index = max(0, int(kwargs.get("resume_step_index", 0) or 0))
        self._last_recovery_error = ""
        self._recovery_attempts = {}
        self._risk_stats = {
            "high_risk_window_shift_count": 0,
            "high_risk_window_shift_steps": [],
        }
        self._vision_fallback_stats = {
            "count": 0,
            "success_count": 0,
            "failed_count": 0,
            "steps": [],
            "failed_details": [],
            "templates": {},
            "templates_success": {},
            "templates_failed": {},
        }

        if self._db and self._task_id:
            self._db.update_task_status(self._task_id, "running")

        # 使用 ReAct 循环（每步 Act→Screenshot→Observe→Reflect）
        result = self.run_react_loop(plan, **kwargs)

        if self._db and self._task_id:
            if result.get("success"):
                self._db.update_task_status(self._task_id, "success", result=result)
            else:
                self._db.update_task_status(
                    self._task_id,
                    "failed",
                    error=result.get("error", ""),
                    result=result,
                )
        self._finalize_plan_file(
            plan=plan,
            success=bool(result.get("success")),
            failed_step=result.get("failed_step"),
            error=result.get("error", ""),
        )
        result["risk_stats"] = dict(self._risk_stats)
        result["vision_fallback_stats"] = dict(self._vision_fallback_stats)
        result["recovery_error"] = self._last_recovery_error
        return result

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executor 保持规则驱动，只回传当前动作。"""
        action_name = context.get("action", "")
        memory_hints = []
        if self._memory and action_name:
            try:
                memory_hints = self._recall(f"步骤 {action_name}", top_k=2)
            except Exception:
                memory_hints = []

        return {
            "next_action": action_name,
            "reason": "rule-driven executor",
            "confidence": 0.9 if not memory_hints else 0.7,
        }

    def act(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if self._db and self._task_id:
            self._db.update_step_status(self._task_id, self.state.step_index - 1, "running")

        action_params = dict(params)
        if "locator" not in action_params and self._locator is not None:
            action_params["locator"] = self._locator
        if "log" not in action_params and self._logger is not None:
            action_params["log"] = self._logger
        if self._logger and params:
            self._logger.debug(f"[Executor] 执行参数 {action_name}: {params}")

        result = ActionRegistry.execute(action_name, **action_params)
        if isinstance(result, dict):
            vision_meta = self._extract_vision_fallback(result)
            if vision_meta:
                result["used_vision_fallback"] = True
                result["vision_fallback"] = vision_meta

        # 窗口类动作成功后初始化 locator
        if action_name in {"find_window", "activate_window"} and result.get("success"):
            if self._locator is None:
                from infrastructure.locator import JingmaiLocator

                self._locator = JingmaiLocator(log=self._logger)
                self._locator.find_window()

        return result

    def _extract_vision_fallback(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        vision_meta = result.get("vision_fallback")
        if isinstance(vision_meta, dict) and vision_meta.get("success"):
            return vision_meta

        method = str(result.get("method", "") or "").lower()
        if "vision" in method:
            return {
                "success": True,
                "template": "",
                "template_path": "",
                "match_confidence": None,
            }
        return None

    def _record_vision_fallback(
        self,
        step_index: int,
        action_name: str,
        act_result: Optional[Dict[str, Any]],
        step_success: bool,
    ):
        vision_meta = self._extract_vision_fallback(act_result or {})
        if not vision_meta:
            return

        template_name = str(vision_meta.get("template", "") or "")
        self._vision_fallback_stats["count"] += 1
        if step_success:
            self._vision_fallback_stats["success_count"] += 1
        else:
            self._vision_fallback_stats["failed_count"] += 1
        self._vision_fallback_stats["steps"].append(
            {
                "step": step_index,
                "action": action_name,
                "template": template_name,
                "template_path": vision_meta.get("template_path", ""),
                "success": step_success,
                "screenshot": str((act_result or {}).get("screenshot", "") or ""),
            }
        )
        if template_name:
            self._vision_fallback_stats["templates"][template_name] = (
                self._vision_fallback_stats["templates"].get(template_name, 0) + 1
            )
            bucket = "templates_success" if step_success else "templates_failed"
            self._vision_fallback_stats[bucket][template_name] = (
                self._vision_fallback_stats[bucket].get(template_name, 0) + 1
            )
        if not step_success:
            original_screenshot = str((act_result or {}).get("screenshot", "") or "")
            archived_screenshot = self._archive_failed_vision_screenshot(
                step_index=step_index,
                action_name=action_name,
                template_name=template_name,
                screenshot_path=original_screenshot,
            )
            detail = {
                "task_id": self._task_id or "",
                "step": step_index,
                "action": action_name,
                "template": template_name,
                "template_path": vision_meta.get("template_path", ""),
                "screenshot": archived_screenshot or original_screenshot,
                "original_screenshot": original_screenshot,
                "error": str((act_result or {}).get("error", "") or ""),
            }
            self._vision_fallback_stats["failed_details"].append(detail)
            self._update_failed_vision_indexes(detail)

    def _archive_failed_vision_screenshot(
        self,
        step_index: int,
        action_name: str,
        template_name: str,
        screenshot_path: str,
    ) -> str:
        if not screenshot_path:
            return ""

        try:
            import re
            import shutil
            from pathlib import Path

            source = Path(screenshot_path)
            if not source.exists():
                return ""

            task_slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", self._task_id or "unknown-task").strip("_") or "unknown-task"
            action_slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", action_name or "action").strip("_") or "action"
            template_slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", template_name or "unknown-template").strip("_") or "unknown-template"

            archive_dir = Path("data") / "vision-fallback-failures" / task_slug
            archive_dir.mkdir(parents=True, exist_ok=True)
            target = archive_dir / f"step-{step_index:02d}_{action_slug}_{template_slug}{source.suffix or '.png'}"
            shutil.copyfile(source, target)
            return str(target.resolve())
        except Exception:
            return ""

    def _update_failed_vision_indexes(self, detail: Dict[str, Any]):
        try:
            import re
            from pathlib import Path

            task_slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", self._task_id or "unknown-task").strip("_") or "unknown-task"
            root_dir = Path("data") / "vision-fallback-failures"
            task_dir = root_dir / task_slug
            task_dir.mkdir(parents=True, exist_ok=True)

            summary_path = task_dir / "summary.json"
            index_path = root_dir / "index.json"

            summary_payload = self._load_index_payload(summary_path, default={"task_id": self._task_id or "", "items": []})
            summary_payload["task_id"] = self._task_id or ""
            summary_payload["items"] = self._upsert_failed_vision_detail(summary_payload.get("items", []), detail)
            summary_payload["count"] = len(summary_payload["items"])
            summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2), encoding="utf-8")

            index_payload = self._load_index_payload(index_path, default={"items": []})
            index_payload["items"] = self._upsert_failed_vision_detail(index_payload.get("items", []), detail)
            index_payload["count"] = len(index_payload["items"])
            index_path.write_text(json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            return

    def _load_index_payload(self, path, default: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return dict(default)

    def _upsert_failed_vision_detail(self, items: List[Dict[str, Any]], detail: Dict[str, Any]) -> List[Dict[str, Any]]:
        key = (
            str(detail.get("task_id", "")),
            int(detail.get("step", 0) or 0),
            str(detail.get("action", "")),
            str(detail.get("template", "")),
        )

        normalized = []
        replaced = False
        for item in items:
            item_key = (
                str(item.get("task_id", "")),
                int(item.get("step", 0) or 0),
                str(item.get("action", "")),
                str(item.get("template", "")),
            )
            if item_key == key:
                normalized.append(dict(detail))
                replaced = True
            else:
                normalized.append(item)

        if not replaced:
            normalized.append(dict(detail))
        return normalized

    # ── ReAct 执行循环 ─────────────────────────────

    def run_react_loop(self, plan: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        ReAct 执行主循环 — 每步 Act → Screenshot → Observe → Reflect

        参考 DataWhare Hello-Agents 第四章:
          - ReAct (4.2): Thought→Action→Observation 动态循环
          - Plan-and-Solve (4.3): 按计划逐步执行，历史结果传递给后续步骤
          - Reflection (4.4): 执行→反思→优化，递进重试

        流程:
          对计划中的每一步:
            1. Act: 执行动作
            2. Screenshot: 截图当前窗口
            3. Observe: LLM 视觉分析截图（ReAct Observation）
            4. Reflect: 判断成功/失败（Reflection）
               - 成功 → 标记步骤完成 → 执行下一步
               - 失败 → 递进重试（直接重试 → 退避 → 清缓存重定位）
        """
        self.start()
        self._plan = plan
        self._start_index = min(self._resume_step_index, len(plan))
        results = []
        history = []  # ReAct 历史轨迹（类似 ReActAgent.history）
        start_index = self._start_index

        self._log("info", f"开始 ReAct 执行循环，{len(plan)} 个步骤")
        if start_index > 0:
            self._log("info", f"断点续跑: 跳过前 {start_index} 步，从步骤 {start_index + 1} 开始")
            self._prepare_resume_context(
                plan[start_index].get("action", "") if start_index < len(plan) else "",
                target_step=start_index + 1,
            )

        if start_index >= len(plan):
            self.finish(True)
            return {
                "success": True,
                "results": results,
                "history": history,
                "skipped_completed": True,
                "risk_stats": dict(self._risk_stats),
                "vision_fallback_stats": dict(self._vision_fallback_stats),
                "recovery_error": self._last_recovery_error,
            }

        for i in range(start_index, len(plan)):
            step = plan[i]
            self.state.step_index = i + 1
            self.state.total_steps = len(plan)
            action_name = step.get("action", "")
            params = step.get("params", {})
            self.state.current_action = action_name

            self._log("info", f"--- 步骤 {i+1}/{len(plan)}: {action_name} ---")

            # 安全检查
            if not self._check_safety(action_name):
                self.finish(False, f"安全拦截: {action_name}")
                return {
                    "success": False,
                    "results": results,
                    "error": "安全拦截",
                    "risk_stats": dict(self._risk_stats),
                    "vision_fallback_stats": dict(self._vision_fallback_stats),
                    "recovery_error": self._last_recovery_error,
                }

            # 熔断检查
            if not self._circuit_breaker.can_execute():
                self.finish(False, "熔断器开启")
                return {
                    "success": False,
                    "results": results,
                    "error": "熔断器开启",
                    "risk_stats": dict(self._risk_stats),
                    "vision_fallback_stats": dict(self._vision_fallback_stats),
                    "recovery_error": self._last_recovery_error,
                }

            # 执行前确保 locator 有效（非窗口类动作）
            if action_name not in {"find_window", "activate_window"}:
                self._ensure_locator()

            # ── ReAct: Act → Screenshot → Observe → Reflect（含递进重试）──
            step_success = False
            last_act_result = None
            observation = None
            screenshot_path = None
            retry_count = 1
            # 熔断器修复：只在所有重试都失败后才触发，避免中途打开熔断器
            _step_ultimately_failed = False

            for retry in range(REACT_MAX_RETRIES):
                window_before = self._capture_window_summary()

                # 递进式重试策略（Reflection: 每次重试前做不同的事）
                if retry == 1:
                    wait = random.uniform(2, 4)
                    self._log("info", f"重试 [2/{REACT_MAX_RETRIES}]: 等待 {wait:.1f}s 后重试")
                    time.sleep(wait)
                elif retry == 2:
                    self._log("info", f"重试 [3/{REACT_MAX_RETRIES}]: 清除缓存，强制重定位窗口")
                    self._force_relocate()

                # 1. Act: 执行动作
                try:
                    act_result = self.act(action_name, params)
                except Exception as e:
                    act_result = {"success": False, "error": str(e)}
                    self._log("error", f"步骤 {i+1} 执行异常: {e}")
                last_act_result = act_result
                window_after = self._capture_window_summary()
                act_result["window_before"] = window_before
                act_result["window_after"] = window_after
                window_diff = self._diff_window_summary(window_before, window_after)
                act_result["window_diff"] = window_diff
                self._log_window_diff_risk(action_name, window_diff, step_index=i + 1)

                # 2. Screenshot: 截图当前窗口状态
                screenshot_path = self._take_screenshot(action_name)
                if screenshot_path:
                    act_result["screenshot"] = screenshot_path

                # 3. Observe: LLM 视觉分析截图（ReAct Observation）
                observation = self._react_observe(action_name, screenshot_path, act_result)
                if not act_result.get("success", False):
                    last_act_result["vision_verified"] = observation.get("status") != "unknown"
                    last_act_result["vision_analysis"] = observation
                    last_act_result["error"] = act_result.get("error", "Action execution failed")
                    # 熔断器修复：只在最后一次重试失败后才触发
                    if retry == REACT_MAX_RETRIES - 1:
                        self._circuit_breaker.record_failure()
                        _step_ultimately_failed = True
                    self._log(
                        "warning",
                        f"Step {i+1} action failed "
                        f"(retry {retry+1}/{REACT_MAX_RETRIES}): "
                        f"{last_act_result['error']}",
                    )
                    continue

                # 4. Reflect: 根据 Observation 判断是否成功
                if observation.get("status") == "ok":
                    # LLM 确认成功
                    step_success = bool(act_result.get("success", False))
                    last_act_result["vision_verified"] = True
                    last_act_result["vision_analysis"] = observation
                    if step_success:
                        self._circuit_breaker.record_success()
                    self._log("info", f"步骤 {i+1} 视觉验证通过: {observation.get('reason', '')}")
                    break

                elif observation.get("status") == "error":
                    # LLM 确认失败，进入重试
                    last_act_result["vision_verified"] = True
                    last_act_result["vision_analysis"] = observation
                    last_act_result["success"] = False
                    last_act_result["error"] = f"视觉验证失败: {observation.get('reason', '')}"
                    # 熔断器修复：只在最后一次重试失败后才触发
                    if retry == REACT_MAX_RETRIES - 1:
                        self._circuit_breaker.record_failure()
                        _step_ultimately_failed = True
                    self._log("warning",
                              f"步骤 {i+1} 视觉验证失败"
                              f"（重试 {retry+1}/{REACT_MAX_RETRIES}）: "
                              f"{observation.get('reason', '')}")
                    continue

                else:
                    # status == "unknown": LLM 无法判断，信任 action 原始结果
                    step_success = act_result.get("success", False)
                    last_act_result["vision_verified"] = False
                    last_act_result["verification_method"] = "action-result-fallback"
                    self._log("info", f"步骤 {i+1} LLM 无法判断，使用动作结果: "
                              f"{'成功' if step_success else '失败'}")
                    break

            # ── 记录步骤结果 ──
            retry_count = retry + 1
            self._record_vision_fallback(i + 1, action_name, last_act_result, step_success)
            step_result = {
                "step": i + 1,
                "action": action_name,
                "success": step_success,
                "result": last_act_result,
                "retries": retry_count,
                "used_vision_fallback": bool((last_act_result or {}).get("used_vision_fallback")),
                "vision_template": ((last_act_result or {}).get("vision_fallback") or {}).get("template", ""),
            }
            results.append(step_result)

            # 更新数据库步骤状态
            if self._db and self._task_id:
                self._db.update_step_status(
                    task_id=self._task_id,
                    step_index=i,
                    status="success" if step_success else "failed",
                    error=last_act_result.get("error", "") if not step_success else "",
                    screenshot=screenshot_path or "",
                    result=last_act_result,
                )

            # 累积 ReAct 历史轨迹（Plan-and-Solve: 传递给后续步骤）
            history.append({
                "step": i + 1,
                "action": action_name,
                "observation_status": observation.get("status", "unknown") if observation else "none",
                "observation_reason": observation.get("reason", "") if observation else "",
                "success": step_success,
            })

            # 记忆关键步骤
            self._remember(
                f"步骤 {i+1} {action_name}: "
                f"{'成功' if step_success else '失败（重试' + str(retry_count) + '次）'}",
                importance=0.7 if not step_success else 0.3,
                step=i + 1,
                action=action_name,
                action_result_success=bool((last_act_result or {}).get("success", False)),
                vision_status=(observation or {}).get("status", "none"),
                used_vision_fallback=bool((last_act_result or {}).get("used_vision_fallback")),
                vision_template=((last_act_result or {}).get("vision_fallback") or {}).get("template", ""),
                retry_count=retry_count,
                error=(last_act_result or {}).get("error", ""),
                screenshot=screenshot_path or "",
            )

            # Plan-and-Solve: 实时更新计划文件（每步完成后持久化状态）
            self._update_plan_file(plan, i, step_success, retry_count)

            # CLI 进度回调
            if self._on_progress:
                try:
                    self._on_progress(
                        step_index=i + 1,
                        total_steps=len(plan),
                        action=action_name,
                        success=step_success,
                        retries=retry_count,
                        observation=observation,
                    )
                except Exception:
                    pass

            # 必需步骤失败则中止
            if not step_success and step.get("required", True):
                self.finish(False, f"步骤 {i+1} 失败（已重试 {retry_count} 次）")
                return {
                    "success": False,
                    "results": results,
                    "error": last_act_result.get("error", "步骤失败"),
                    "failed_step": i + 1,
                    "history": history,
                    "risk_stats": dict(self._risk_stats),
                    "vision_fallback_stats": dict(self._vision_fallback_stats),
                    "recovery_error": self._last_recovery_error,
                }

            self._log("info", f"步骤 {i+1}/{len(plan)} 完成: {'OK' if step_success else 'SKIP'}")

        self.finish(True)
        self._log("info", f"ReAct 循环完成，共 {len(results)} 步")
        return {
            "success": True,
            "results": results,
            "history": history,
            "risk_stats": dict(self._risk_stats),
            "vision_fallback_stats": dict(self._vision_fallback_stats),
            "recovery_error": self._last_recovery_error,
        }

    def _react_observe(self, action_name: str, screenshot_path: Optional[str],
                       act_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        ReAct Observation 阶段 — 截图 + LLM 视觉分析

        参考 ReAct 范式的 Observation: 收集执行结果和环境反馈
        参考 Reflection 范式的自我评估: LLM 扮演"评审员"角色

        Returns:
            {"status": "ok"|"error"|"unknown", "reason": "..."}
        """
        # LLM 可用 + 有截图 → 视觉验证
        if not act_result.get("success", False):
            error = act_result.get("error") or act_result.get("message") or "Unknown error"
            return {"status": "error", "reason": f"Action returned failure: {error}"}

        if self._llm and screenshot_path:
            try:
                observation = self._vision_verify(action_name, screenshot_path, act_result)
                if observation and observation.get("status") == "unknown":
                    window_diff = act_result.get("window_diff", {}) or {}
                    if window_diff.get("risk_level") == "high":
                        risk_hint = window_diff.get("risk_hint", "检测到高风险窗口漂移")
                        return {
                            "status": "error",
                            "reason": f"{risk_hint}，且视觉校验无法确认当前页面，按失败处理",
                        }
                return observation
            except Exception as exc:
                self._log("warning", f"LLM 视觉验证异常: {exc}")

        # LLM 不可用或无截图 → 信任 action_result
        if act_result.get("success"):
            return {"status": "ok", "reason": "动作返回成功（无视觉验证）"}
        else:
            error = act_result.get("error") or act_result.get("message") or "未知错误"
            return {"status": "error", "reason": f"动作返回失败: {error}"}

    def _ensure_locator(self):
        """执行前验证 locator.hwnd 有效，无效则自动重定位。"""
        if self._locator is None:
            self._log("info", "locator 未初始化，执行本地预检恢复")
            self._recover_locator(reason="missing-locator")
            return
        try:
            import ctypes
            hwnd = self._locator.hwnd
            if hwnd and ctypes.windll.user32.IsWindow(hwnd):
                return
            # hwnd 无效，重新定位
            self._log("info", "locator.hwnd 已失效，重新定位窗口")
            self._recover_locator(reason="invalid-hwnd")
        except Exception:
            pass

    def _force_relocate(self):
        """递进重试第 3 级：清除缓存，强制重新查找窗口"""
        self._recover_locator(reason="force-relocate", clear_cache=True)

    def _prepare_resume_context(self, next_action_name: str, target_step: int = 0):
        """断点续跑前做一次本地窗口健康恢复，避免直接重跑失败 action。"""
        if next_action_name in {"find_window", "activate_window"}:
            return
        self._log("info", f"续跑预检恢复: 在重跑 {next_action_name} 前先恢复窗口上下文")
        self._recover_locator(reason="resume-preflight", step_index=target_step)

    def _recover_locator(self, reason: str, clear_cache: bool = False, step_index: int = 0) -> bool:
        """本地恢复窗口上下文：find_window → activate_window。"""
        actual_step = step_index or self.state.step_index or 0
        try:
            from infrastructure.locator import JingmaiLocator

            if self._locator is None:
                self._locator = JingmaiLocator(log=self._logger)
            elif clear_cache:
                self._locator.hwnd = None
                self._locator.window_rect = None

            info = self._locator.find_window()
            if not info:
                error = "未找到京麦窗口"
                self._last_recovery_error = f"{reason}: {error}"
                self._record_recovery_attempt(actual_step, reason, False, error)
                self._log("warning", f"窗口恢复失败({reason})：{error}")
                return False

            activated = self._locator.activate_window()
            if not activated:
                error = "activate_window 未成功"
                self._last_recovery_error = f"{reason}: {error}"
                self._record_recovery_attempt(actual_step, reason, False, error)
                self._log("warning", f"窗口恢复失败({reason})：{error}")
                return False

            self._last_recovery_error = ""
            self._record_recovery_attempt(
                actual_step,
                reason,
                True,
                "",
                window_summary=self._build_window_summary(info),
            )
            self._log("info", f"窗口恢复成功({reason}): hwnd={getattr(info, 'hwnd', self._locator.hwnd)}")
            return True
        except Exception as exc:
            error = str(exc)
            self._last_recovery_error = f"{reason}: {error}"
            self._record_recovery_attempt(actual_step, reason, False, error)
            self._log("warning", f"窗口恢复异常({reason}): {exc}")
            return False

    def _record_recovery_attempt(self, step_index: int, reason: str, success: bool, error: str,
                                 window_summary: Optional[Dict[str, Any]] = None):
        if step_index <= 0:
            return
        attempts = self._recovery_attempts.setdefault(step_index, [])
        attempt = {
            "reason": reason,
            "success": success,
            "error": error,
            "at": int(time.time()),
        }
        if window_summary:
            attempt["window"] = window_summary
        attempts.append(attempt)

    def _build_window_summary(self, info) -> Dict[str, Any]:
        rect = getattr(info, "rect", None) or self._locator.window_rect
        title = getattr(info, "title", "") or ""
        summary = {
            "hwnd": getattr(info, "hwnd", self._locator.hwnd if self._locator else 0),
            "title": title[:120],
            "rect": list(rect) if rect else [],
        }
        if rect and len(rect) == 4:
            summary["width"] = rect[2] - rect[0]
            summary["height"] = rect[3] - rect[1]
        return summary

    def _capture_window_summary(self) -> Optional[Dict[str, Any]]:
        if not self._locator:
            return None
        try:
            info = self._locator.find_window()
            if not info:
                return None
            return self._build_window_summary(info)
        except Exception:
            return None

    def _diff_window_summary(self, before: Optional[Dict[str, Any]],
                             after: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not before and not after:
            return {"changed": False, "fields": []}
        if not before or not after:
            return {
                "changed": True,
                "fields": ["window_presence"],
                "before": before,
                "after": after,
            }

        changed_fields = []
        for field in ("hwnd", "title", "rect", "width", "height"):
            if before.get(field) != after.get(field):
                changed_fields.append(field)

        diff = {"changed": bool(changed_fields), "fields": changed_fields}
        if changed_fields:
            diff["before"] = {field: before.get(field) for field in changed_fields}
            diff["after"] = {field: after.get(field) for field in changed_fields}
        return diff

    def _log_window_diff_risk(self, action_name: str, window_diff: Dict[str, Any], step_index: int):
        if not window_diff.get("changed"):
            return

        changed_fields = set(window_diff.get("fields", []))
        if {"hwnd", "title"} & changed_fields:
            risk = (
                f"步骤 {step_index} {action_name} 执行后窗口上下文发生高风险变化: "
                f"fields={sorted(changed_fields)}; 可能命中错误窗口或页面"
            )
            window_diff["risk_level"] = "high"
            window_diff["risk_hint"] = risk
            self._risk_stats["high_risk_window_shift_count"] += 1
            self._risk_stats["high_risk_window_shift_steps"].append({
                "step": step_index,
                "action": action_name,
                "fields": sorted(changed_fields),
            })
            self._log("warning", risk)
            return

        info = f"步骤 {step_index} {action_name} 执行后窗口发生变化: fields={window_diff.get('fields', [])}"
        window_diff["risk_level"] = "info"
        window_diff["risk_hint"] = info
        self._log("info", info)

    def _take_screenshot(self, action_name: str) -> Optional[str]:
        """截图当前窗口状态"""
        if not self._locator:
            return None
        try:
            import os
            screenshot_dir = self.settings.SCREENSHOT_DIR
            os.makedirs(screenshot_dir, exist_ok=True)
            save_path = os.path.join(
                screenshot_dir,
                f"{self._task_id}_{action_name}_{int(time.time())}.png"
            )
            return self._locator.take_screenshot(save_path, for_vision=True)
        except Exception as exc:
            self._log("warning", f"截图失败: {exc}")
            return None

    def _vision_verify(self, action_name: str, screenshot_path: str,
                       action_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        调用 LLM 做视觉验证

        Returns:
            dict: {"status": "ok"|"error"|"unknown", "reason": "..."}
        """
        # 注意：以下提示词中提到的"余额已用完"等页面内嵌卡片不算错误
        # 注意：以下提示词中提到的"余额已用完"等页面内嵌卡片不算错误
        prompt_map = {
            "verify_result": "分析这张京麦客户端截图，检查是否有错误提示或异常状态。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}。注意：页面内的'余额已用完'、'请尽快充值'等京准通广告提示卡片不是错误，不影响商品发布功能。",
            "publish_product": "分析这张截图，判断商品是否已成功发布。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}。注意：页面内的'余额已用完'、'请尽快充值'等京准通广告提示卡片不是错误，不影响商品发布功能。",
            "save_draft": "分析这张截图，判断草稿是否已成功保存。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}。注意：页面内的'余额已用完'、'请尽快充值'等京准通广告提示卡片不是错误，不影响商品发布功能。",
            "find_window": "分析这张京麦客户端截图，确认是否已找到京麦窗口。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}。注意：页面内的'余额已用完'、'请尽快充值'等京准通广告提示卡片不是错误，只要找到京麦窗口即可。",
            "activate_window": "分析这张京麦客户端截图，确认京麦窗口是否已激活。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}。注意：页面内的'余额已用完'、'请尽快充值'等京准通广告提示卡片不是错误，只要窗口已激活即可。",
            "navigate_to": "分析这张京麦客户端截图，确认是否已成功导航到商品发布流程。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}。以下任一情况都应判定为成功：1. 已进入类目选择发品页，例如出现类目搜索、类目面包屑、类目列、'下一步，完善其他商品信息'等元素；2. 已进入后续商品信息页，例如出现'商品标题'、'品牌'、'价格'等输入区域。只有仍停留在首页、工作台、商品列表页，或明显不是发品流程时才返回 error。页面内的'余额已用完'广告卡片不是错误。",
            "select_category": "分析这张京麦客户端截图，确认是否已成功选择商品类目。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}。以下任一情况都应判定为成功：1. 类目页中已明确选中'插座'，且下一步可点击；2. 页面已经从类目页跳转到商品信息页，即使仍在骨架屏加载阶段，只要能看出进入了包含'商品标题'、'品牌'、'价格'等字段的发布流程也算成功。不要因为截图已经离开类目页就判失败；只有仍停留在类目搜索/选择状态且未确认选中时才返回 error。页面内的'余额已用完'广告卡片不是错误。",
            "fill_product_info": "分析这张京麦客户端截图，确认商品信息是否已正确填写。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}。必须检查：1.商品标题字段是否有内容 2.京东价格是否显示70 3.市场价是否显示70 4.不是空白表单。页面内的'余额已用完'广告卡片不是错误。",
        }
        prompt = prompt_map.get(
            action_name,
            "分析这张截图，判断操作是否成功。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}。注意：页面内的'余额已用完'、'请尽快充值'等京准通广告提示卡片不是错误，不影响商品发布功能。"
        )

        window_diff = action_result.get("window_diff", {}) or {}
        if window_diff.get("risk_level") == "high":
            risk_hint = window_diff.get("risk_hint", "检测到窗口上下文高风险漂移")
            prompt = (
                f"{risk_hint}。请优先检查是否跳转到了错误窗口、错误页面、错误标签或非京麦发布上下文。"
                f"如果截图显示页面上下文明显不对，应优先返回 error。{prompt}"
            )

        response = self._llm.invoke_multimodal(prompt, screenshot_path)
        if not response:
            return None

        # 解析 LLM 返回的 JSON
        import json
        import re
        try:
            # 尝试直接解析
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # 尝试提取 JSON
            match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            self._log("warning", f"LLM 视觉验证返回非 JSON: {response[:200]}")
            return {"status": "unknown", "reason": f"LLM 返回无法解析: {response[:100]}"}

    def _update_plan_file(self, plan: List[Dict[str, Any]], step_index: int,
                          success: bool, retries: int):
        """
        Plan-and-Solve: 每步完成后将计划状态写回文件

        更新计划文件中对应步骤的 status/retries/screenshot 字段，
        使外部工具（CLI / 监控脚本）可实时读取执行进度。
        """
        if not self._plan_file:
            return
        try:
            # 构建带状态的完整计划包
            updated_steps = []
            for idx, step in enumerate(plan):
                step_copy = dict(step)
                step_num = idx + 1
                if idx == step_index:
                    # 当前步骤：写入本轮执行结果
                    step_copy["status"] = "success" if success else "failed"
                    step_copy["retries"] = retries
                elif idx < self._start_index:
                    # 断点续跑前已跳过的步骤：保留原始状态（不臆断为 success）
                    existing = str(step_copy.get("status", "")).lower()
                    if existing not in {"success", "failed", "pending"}:
                        step_copy["status"] = "success"
                    # 不覆盖原有 status，保持原样
                elif idx < step_index:
                    # 本轮中已执行的步骤：标记成功
                    step_copy["status"] = "success"
                else:
                    step_copy["status"] = "pending"
                if step_num in self._recovery_attempts:
                    step_copy["recovery_attempts"] = list(self._recovery_attempts[step_num])
                updated_steps.append(step_copy)

            plan_package = {
                "task_id": self._task_id,
                "status": "running",
                "current_step": step_index + 1,
                "total_steps": len(plan),
                "plan": updated_steps,
            }
            # 保留原始计划中的 product_data 等元信息
            if self._original_plan_data:
                plan_package.setdefault("product_data", self._original_plan_data.get("product_data", {}))
            if self._last_recovery_error:
                plan_package["recovery_error"] = self._last_recovery_error
            plan_package["risk_stats"] = dict(self._risk_stats)
            plan_package["vision_fallback_stats"] = dict(self._vision_fallback_stats)

            import os
            os.makedirs(os.path.dirname(self._plan_file) or ".", exist_ok=True)
            with open(self._plan_file, "w", encoding="utf-8") as f:
                json.dump(plan_package, f, ensure_ascii=False, indent=2)

            self._log("debug", f"计划文件已更新: 步骤 {step_index+1}/{len(plan)}")
        except Exception as exc:
            self._log("warning", f"更新计划文件失败: {exc}")

    def _finalize_plan_file(self, plan: List[Dict[str, Any]], success: bool,
                            failed_step: Optional[int] = None, error: str = ""):
        """执行结束后回写计划包顶层状态，便于监控与断点续跑判断。"""
        if not self._plan_file:
            return
        try:
            updated_steps = []
            failed_index = failed_step - 1 if failed_step else None
            for idx, step in enumerate(plan):
                step_copy = dict(step)
                current_status = str(step_copy.get("status", "")).lower()
                step_num = idx + 1
                if success:
                    step_copy["status"] = "success"
                elif failed_index is None:
                    step_copy["status"] = current_status or "pending"
                elif idx < failed_index:
                    step_copy["status"] = "success"
                elif idx == failed_index:
                    step_copy["status"] = "failed"
                else:
                    step_copy["status"] = "pending"
                if step_num in self._recovery_attempts:
                    step_copy["recovery_attempts"] = list(self._recovery_attempts[step_num])
                updated_steps.append(step_copy)

            plan_package = {
                "task_id": self._task_id,
                "status": "success" if success else "failed",
                "current_step": len(plan) if success else (failed_step or self.state.step_index or 1),
                "total_steps": len(plan),
                "plan": updated_steps,
            }
            if error and not success:
                plan_package["error"] = error
            if self._last_recovery_error:
                plan_package["recovery_error"] = self._last_recovery_error
            if self._original_plan_data:
                plan_package.setdefault("product_data", self._original_plan_data.get("product_data", {}))
            plan_package["risk_stats"] = dict(self._risk_stats)
            plan_package["vision_fallback_stats"] = dict(self._vision_fallback_stats)

            import os
            os.makedirs(os.path.dirname(self._plan_file) or ".", exist_ok=True)
            with open(self._plan_file, "w", encoding="utf-8") as f:
                json.dump(plan_package, f, ensure_ascii=False, indent=2)

            self._log("debug", f"计划文件顶层状态已更新: {plan_package['status']}")
        except Exception as exc:
            self._log("warning", f"写入计划最终状态失败: {exc}")

    @property
    def progress(self) -> str:
        if not self.state.started_at:
            return "未开始"
        return f"步骤 {self.state.step_index}/{self.state.total_steps} - {self.state.current_action}"
