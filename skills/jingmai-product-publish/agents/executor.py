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
import inspect
import json
import random
import time
from typing import Any, Callable, Dict, List, Optional

from actions import ActionRegistry
from agents.base import BaseAgent


# 递进式重试最大次数
REACT_MAX_RETRIES = 3

STRICT_PRECHECK_ACTIONS = {
    "navigate_to",
    "select_category",
    "fill_product_info",
    "save_draft",
    "publish_product",
    "verify_result",
}

STRICT_POSTCHECK_ACTIONS = {
    "navigate_to",
    "select_category",
    "fill_product_info",
    "save_draft",
    "publish_product",
    "verify_result",
}


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
        self._step_artifacts: Dict[int, Dict[str, Any]] = {}
        self._video_observer = None
        self._opencli_session = "jingmai-publish-recovery"
        self._last_opencli_probe: Dict[str, Any] = {}

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
        self._step_artifacts = {}
        self._video_observer = None
        self._opencli_session = f"jingmai-publish-{self._task_id or 'session'}"
        self._last_opencli_probe = {}
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
            react_contract = step.get("react_contract") or {}
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
            last_recovery = None
            # 熔断器修复：只在所有重试都失败后才触发，避免中途打开熔断器
            _step_ultimately_failed = False

            for retry in range(REACT_MAX_RETRIES):
                precheck_screenshot = None
                precheck_observation = None
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
                    precheck_artifacts = self._capture_visual_artifacts(i + 1, action_name, "precheck")
                    precheck_screenshot = precheck_artifacts.get("primary_path") or ""
                    precheck_observation = self._react_precheck(
                        action_name=action_name,
                        step=step,
                        screenshot_path=precheck_screenshot,
                        history=history,
                    )
                    precheck_observation = self._coerce_precheck_for_action(
                        action_name=action_name,
                        observation=precheck_observation,
                        step=step,
                        history=history,
                    )
                    precheck_status = (precheck_observation or {}).get("status", "unknown")
                    precheck_state = (precheck_observation or {}).get("current_state", "")
                    precheck_action = (precheck_observation or {}).get("suggested_action", "")
                    if precheck_observation:
                        self._log(
                            "info",
                            f"步骤 {i+1} precheck: status={precheck_status} "
                            f"state={precheck_state or 'n/a'} suggested={precheck_action or 'n/a'}",
                        )
                    should_block_precheck = self._should_block_precheck(action_name, precheck_observation)
                    if should_block_precheck:
                        last_act_result = {
                            "success": False,
                            "error": f"视觉预检失败: {precheck_observation.get('reason', '')}",
                            "precheck": precheck_observation,
                            "screenshot": precheck_screenshot or "",
                            "react_contract": react_contract,
                        }
                        observation = precheck_observation
                        if retry == REACT_MAX_RETRIES - 1:
                            self._circuit_breaker.record_failure()
                            _step_ultimately_failed = True
                        self._log(
                            "warning",
                            f"步骤 {i+1} 执行前视觉预检失败"
                            f"（重试 {retry+1}/{REACT_MAX_RETRIES}）: "
                            f"{precheck_observation.get('reason', '')}",
                        )
                        recovery = self._attempt_deviation_recovery(
                            step_index=i + 1,
                            retry_index=retry,
                            action_name=action_name,
                            step=step,
                            history=history,
                            failure_stage="precheck",
                            observation=precheck_observation,
                            act_result=last_act_result,
                            window_diff=None,
                        )
                        if recovery:
                            last_recovery = recovery
                            last_act_result["recovery"] = recovery
                        continue

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
                postcheck_artifacts = self._capture_visual_artifacts(i + 1, action_name, "postcheck")
                screenshot_path = postcheck_artifacts.get("primary_path") or ""
                if screenshot_path:
                    act_result["screenshot"] = screenshot_path
                artifacts = self._step_artifacts.setdefault(i + 1, {})
                artifacts["action_screenshot"] = screenshot_path or ""
                artifacts["postcheck_screenshot"] = screenshot_path or ""

                # 3. Observe: LLM 视觉分析截图（ReAct Observation）
                act_result["react_contract"] = react_contract
                observation = self._call_react_observe(
                    action_name,
                    screenshot_path,
                    act_result,
                    step=step,
                    history=history,
                )
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
                    recovery = self._attempt_deviation_recovery(
                        step_index=i + 1,
                        retry_index=retry,
                        action_name=action_name,
                        step=step,
                        history=history,
                        failure_stage="action",
                        observation=observation,
                        act_result=last_act_result,
                        window_diff=window_diff,
                    )
                    if recovery:
                        last_recovery = recovery
                        last_act_result["recovery"] = recovery
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
                    recovery = self._attempt_deviation_recovery(
                        step_index=i + 1,
                        retry_index=retry,
                        action_name=action_name,
                        step=step,
                        history=history,
                        failure_stage="postcheck",
                        observation=observation,
                        act_result=last_act_result,
                        window_diff=window_diff,
                    )
                    if recovery:
                        last_recovery = recovery
                        last_act_result["recovery"] = recovery
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
            if isinstance(last_act_result, dict) and last_recovery and "recovery" not in last_act_result:
                last_act_result["recovery"] = last_recovery
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


    def _react_precheck(
        self,
        action_name: str,
        step: Dict[str, Any],
        screenshot_path: Optional[str],
        history: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Vision gate before action execution."""
        if not self._llm or not screenshot_path:
            return {"status": "unknown", "reason": "no-llm-or-screenshot", "stage": "precheck"}

        contract = step.get("react_contract") or {}
        precheck = contract.get("precheck") or {}
        goal = contract.get("goal") or f"???? {action_name}"
        workflow_context = contract.get("workflow_context") or {}
        expect_any = precheck.get("expect_any") or []
        reject_any = precheck.get("reject_any") or []
        recent_history = history[-3:] if history else []
        prompt = (
            "?????????????????????"
            "???????????????????????????????"
            "??? JSON: "
            "{\"status\":\"ok\"|\"error\"|\"unknown\"," 
            "\"reason\":\"??\","
            "\"current_state\":\"????????\","
            "\"suggested_action\":\"proceed\"|\"recover\"|\"stop\"}?"
            f"????: {action_name}?"
            f"????: {goal}?"
            f"???????: {json.dumps(workflow_context, ensure_ascii=False) if workflow_context else '{}'}?"
            f"???????: {expect_any or ['?']}?"
            f"???????????????: {reject_any or ['?']}?"
            f"??????: {json.dumps(recent_history, ensure_ascii=False)}?"
            f"???????: {self._build_precheck_action_hint(action_name)}?"
            "????????????????????????????????????"
            "?????????????????????? error?"
        )
        result = self._vision_query(prompt, screenshot_path)
        if result is not None:
            result.setdefault("stage", "precheck")
        return result

    @staticmethod
    def _should_block_precheck(action_name: str, observation: Optional[Dict[str, Any]]) -> bool:
        reason = str((observation or {}).get("reason", "") or "").lower()
        if reason == "no-llm-or-screenshot":
            return False
        status = str((observation or {}).get("status", "unknown") or "unknown").lower()
        return status == "error" or (action_name in STRICT_PRECHECK_ACTIONS and status != "ok")

    @staticmethod
    def _build_precheck_action_hint(action_name: str) -> str:
        hints = {
            "publish_product": (
                "如果截图里已经能看到‘提交发布’按钮，或同时看到商品标题/品牌/市场价/京东价等商品信息字段，"
                "这仍然属于可执行 publish_product 的发布表单页，应该返回 status=ok 和 suggested_action=proceed。"
                "只有当页面明显处于类目选择页、商品列表/草稿列表页、登录页、系统错误页时，才返回 error。"
            ),
            "verify_result": (
                "如果截图里仍停留在发布表单，但没有出现错误、异常、登录失效，也可以视为可继续核验的状态，"
                "不要因为仍看到‘提交发布’按钮就直接判错。"
            ),
        }
        return hints.get(action_name, "仅根据当前截图判断是否可以安全继续当前步骤。")

    def _react_observe(
        self,
        action_name: str,
        screenshot_path: Optional[str],
        act_result: Dict[str, Any],
        step: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Screenshot-based postcheck after action execution."""
        if not act_result.get("success", False):
            error = act_result.get("error") or act_result.get("message") or "Unknown error"
            return {"status": "error", "reason": f"Action returned failure: {error}", "stage": "postcheck"}

        if self._llm and screenshot_path:
            try:
                observation = self._vision_verify(
                    action_name,
                    screenshot_path,
                    act_result,
                    step=step,
                    history=history or [],
                )
                observation = self._coerce_postcheck_for_action(
                    action_name=action_name,
                    observation=observation,
                    step=step,
                    history=history,
                    act_result=act_result,
                )
                if observation:
                    self._log(
                        "info",
                        f"步骤 {self.state.step_index} postcheck: status={observation.get('status', 'unknown')} "
                        f"reason={observation.get('reason', '')[:120]}",
                    )
                if observation and observation.get("status") == "unknown":
                    if action_name in STRICT_POSTCHECK_ACTIONS:
                        return {
                            "status": "error",
                            "reason": f"高风险步骤的视觉复核无法确认结果: {observation.get('reason', '')}",
                            "stage": "postcheck",
                        }
                    window_diff = act_result.get("window_diff", {}) or {}
                    if window_diff.get("risk_level") == "high":
                        risk_hint = window_diff.get("risk_hint", "??????????")
                        return {
                            "status": "error",
                            "reason": f"{risk_hint}????????????????????",
                            "stage": "postcheck",
                        }
                if observation is not None:
                    observation.setdefault("stage", "postcheck")
                return observation
            except Exception as exc:
                self._log("warning", f"LLM ??????: {exc}")

        if act_result.get("success"):
            return {"status": "ok", "reason": "?????????????", "stage": "postcheck"}

        error = act_result.get("error") or act_result.get("message") or "????"
        return {"status": "error", "reason": f"??????: {error}", "stage": "postcheck"}

    def _call_react_observe(
        self,
        action_name: str,
        screenshot_path: Optional[str],
        act_result: Dict[str, Any],
        step: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        observe = self._react_observe
        try:
            signature = inspect.signature(observe)
        except (TypeError, ValueError):
            signature = None

        kwargs: Dict[str, Any] = {}
        if signature is not None:
            if "step" in signature.parameters:
                kwargs["step"] = step
            if "history" in signature.parameters:
                kwargs["history"] = history
        else:
            kwargs = {"step": step, "history": history}

        try:
            return observe(action_name, screenshot_path, act_result, **kwargs)
        except TypeError:
            return observe(action_name, screenshot_path, act_result)

    def _attempt_deviation_recovery(
        self,
        step_index: int,
        retry_index: int,
        action_name: str,
        step: Dict[str, Any],
        history: List[Dict[str, Any]],
        failure_stage: str,
        observation: Optional[Dict[str, Any]],
        act_result: Optional[Dict[str, Any]],
        window_diff: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if retry_index >= REACT_MAX_RETRIES - 1:
            return None

        deviation = self._classify_deviation(
            action_name=action_name,
            step=step,
            failure_stage=failure_stage,
            observation=observation,
            act_result=act_result,
            window_diff=window_diff,
        )
        plan = self._build_recovery_actions(
            action_name=action_name,
            step=step,
            retry_index=retry_index,
            deviation=deviation,
        )
        if not plan:
            return {
                "deviation_type": deviation["type"],
                "recoverable": False,
                "verified": False,
                "actions": [],
                "error": deviation["reason"],
            }

        executed: List[Dict[str, Any]] = []
        success = True
        error = ""
        for action in plan:
            result = self._run_recovery_action(action, step_index=step_index)
            executed.append(result)
            if not result.get("success"):
                success = False
                error = result.get("error", "recovery-action-failed")
                break

        verification = {
            "success": success,
            "verified": success,
            "observation": None,
            "error": error,
        }
        if success:
            verification = self._verify_recovery_state(
                action_name=action_name,
                step=step,
                history=history,
                retry_index=retry_index,
            )
            success = bool(verification.get("success"))
            error = verification.get("error", "")

        summary = {
            "deviation_type": deviation["type"],
            "recoverable": True,
            "verified": bool(verification.get("verified")),
            "actions": executed,
            "error": error,
        }
        if verification.get("observation") is not None:
            summary["verification"] = verification["observation"]
        if self._last_opencli_probe:
            summary["opencli_probe"] = {
                "page_state": str((self._last_opencli_probe.get("observation") or {}).get("page_state", "") or ""),
                "reason": str((self._last_opencli_probe.get("observation") or {}).get("reason", "") or ""),
                "raw_output": str(self._last_opencli_probe.get("raw_output", "") or "")[:400],
            }
        self._record_recovery_attempt(
            step_index,
            reason=f"{failure_stage}:{deviation['type']}",
            success=success,
            error=error,
            details=summary,
        )
        if success:
            self._log("info", f"步骤 {step_index} 恢复矩阵执行成功: {deviation['type']}")
        else:
            self._log("warning", f"步骤 {step_index} 恢复矩阵执行失败: {deviation['type']} {error}")
        return summary

    def _classify_deviation(
        self,
        action_name: str,
        step: Dict[str, Any],
        failure_stage: str,
        observation: Optional[Dict[str, Any]],
        act_result: Optional[Dict[str, Any]],
        window_diff: Optional[Dict[str, Any]],
    ) -> Dict[str, str]:
        reason = str((observation or {}).get("reason", "") or "")
        current_state = str((observation or {}).get("current_state", "") or "")
        suggested_action = str((observation or {}).get("suggested_action", "") or "")
        action_error = str((act_result or {}).get("error", "") or "")
        combined = "\n".join([reason, current_state, suggested_action, action_error]).lower()
        page_state = self._detect_page_state(observation, action_name=action_name)

        hard_stop_markers = ("扫码登录", "登录失效", "系统错误", "404", "网络异常", "白屏")
        if any(marker in combined for marker in hard_stop_markers):
            return {"type": "hard_stop", "reason": reason or action_error or current_state, "page_state": page_state}

        if window_diff and (
            window_diff.get("risk_level") == "high"
            or any(field in {"hwnd", "title", "window_presence"} for field in window_diff.get("fields", []))
        ):
            return {"type": "window_context_lost", "reason": window_diff.get("risk_hint", "window-shift"), "page_state": page_state}

        if failure_stage in {"precheck", "postcheck"} and page_state in {"product_list_page", "category_page"}:
            return {"type": "wrong_page_publish_flow", "reason": reason or current_state, "page_state": page_state}

        if action_name in {"fill_product_info", "fill_product_description", "publish_product", "save_draft", "verify_result"}:
            publish_form_markers = ("商品标题", "品牌", "价格", "发布商品", "商品信息", "商品描述", "物流售后")
            if failure_stage == "postcheck" and any(marker.lower() in combined for marker in publish_form_markers):
                return {"type": "form_section_mismatch", "reason": reason or current_state, "page_state": page_state}

        if failure_stage == "action":
            return {"type": "action_execution_error", "reason": action_error or reason or "action-failed", "page_state": page_state}
        if failure_stage == "postcheck":
            return {"type": "postcheck_validation_error", "reason": reason or current_state or "postcheck-failed", "page_state": page_state}
        return {"type": "precheck_blocked", "reason": reason or current_state or "precheck-failed", "page_state": page_state}

    def _build_recovery_actions(
        self,
        action_name: str,
        step: Dict[str, Any],
        retry_index: int,
        deviation: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        deviation_type = deviation.get("type", "")
        page_state = deviation.get("page_state", "unknown")
        if deviation_type == "hard_stop":
            return []

        doc_recovery = self._build_doc_strict_recovery_actions(
            action_name=action_name,
            step=step,
            retry_index=retry_index,
            deviation=deviation,
        )
        if doc_recovery:
            return doc_recovery

        stronger_reset = retry_index >= 1
        category = self._extract_recovery_category(step)
        window_action = {"type": "force_relocate" if stronger_reset else "recover_locator"}
        wait_action = {"type": "wait", "seconds": 1.5 + retry_index}

        if deviation_type == "window_context_lost":
            return [window_action, {"type": "refresh_page", "mode": "soft"}]

        if page_state == "product_list_page":
            actions = [window_action, {"type": "refresh_page", "mode": "soft"}]
            if action_name not in {"find_window", "activate_window", "navigate_to"}:
                actions.append({"type": "navigate_to", "page": "publish"})
            return actions

        if page_state == "category_page":
            actions = [window_action, {"type": "refresh_page", "mode": "soft"}]
            if category:
                actions.append({"type": "navigate_to", "page": "publish"})
                actions.append({"type": "select_category", "search_text": category})
            elif action_name not in {"find_window", "activate_window", "navigate_to"}:
                actions.append({"type": "navigate_to", "page": "publish"})
            return actions

        if page_state == "product_info_page":
            if action_name == "fill_product_description":
                return [wait_action]
            if action_name in {"publish_product", "verify_result"}:
                return [wait_action, window_action]

        if page_state == "sku_table_page":
            if action_name == "fill_product_info":
                return [wait_action]
            if action_name in {"publish_product", "verify_result"}:
                return [wait_action, window_action]

        if page_state == "description_page":
            if action_name == "fill_product_info":
                return [
                    window_action,
                    {
                        "type": "recover_from_detail_editor",
                        "page": "publish",
                        "search_text": category,
                        "target_action": action_name,
                    },
                    {"type": "opencli_state_probe", "reason": "description_page"},
                ]
            if action_name in {"publish_product", "verify_result"}:
                return [
                    wait_action,
                    window_action,
                    {
                        "type": "recover_from_detail_editor",
                        "page": "publish",
                        "search_text": category,
                        "target_action": action_name,
                    },
                    {"type": "opencli_state_probe", "reason": "description_page"},
                ]

        if page_state == "wrong_blank_page":
            actions = [window_action, {"type": "refresh_page", "mode": "hard"}, {"type": "opencli_state_probe", "reason": "wrong_blank_page"}]
            if action_name not in {"find_window", "activate_window", "navigate_to"}:
                actions.append({"type": "navigate_to", "page": "publish"})
            if action_name in {"fill_product_info", "fill_product_description", "publish_product", "verify_result"} and category:
                actions.append({"type": "select_category", "search_text": category})
            return actions

        if page_state == "publish_confirm_page":
            if action_name in {"verify_result", "publish_product"}:
                return [wait_action]

        if page_state in {"unknown", "browser_host"} and deviation_type in {"precheck_blocked", "postcheck_validation_error"}:
            actions = [wait_action, window_action, {"type": "refresh_page", "mode": "hard"}, {"type": "opencli_state_probe", "reason": deviation_type}]
            if action_name not in {"find_window", "activate_window"}:
                actions.append({"type": "navigate_to", "page": "publish"})
            if action_name in {"select_category", "fill_product_info", "fill_product_description", "publish_product", "verify_result"} and category:
                actions.append({"type": "select_category", "search_text": category})
            return actions

        if deviation_type in {"wrong_page_publish_flow", "form_section_mismatch"}:
            actions = [window_action, {"type": "refresh_page", "mode": "soft"}]
            actions.append({"type": "opencli_state_probe", "reason": deviation_type})
            if action_name not in {"find_window", "activate_window", "navigate_to"}:
                actions.append({"type": "navigate_to", "page": "publish"})
            if (
                action_name in {"fill_product_info", "fill_product_description", "publish_product", "save_draft", "verify_result"}
                and category
            ):
                actions.append({"type": "select_category", "search_text": category})
            return actions

        if deviation_type == "action_execution_error":
            return [wait_action, window_action, {"type": "refresh_page", "mode": "soft"}, {"type": "opencli_state_probe", "reason": deviation_type}]

        if deviation_type in {"precheck_blocked", "postcheck_validation_error"}:
            actions = [wait_action, window_action]
            actions.append({"type": "refresh_page", "mode": "soft" if not stronger_reset else "hard"})
            actions.append({"type": "opencli_state_probe", "reason": deviation_type})
            if stronger_reset and action_name not in {"find_window", "activate_window", "navigate_to"}:
                actions.append({"type": "navigate_to", "page": "publish"})
            return actions

        return [wait_action, window_action, {"type": "refresh_page", "mode": "soft"}, {"type": "opencli_state_probe", "reason": deviation_type or "generic"}]

    def _build_doc_strict_recovery_actions(
        self,
        action_name: str,
        step: Dict[str, Any],
        retry_index: int,
        deviation: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        if not isinstance(step, dict) or not step.get("doc_strict"):
            return []
        deviation_type = str(deviation.get("type", "") or "")
        if deviation_type not in {"wrong_page_publish_flow", "form_section_mismatch", "precheck_blocked", "postcheck_validation_error"}:
            return []

        guard = dict(step.get("doc_strict_guard") or {})
        sequence = [item for item in list(guard.get("recovery_sequence") or []) if isinstance(item, dict)]
        if not sequence:
            return []

        category = self._extract_recovery_category(step)
        params = dict((step or {}).get("params") or {})
        stronger_reset = retry_index >= 1
        actions: List[Dict[str, Any]] = []
        for item in sequence:
            action = dict(item)
            action_type = str(action.get("type", "") or "")
            if not action_type:
                continue
            if stronger_reset and action_type == "recover_locator":
                action["type"] = "force_relocate"
            if action_type == "select_category" and category and not action.get("search_text"):
                action["search_text"] = category
            if action_type in {"fill_product_info", "fill_product_description"}:
                for key in ("product", "required_visual_fields", "field_groups", "publish_mode", "doc_sections", "batch_scope"):
                    if key in params and key not in action:
                        action[key] = params.get(key)
            actions.append(action)
        return actions

    def _run_recovery_action(self, action: Dict[str, Any], step_index: int) -> Dict[str, Any]:
        action_type = str(action.get("type", "") or "")
        try:
            if action_type == "wait":
                seconds = float(action.get("seconds", 1.5) or 1.5)
                self._log("info", f"步骤 {step_index} 恢复动作: wait {seconds:.1f}s")
                time.sleep(seconds)
                return {"type": action_type, "success": True, "seconds": seconds}

            if action_type == "recover_locator":
                success = self._recover_locator(reason="matrix-recover", step_index=step_index)
                return {"type": action_type, "success": success, "error": "" if success else self._last_recovery_error}

            if action_type == "force_relocate":
                success = self._recover_locator(reason="matrix-force-relocate", clear_cache=True, step_index=step_index)
                return {"type": action_type, "success": success, "error": "" if success else self._last_recovery_error}

            if action_type == "opencli_state_probe":
                probe = self._run_opencli_state_probe(reason=str(action.get("reason", "") or "recovery"))
                self._last_opencli_probe = dict((probe or {}).get("result") or {})
                probe_result = dict((probe or {}).get("result") or {})
                probe_observation = probe_result.get("observation")
                probe_has_signal = bool(
                    isinstance(probe_observation, dict)
                    or str(probe_result.get("raw_output", "") or "").strip()
                )
                normalized_probe = dict(probe or {})
                normalized_probe["success"] = bool((probe or {}).get("success")) or probe_has_signal
                if normalized_probe["success"] and not probe.get("success"):
                    normalized_probe["error"] = ""
                return {"type": action_type, **normalized_probe}

            if action_type == "recover_from_detail_editor":
                from actions.form import _return_from_advanced_detail_editor
                from actions.window import navigate_to

                category = str(action.get("search_text", "") or "").strip()
                target_page = str(action.get("page", "publish") or "publish").strip() or "publish"
                return_success = bool(_return_from_advanced_detail_editor(locator=self._locator, log=self._logger))
                current_state = self._detect_local_page_state(action_name=str(action.get("target_action", "") or ""))
                if current_state in {"product_info_page", "sku_table_page", "category_page", "publish_confirm_page"}:
                    return {
                        "type": action_type,
                        "success": True,
                        "method": "return_to_merchant_backend",
                        "page_state": current_state,
                    }

                navigate_result = navigate_to(page=target_page, locator=self._locator, log=self._logger)
                navigate_success = bool((navigate_result or {}).get("success", False))
                select_success = True
                select_result: Dict[str, Any] | None = None
                if category:
                    select_result = ActionRegistry.execute(
                        "select_category",
                        search_text=category,
                        locator=self._locator,
                        log=self._logger,
                    )
                    select_success = bool((select_result or {}).get("success", False))

                current_state = self._detect_local_page_state(action_name=str(action.get("target_action", "") or ""))
                success = current_state in {"product_info_page", "sku_table_page", "category_page", "publish_confirm_page"}
                return {
                    "type": action_type,
                    "success": success,
                    "method": "return_then_navigate",
                    "return_success": return_success,
                    "navigate_success": navigate_success,
                    "select_success": select_success,
                    "navigate_result": navigate_result,
                    "select_result": select_result,
                    "page_state": current_state,
                    "error": "" if success else "detail editor recovery did not return to publish flow",
                }

            params = dict(action)
            params.pop("type", None)
            payload = dict(params)
            if "locator" not in payload and self._locator is not None:
                payload["locator"] = self._locator
            if "log" not in payload and self._logger is not None:
                payload["log"] = self._logger
            self._log("info", f"步骤 {step_index} 恢复动作: {action_type} {params}")
            result = ActionRegistry.execute(action_type, **payload)
            ok = bool((result or {}).get("success", False))
            return {"type": action_type, "success": ok, "result": result, "error": "" if ok else str((result or {}).get("error", ""))}
        except Exception as exc:
            return {"type": action_type, "success": False, "error": str(exc)}

    def _verify_recovery_state(
        self,
        action_name: str,
        step: Dict[str, Any],
        history: List[Dict[str, Any]],
        retry_index: int,
    ) -> Dict[str, Any]:
        recovery_action = f"recovery_{action_name}_{retry_index + 1}"
        recovery_artifacts = self._capture_visual_artifacts(
            self.state.step_index or 0,
            recovery_action,
            "recovery",
        )
        screenshot_path = recovery_artifacts.get("primary_path") or ""
        observation = self._react_precheck(
            action_name=action_name,
            step=step,
            screenshot_path=screenshot_path,
            history=history,
        )
        observation = self._coerce_precheck_for_action(
            action_name=action_name,
            observation=observation,
            step=step,
            history=history,
        )
        if observation is None:
            return {"success": True, "verified": False, "observation": None, "error": ""}
        blocked = self._should_block_precheck(action_name, observation)
        if blocked:
            probe_observation = self._build_probe_recovery_observation(action_name, step, history)
            if probe_observation is not None:
                return {
                    "success": True,
                    "verified": True,
                    "observation": probe_observation,
                    "error": "",
                    "used_opencli_probe": True,
                }
            return {
                "success": False,
                "verified": False,
                "observation": observation,
                "error": str(observation.get("reason", "") or "recovery-precheck-blocked"),
            }
        return {"success": True, "verified": True, "observation": observation, "error": ""}

    @staticmethod
    def _extract_recovery_category(step: Dict[str, Any]) -> str:
        params = (step or {}).get("params") or {}
        if not isinstance(params, dict):
            return ""
        direct = str(params.get("search_text", "") or "").strip()
        if direct:
            return direct
        product = params.get("product")
        if isinstance(product, dict):
            nested = product.get("product", product)
            if isinstance(nested, dict):
                return str(nested.get("category", "") or "").strip()
        return ""

    @staticmethod
    def _detect_page_state(observation: Optional[Dict[str, Any]], action_name: str = "") -> str:
        reason = str((observation or {}).get("reason", "") or "")
        current_state = str((observation or {}).get("current_state", "") or "")
        suggested_action = str((observation or {}).get("suggested_action", "") or "")
        text = "\n".join([reason, current_state, suggested_action]).lower()
        current_state_lower = current_state.lower()

        if any(marker in text for marker in ("扫码登录", "登录失效", "重新登录", "登录页")):
            return "login_page"
        if any(marker in current_state_lower for marker in ("商品信息页", "商品基本信息页", "product_info", "basic info")):
            return "product_info_page"
        if any(marker in text for marker in ("商品列表", "工作台", "草稿列表", "搜索结果", "列表页")):
            return "product_list_page"
        if any(
            marker in text
            for marker in (
                "sku属性",
                "销售属性",
                "批量导入",
                "批量应用",
                "默认全部sku",
                "市场价",
                "京东价",
                "采购价",
                "sku表格",
                "价格区域已显示",
            )
        ):
            return "sku_table_page"
        if (
            any(marker in text for marker in ("商品信息填写", "商品信息页", "商品基本信息页", "商品信息填写内容"))
            and not any(marker in text for marker in ("类目选择区域", "未显示类目选择区域", "仍在类目选择页"))
        ):
            return "product_info_page"
        if any(marker in text for marker in ("类目", "一级类目", "末级类目", "选择类目")):
            return "category_page"
        if any(marker in text for marker in ("商品描述", "商详", "图文编辑", "代码编辑", "高级编辑模式")):
            return "description_page"
        if any(marker in text for marker in ("空白且可能已跳转至详情页", "非编辑状态", "空白表单", "空白页面")):
            return "wrong_blank_page"
        if any(marker in text for marker in ("继续发布", "采销审核", "发布成功", "提交成功")):
            return "publish_confirm_page"
        if any(marker in text for marker in ("商品标题", "品牌", "价格", "商品信息", "发布商品", "商品基本信息")):
            return "product_info_page"
        if action_name == "fill_product_description":
            return "description_page"
        return "unknown"

    def _detect_local_page_state(self, action_name: str = "") -> str:
        if self._locator is None:
            return "unknown"
        try:
            if action_name in {"fill_product_info", "fill_product_description", "publish_product"}:
                from actions.form import _classify_fill_page_state

                return _classify_fill_page_state(locator=self._locator, log=self._logger)
        except Exception:
            pass
        return "unknown"

    @staticmethod
    def _observation_indicates_description_page(observation: Optional[Dict[str, Any]]) -> bool:
        if not isinstance(observation, dict):
            return False
        joined = "\n".join(
            [
                str(observation.get("reason", "") or ""),
                str(observation.get("current_state", "") or ""),
                str(observation.get("suggested_action", "") or ""),
            ]
        )
        markers = (
            "京东智铺",
            "返回商家后台",
            "详情页",
            "跳转至详情页",
            "已跳转至详情页",
            "非编辑状态",
            "图文编辑",
            "代码编辑",
            "高级编辑模式",
            "空白且可能已跳转至详情页",
        )
        return any(marker in joined for marker in markers)

    def _vision_query(self, prompt: str, screenshot_path: str) -> Optional[Dict[str, Any]]:
        extra_paths = self._extra_visual_paths_from_primary(screenshot_path)
        try:
            response = self._llm.invoke_multimodal(prompt, screenshot_path, extra_image_paths=extra_paths)
        except Exception as exc:
            self._log("warning", f"LLM visual verification unavailable: {exc}")
            return {
                "status": "unknown",
                "reason": f"llm-visual-unavailable: {str(exc)[:160]}",
                "suggested_action": "recover",
            }
        if not response:
            return None

        result = self._parse_llm_json_relaxed(response)
        if result is not None:
            return self._normalize_vision_gate_result(result)

        self._log("warning", f"LLM visual verification returned non-JSON: {response[:200]}")
        return {"status": "unknown", "reason": f"LLM response not parseable: {response[:100]}"}

    def _parse_llm_json_relaxed(self, response: str) -> Optional[Dict[str, Any]]:
        import re

        text = str(response or "").strip()
        if not text:
            return None

        candidates = [text]

        fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
        if fence_match:
            candidates.append(fence_match.group(1).strip())

        start = text.find("{")
        if start != -1:
            candidates.append(text[start:].strip())
            end = text.rfind("}")
            if end != -1 and end > start:
                candidates.append(text[start : end + 1].strip())

        inline_match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if inline_match:
            candidates.append(inline_match.group().strip())

        seen = set()
        for candidate in candidates:
            candidate = candidate.strip()
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            for variant in self._iter_json_repair_candidates(candidate):
                try:
                    parsed = json.loads(variant)
                except json.JSONDecodeError:
                    continue
                if isinstance(parsed, dict):
                    return parsed
        return None

    @staticmethod
    def _iter_json_repair_candidates(candidate: str):
        variants = []
        stripped = candidate.strip()
        if stripped:
            variants.append(stripped)

        if "```" in stripped:
            stripped = stripped.split("```", 1)[0].strip()
            if stripped:
                variants.append(stripped)

        if stripped.startswith("{"):
            open_count = stripped.count("{")
            close_count = stripped.count("}")
            if open_count > close_count:
                variants.append(stripped + ("}" * (open_count - close_count)))

        seen = set()
        for item in variants:
            if item and item not in seen:
                seen.add(item)
                yield item

    def _normalize_vision_gate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(result, dict):
            return {"status": "unknown", "reason": "vision result is not a dict"}

        status = str(result.get("status", "unknown") or "unknown").lower()
        reason = str(result.get("reason", "") or "")
        current_state = str(result.get("current_state", "") or "")
        suggested_action = str(result.get("suggested_action", "") or "")
        joined = f"{reason}\n{current_state}\n{suggested_action}"

        ad_markers = ("余额已用完", "请尽快充值", "京准通")
        publish_markers = ("商品发布", "商品基本信息", "类目", "商品标题", "品牌", "价格")
        if status == "error" and any(marker in joined for marker in ad_markers):
            if any(marker in joined for marker in publish_markers):
                result["status"] = "ok"
                result["reason"] = "忽略京准通余额广告卡片，页面仍处于可继续的发品流程"
                result["suggested_action"] = "proceed"
            else:
                result["status"] = "unknown"
                result["reason"] = "检测到京准通余额广告卡片，但未确认是否影响当前发品流程"
                result["suggested_action"] = "recover"
        return result

    def _build_probe_recovery_observation(
        self,
        action_name: str,
        step: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        probe = dict(self._last_opencli_probe or {})
        observation = probe.get("observation")
        if not isinstance(observation, dict):
            return None
        normalized = self._coerce_precheck_for_action(
            action_name=action_name,
            observation=dict(observation),
            step=step,
            history=history,
        )
        if not isinstance(normalized, dict):
            return None
        if self._should_block_precheck(action_name, normalized):
            page_state = str(
                normalized.get("page_state")
                or self._detect_page_state(normalized, action_name=action_name)
                or ""
            ).strip()
            if not self._probe_page_state_accepts_action(action_name, page_state):
                return None
            normalized = dict(normalized)
            normalized["status"] = "ok"
            normalized["suggested_action"] = "proceed"
            normalized["reason"] = (
                f"opencli probe accepted current page state for {action_name}: "
                f"{page_state or 'unknown'}"
            )
            normalized["page_state"] = page_state
        normalized.setdefault("recovery_source", "opencli_state_probe")
        if probe.get("raw_output") and not normalized.get("opencli_raw_output"):
            normalized["opencli_raw_output"] = str(probe.get("raw_output", "") or "")[:400]
        return normalized

    @staticmethod
    def _probe_page_state_accepts_action(action_name: str, page_state: str) -> bool:
        acceptable = {
            "navigate_to": {"category_page", "product_info_page", "sku_table_page", "description_page", "publish_confirm_page"},
            "select_category": {"category_page", "product_info_page", "sku_table_page", "description_page"},
            "fill_product_info": {"product_info_page", "sku_table_page", "publish_confirm_page"},
            "publish_product": {"product_info_page", "description_page", "publish_confirm_page"},
        }
        return page_state in acceptable.get(action_name, set())

    def _coerce_precheck_for_action(
        self,
        action_name: str,
        observation: Optional[Dict[str, Any]],
        step: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        if not isinstance(observation, dict):
            return observation

        if action_name == "fill_product_info":
            local_page_state = self._detect_local_page_state(action_name=action_name)
            observed_page_state = self._detect_page_state(observation, action_name=action_name)
            if local_page_state == "description_page":
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["page_state"] = "description_page"
                normalized["reason"] = "fill_product_info precheck accepted description_page for in-action return"
                return self._apply_doc_strict_guard(action_name, step, normalized, stage="precheck")
            if local_page_state == "wrong_blank_page":
                normalized = dict(observation)
                normalized["status"] = "error"
                normalized["suggested_action"] = "recover"
                normalized["page_state"] = local_page_state
                normalized["reason"] = "fill_product_info blocked: current page is blank/non-editing state, should recover before retry"
                return self._apply_doc_strict_guard(action_name, step, normalized, stage="precheck")
            if observed_page_state == "wrong_blank_page":
                normalized = dict(observation)
                normalized["status"] = "error"
                normalized["suggested_action"] = "recover"
                normalized["page_state"] = "wrong_blank_page"
                normalized["reason"] = "fill_product_info blocked: observation indicates blank/non-editing state"
                return self._apply_doc_strict_guard(action_name, step, normalized, stage="precheck")
            if self._observation_indicates_description_page(observation):
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["page_state"] = "description_page"
                normalized["reason"] = "fill_product_info precheck accepted observed description_page for in-action return"
                return self._apply_doc_strict_guard(action_name, step, normalized, stage="precheck")

        if action_name not in {"find_window", "activate_window", "navigate_to", "fill_product_info", "publish_product"}:
            return self._apply_doc_strict_guard(action_name, step, observation, stage="precheck")

        status = str(observation.get("status", "unknown") or "unknown").lower()
        if status not in {"error", "unknown"}:
            return self._apply_doc_strict_guard(action_name, step, observation, stage="precheck")
        if status == "unknown" and action_name not in {"fill_product_info"}:
            return self._apply_doc_strict_guard(action_name, step, observation, stage="precheck")
        if action_name in {"find_window", "activate_window"}:
            joined = "\n".join(
                [
                    str(observation.get("reason", "") or ""),
                    str(observation.get("current_state", "") or ""),
                    str(observation.get("suggested_action", "") or ""),
                ]
            )
            lowered = joined.lower()
            window_ready_markers = (
                "浜害",
                "宸ヤ綔鍙?",
                "鍟嗗搧鍙戝竷",
                "鍟嗗搧鍩烘湰淇℃伅",
                "鍟嗗鍚庡彴",
                "鍙戝竷鍟嗗搧",
                "娴忚鍣?",
                "jmworkstation",
                "pt_main",
            )
            blank_or_broken_markers = (
                "鎵爜鐧诲綍",
                "鐧诲綍澶辨晥",
                "绯荤粺閿欒",
                "404",
                "缃戠粶寮傚父",
                "绌虹櫧",
                "鐧藉睆",
                "鏈姞杞?",
                "寮傚父",
                "绾櫧",
            )
            if any(marker in lowered for marker in window_ready_markers) and not any(
                marker in joined for marker in blank_or_broken_markers
            ):
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["reason"] = "window precheck accepted browser-hosted jingmai page"
                return normalized
            if self._locator is not None:
                try:
                    window_info = self._locator.find_window()
                except Exception:
                    window_info = None
                window_title = str(getattr(window_info, "title", "") or "")
                if window_title:
                    lowered_title = window_title.lower()
                    if (
                        any(token in lowered_title for token in ("jd_", "jmworkstation", "jingmai", "京麦"))
                        and not any(marker in joined for marker in ("扫码登录", "登录失效", "系统错误", "404", "网络异常"))
                        and not any(marker in joined for marker in blank_or_broken_markers)
                    ):
                        normalized = dict(observation)
                        normalized["status"] = "ok"
                        normalized["suggested_action"] = "proceed"
                        normalized["reason"] = f"window precheck accepted by locator title: {window_title[:80]}"
                        return normalized

        history = history or []
        reason = str(observation.get("reason", "") or "")
        current_state = str(observation.get("current_state", "") or "")
        suggested_action = str(observation.get("suggested_action", "") or "")
        joined = f"{reason}\n{current_state}\n{suggested_action}"

        hard_stop_markers = ("扫码登录", "登录失效", "系统错误", "404", "网络异常")
        if any(marker in joined for marker in hard_stop_markers):
            return observation

        publish_markers = ("商品发布", "商品基本信息", "商品标题", "品牌", "价格", "市场价", "京东价")
        recoverable_markers = ("字段校验失败", "填写表单阶段", "fill_product_info", "必填", "请输入")
        last_success_action = next(
            (item.get("action", "") for item in reversed(history) if item.get("success")),
            "",
        )
        is_publish_context = any(marker in joined for marker in publish_markers)
        is_recoverable_fill_state = any(marker in joined for marker in recoverable_markers)
        is_fill_product_info_state = "fill_product_info" in current_state.lower()
        is_recent_fill_flow = last_success_action in {"select_category", "fill_product_info"}

        if action_name == "navigate_to":
            page_state = self._detect_page_state(observation, action_name=action_name)
            navigate_ready_markers = ("商品信息", "商品基本信息", "商品规格", "下一步", "发布商品", "工作台", "类目")
            navigate_positive_markers = (
                "可以继续",
                "可继续",
                "继续后续操作",
                "继续下一步",
                "已成功到达",
                "符合流程正常状态",
                "页面内容完整且可操作",
                "处于商品发布流程中",
            )
            navigate_wrong_markers = ("扫码登录", "登录失败", "404", "网络异常")
            explicit_form_markers = (
                "商品基本信息页",
                "商品基本信息",
                "商品信息填写",
                "商品信息页",
                "商品标题",
                "品牌",
                "价格",
                "类目",
                "下一步，完善其他商品信息",
            )
            if (
                page_state in {"category_page", "product_info_page", "description_page", "publish_confirm_page"}
                or any(marker in joined for marker in navigate_ready_markers)
                or any(marker in joined for marker in navigate_positive_markers)
                or (suggested_action == "navigate_to" and any(marker in joined for marker in explicit_form_markers))
            ) and not any(marker in joined for marker in navigate_wrong_markers):
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["reason"] = "already inside publish workflow; navigate_to accepted current page"
                return normalized

        if action_name == "fill_product_info" and (is_publish_context or is_fill_product_info_state or (is_recent_fill_flow and is_recoverable_fill_state)):
            normalized = dict(observation)
            normalized["status"] = "ok"
            normalized["suggested_action"] = "proceed"
            normalized["reason"] = "仍在发品表单页，允许 fill_product_info 继续执行以修复字段状态"
            return normalized

        if action_name == "fill_product_info" and any(
            marker in joined
            for marker in (
                "可安全继续当前步骤",
                "可以安全继续当前步骤",
                "可继续当前步骤",
                "商品基本信息区域已加载",
                "处于商品基本信息填写步骤",
                "商品信息填写中",
                "商品基本信息填写阶段",
            )
        ):
            normalized = dict(observation)
            normalized["status"] = "ok"
            normalized["suggested_action"] = "proceed"
            normalized["reason"] = "vision precheck explicitly confirms fill_product_info can continue on current form"
            return normalized

        if action_name == "fill_product_info" and self._locator is not None:
            try:
                from actions.form import _classify_fill_page_state

                local_fill_state = _classify_fill_page_state(locator=self._locator, log=self._logger)
            except Exception:
                local_fill_state = "unknown"
            if local_fill_state in {"product_info_page", "sku_table_page"}:
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["page_state"] = local_fill_state
                normalized["reason"] = f"local fill-page probe accepted context for fill_product_info: {local_fill_state}"
                return normalized

        if action_name == "publish_product":
            publish_ready_markers = (
                "发布商品",
                "提交发布",
                "商品标题",
                "品牌",
                "价格",
                "市场价",
                "京东价",
                "商品基本信息",
            )
            wrong_context_markers = ("商品列表", "草稿", "类目", "登录", "扫码", "系统错误")
            if any(marker in joined for marker in publish_ready_markers) and not any(
                marker in joined for marker in wrong_context_markers
            ):
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["reason"] = "仍在发品表单的提交发布阶段，允许 publish_product 继续执行。"
                return normalized

        return self._apply_doc_strict_guard(action_name, step, observation, stage="precheck")

    def _coerce_postcheck_for_action(
        self,
        action_name: str,
        observation: Optional[Dict[str, Any]],
        step: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
        act_result: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        if not isinstance(observation, dict):
            return observation
        if action_name == "fill_product_info":
            local_page_state = self._detect_local_page_state(action_name=action_name)
            observed_page_state = self._detect_page_state(observation, action_name=action_name)
            if local_page_state in {"description_page", "wrong_blank_page"}:
                normalized = dict(observation)
                normalized["status"] = "error"
                normalized["suggested_action"] = "recover"
                normalized["page_state"] = local_page_state
                normalized["reason"] = (
                    "fill_product_info postcheck detected advanced detail editor; should return to merchant backend before retry"
                    if local_page_state == "description_page"
                    else "fill_product_info postcheck detected blank/non-editing state; should recover before retry"
                )
                return self._apply_doc_strict_guard(action_name, step, normalized, stage="postcheck")
            if observed_page_state == "wrong_blank_page":
                normalized = dict(observation)
                normalized["status"] = "error"
                normalized["suggested_action"] = "recover"
                normalized["page_state"] = "wrong_blank_page"
                normalized["reason"] = "fill_product_info postcheck detected blank/non-editing state"
                return self._apply_doc_strict_guard(action_name, step, normalized, stage="postcheck")
            if self._observation_indicates_description_page(observation):
                normalized = dict(observation)
                normalized["status"] = "error"
                normalized["suggested_action"] = "recover"
                normalized["page_state"] = "description_page"
                normalized["reason"] = "fill_product_info postcheck detected advanced detail editor; should return to merchant backend before retry"
                return self._apply_doc_strict_guard(action_name, step, normalized, stage="postcheck")
        if action_name not in {"select_category", "fill_product_info"}:
            return self._apply_doc_strict_guard(action_name, step, observation, stage="postcheck")
        if str(observation.get("status", "unknown") or "unknown").lower() != "error":
            return self._apply_doc_strict_guard(action_name, step, observation, stage="postcheck")

        reason = str(observation.get("reason", "") or "")
        current_state = str(observation.get("current_state", "") or "")
        suggested_action = str(observation.get("suggested_action", "") or "")
        joined = f"{reason}\n{current_state}\n{suggested_action}"
        hard_stop_markers = ("鎵爜鐧诲綍", "鐧诲綍澶辨晥", "绯荤粺閿欒", "404", "缃戠粶寮傚父", "鐧藉睆")
        if any(marker in joined for marker in hard_stop_markers):
            return observation

        if action_name == "select_category":
            action_steps = [str(item or "").strip() for item in ((act_result or {}).get("steps") or []) if str(item or "").strip()]
            if any(marker in action_steps for marker in ("already_past_category", "product_info_ready", "next", "next_retry")):
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["reason"] = f"select_category postcheck accepted action steps: {action_steps}"
                return normalized

            page_state = self._detect_page_state(observation, action_name=action_name)
            product_info_markers = (
                "鍟嗗搧鏍囬",
                "鍝佺墝",
                "浠锋牸",
                "涓嬩竴姝",
                "缂栬緫鍟嗗搧",
                "商品信息页",
                "商品基本信息页",
                "商品信息填写",
                "商品基本信息",
                "已进入商品信息页",
                "商品信息填写内容",
                "title",
                "brand",
                "price",
                "next",
                "edit product",
            )
            if page_state in {"product_info_page", "description_page", "publish_confirm_page"} or any(
                marker in joined for marker in product_info_markers
            ):
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["reason"] = "select_category postcheck accepted product info page"
                return normalized
            category_completion_markers = (
                "已选中目标类目路径",
                "等待完善其他商品信息",
                "类目已选",
                "可继续下一步",
                "准备进入商品信息",
                "商品信息完善步骤",
                "类目已选择",
                "已成功定位至商品类目选择页",
                "category confirmed",
                "selected target category",
                "符合步骤目标要求",
                "符合流程正常状态",
                "页面内容完整且可操作",
                "继续后续操作",
                "可以继续",
            )
            if str(observation.get("page_state", "") or "") == "category_page" and any(
                marker in joined for marker in category_completion_markers
            ):
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["reason"] = "select_category postcheck accepted confirmed category page"
                return normalized

        if action_name == "fill_product_info":
            filled_markers = (
                "鍟嗗搧鏍囬",
                "鍝佺墝",
                "甯傚満浠",
                "浜笢浠",
                "70",
                "title",
                "brand",
                "market price",
                "jd price",
            )
            if any(marker in joined for marker in filled_markers):
                normalized = dict(observation)
                normalized["status"] = "ok"
                normalized["suggested_action"] = "proceed"
                normalized["reason"] = "fill_product_info postcheck accepted populated form"
                return normalized

        return self._apply_doc_strict_guard(action_name, step, observation, stage="postcheck")

    def _apply_doc_strict_guard(
        self,
        action_name: str,
        step: Optional[Dict[str, Any]],
        observation: Optional[Dict[str, Any]],
        stage: str,
    ) -> Optional[Dict[str, Any]]:
        if not isinstance(observation, dict):
            return observation
        if not isinstance(step, dict) or not step.get("doc_strict"):
            return observation

        stage_guard = dict(((step.get("doc_strict_guard") or {}).get(stage, {}) or {}))
        if not stage_guard:
            return observation

        normalized = dict(observation)
        page_state = self._detect_page_state(normalized, action_name=action_name)
        normalized.setdefault("page_state", page_state)
        joined = "\n".join(
            [
                str(normalized.get("reason", "") or ""),
                str(normalized.get("current_state", "") or ""),
                str(normalized.get("suggested_action", "") or ""),
            ]
        )

        reject_markers = [str(item or "").strip() for item in stage_guard.get("reject_markers", []) if str(item or "").strip()]
        if any(marker in joined for marker in reject_markers):
            normalized["status"] = "error"
            normalized["suggested_action"] = str(stage_guard.get("recovery_hint") or step.get("action") or "recover")
            return normalized

        allowed_page_states = [str(item or "").strip() for item in stage_guard.get("allowed_page_states", []) if str(item or "").strip()]
        expanded_allowed_page_states = self._expand_doc_strict_allowed_page_states(
            action_name=action_name,
            stage=stage,
            allowed_page_states=allowed_page_states,
        )
        if expanded_allowed_page_states and page_state not in expanded_allowed_page_states:
            normalized["status"] = "error"
            normalized["reason"] = (
                f"doc-strict {stage} page mismatch for {action_name}: "
                f"expected one of {expanded_allowed_page_states}, got {page_state}"
            )
            normalized["suggested_action"] = str((step.get("doc_strict_guard") or {}).get("recovery_hint") or "recover")
            return normalized

        required_markers = [str(item or "").strip() for item in stage_guard.get("required_markers", []) if str(item or "").strip()]
        if self._doc_strict_page_state_can_bypass_marker_check(
            action_name=action_name,
            stage=stage,
            page_state=page_state,
            allowed_page_states=expanded_allowed_page_states,
        ):
            return normalized
        if required_markers and not any(marker in joined for marker in required_markers):
            normalized["status"] = "error"
            normalized["reason"] = (
                f"doc-strict {stage} markers missing for {action_name}: "
                f"expected any of {required_markers[:4]}"
            )
            normalized["suggested_action"] = str((step.get("doc_strict_guard") or {}).get("recovery_hint") or "recover")
            return normalized

        return normalized

    @staticmethod
    def _expand_doc_strict_allowed_page_states(
        action_name: str,
        stage: str,
        allowed_page_states: List[str],
    ) -> List[str]:
        expanded: List[str] = []
        for state in allowed_page_states or []:
            state_text = str(state or "").strip()
            if state_text and state_text not in expanded:
                expanded.append(state_text)

        if stage == "precheck":
            if action_name == "navigate_to":
                for state in ("category_page", "product_info_page", "description_page", "publish_confirm_page"):
                    if state not in expanded:
                        expanded.append(state)
            if action_name == "select_category":
                for state in ("category_page", "product_info_page", "description_page"):
                    if state not in expanded:
                        expanded.append(state)
            if action_name == "fill_product_info":
                for state in ("product_info_page", "sku_table_page", "description_page", "publish_confirm_page"):
                    if state not in expanded:
                        expanded.append(state)
            if action_name == "publish_product":
                for state in ("product_info_page", "description_page", "publish_confirm_page"):
                    if state not in expanded:
                        expanded.append(state)

        if stage == "postcheck":
            if action_name == "navigate_to":
                for state in ("category_page", "product_info_page", "description_page", "publish_confirm_page"):
                    if state not in expanded:
                        expanded.append(state)
            if action_name == "select_category":
                for state in ("category_page", "product_info_page", "description_page"):
                    if state not in expanded:
                        expanded.append(state)
            if action_name == "fill_product_info":
                for state in ("product_info_page", "sku_table_page", "description_page", "publish_confirm_page"):
                    if state not in expanded:
                        expanded.append(state)
        return expanded

    @staticmethod
    def _doc_strict_page_state_can_bypass_marker_check(
        action_name: str,
        stage: str,
        page_state: str,
        allowed_page_states: List[str],
    ) -> bool:
        if page_state not in set(allowed_page_states or []):
            return False
        return (action_name, stage, page_state) in {
            ("navigate_to", "precheck", "category_page"),
            ("navigate_to", "precheck", "product_info_page"),
            ("navigate_to", "precheck", "description_page"),
            ("navigate_to", "precheck", "publish_confirm_page"),
            ("select_category", "precheck", "category_page"),
            ("select_category", "precheck", "product_info_page"),
            ("select_category", "precheck", "description_page"),
            ("fill_product_info", "precheck", "product_info_page"),
            ("fill_product_info", "precheck", "sku_table_page"),
            ("fill_product_info", "precheck", "description_page"),
            ("fill_product_info", "precheck", "publish_confirm_page"),
            ("publish_product", "precheck", "product_info_page"),
            ("publish_product", "precheck", "description_page"),
            ("publish_product", "precheck", "publish_confirm_page"),
            ("navigate_to", "postcheck", "category_page"),
            ("navigate_to", "postcheck", "product_info_page"),
            ("navigate_to", "postcheck", "description_page"),
            ("navigate_to", "postcheck", "publish_confirm_page"),
            ("select_category", "postcheck", "category_page"),
            ("select_category", "postcheck", "product_info_page"),
            ("select_category", "postcheck", "sku_table_page"),
            ("select_category", "postcheck", "description_page"),
            ("fill_product_info", "postcheck", "sku_table_page"),
            ("fill_product_info", "postcheck", "description_page"),
            ("fill_product_info", "postcheck", "publish_confirm_page"),
        }

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
                                 window_summary: Optional[Dict[str, Any]] = None,
                                 details: Optional[Dict[str, Any]] = None):
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
        if details:
            attempt["details"] = details
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

    def _ensure_video_observer(self):
        if self._video_observer is None and self._locator is not None:
            from infrastructure.video_observer import StepVideoObserver

            self._video_observer = StepVideoObserver(self._locator, self.settings, logger=self._logger)
        return self._video_observer

    def _capture_visual_artifacts(self, step_index: int, action_name: str, stage: str) -> Dict[str, Any]:
        single_path = self._take_screenshot(f"{stage}_{action_name}")
        artifacts = self._step_artifacts.setdefault(step_index, {})
        single_key = f"{stage}_screenshot"
        artifacts[single_key] = single_path or ""

        observer = self._ensure_video_observer()
        if not observer or not observer.enabled:
            return {
                "primary_path": single_path or "",
                "screenshot": single_path or "",
                "contact_sheet": "",
                "frames": [],
                "analysis_paths": [single_path] if single_path else [],
                "frame_count": 0,
                "enabled": False,
            }

        burst = observer.capture_burst(
            task_id=self._task_id,
            step_key=f"step-{step_index:02d}-{action_name}",
            stage=stage,
        )
        artifacts[f"{stage}_video_contact_sheet"] = burst.get("contact_sheet", "") or ""
        artifacts[f"{stage}_video_frames"] = list(burst.get("frames", []) or [])
        artifacts[f"{stage}_video_frame_count"] = int(burst.get("frame_count", 0) or 0)
        primary_path = burst.get("primary_path") or single_path or ""
        analysis_paths = [path for path in [primary_path, single_path] if path]
        frame_paths = list(burst.get("frames", []) or [])
        if frame_paths:
            analysis_paths.extend(frame_paths[:1])
            if len(frame_paths) > 1:
                analysis_paths.append(frame_paths[-1])
        deduped_paths: List[str] = []
        for path in analysis_paths:
            if path and path not in deduped_paths:
                deduped_paths.append(path)
        return {
            "primary_path": primary_path,
            "screenshot": single_path or "",
            "contact_sheet": burst.get("contact_sheet", "") or "",
            "frames": list(burst.get("frames", []) or []),
            "analysis_paths": deduped_paths,
            "frame_count": int(burst.get("frame_count", 0) or 0),
            "enabled": True,
        }

    def _vision_verify(
        self,
        action_name: str,
        screenshot_path: str,
        action_result: Dict[str, Any],
        step: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        调用 LLM 做视觉验证

        Returns:
            dict: {"status": "ok"|"error"|"unknown", "reason": "..."}
        """
        # 注意：以下提示词中提到的"余额已用完"等页面内嵌卡片不算错误
        # 注意：以下提示词中提到的"余额已用完"等页面内嵌卡片不算错误
        contract = (step or {}).get("react_contract") or {}
        postcheck = contract.get("postcheck") or {}
        goal = contract.get("goal") or f"执行 {action_name}"
        workflow_context = contract.get("workflow_context") or {}
        expect_any = [str(item) for item in (postcheck.get("expect_any") or []) if str(item).strip()]
        reject_any = [str(item) for item in (postcheck.get("reject_any") or []) if str(item).strip()]
        recent_history = (history or [])[-3:]
        step_params = (step or {}).get("params") or {}
        product = step_params.get("product") if isinstance(step_params, dict) else {}
        required_visual_fields = step_params.get("required_visual_fields") if isinstance(step_params, dict) else {}
        if not isinstance(product, dict):
            product = {}
        if not isinstance(required_visual_fields, dict):
            required_visual_fields = {}
        key_fields = []
        for field in ("title", "brand", "model", "market_price", "purchase_price", "jd_price"):
            value = product.get(field)
            if value not in (None, ""):
                key_fields.append(f"{field}={value}")
        required_field_labels = []
        for group_name, items in required_visual_fields.items():
            if not isinstance(items, list):
                continue
            labels = [str(item.get("label", "")).strip() for item in items if isinstance(item, dict) and str(item.get("label", "")).strip()]
            if labels:
                required_field_labels.append(f"{group_name}:{labels}")

        action_summary = {
            "success": bool(action_result.get("success", False)),
            "message": action_result.get("message", ""),
            "error": action_result.get("error", ""),
            "failed_fields": action_result.get("failed_fields", []),
            "filled": action_result.get("filled", ""),
            "total": action_result.get("total", ""),
        }
        prompt = ""
        if contract:
            prompt = (
                "分析这张京麦发品截图，判断当前步骤执行后是否达到计划目标。"
                "只返回 JSON: "
                "{\"status\":\"ok\"|\"error\"|\"unknown\","
                "\"reason\":\"原因\","
                "\"current_state\":\"当前页面状态\","
                "\"suggested_action\":\"proceed\"|\"recover\"|\"stop\"}。"
                f"步骤动作: {action_name}。"
                f"步骤目标: {goal}。"
                f"文档上下文: {json.dumps(workflow_context, ensure_ascii=False) if workflow_context else '{}'}。"
                f"成功线索: {expect_any or ['无']}。"
                f"失败或偏差线索: {reject_any or ['无']}。"
                f"关键商品字段: {key_fields or ['无']}。"
                f"动作结果摘要: {json.dumps(action_summary, ensure_ascii=False)}。"
                f"最近历史: {json.dumps(recent_history, ensure_ascii=False)}。"
                "如果仍在正确流程但本步目标没达到，返回 error 并说明偏差；如果截图无法判断，返回 unknown。"
            )
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

        if contract:
            prompt = (
                "分析这张京麦发品截图，判断当前步骤执行后是否达到计划目标。"
                "只返回 JSON: "
                "{\"status\":\"ok\"|\"error\"|\"unknown\","
                "\"reason\":\"原因\","
                "\"current_state\":\"当前页面状态\","
                "\"suggested_action\":\"proceed\"|\"recover\"|\"stop\"}。"
                f"步骤动作: {action_name}。"
                f"步骤目标: {goal}。"
                f"文档上下文: {json.dumps(workflow_context, ensure_ascii=False) if workflow_context else '{}'}。"
                f"成功线索: {expect_any or ['无']}。"
                f"失败或偏差线索: {reject_any or ['无']}。"
                f"关键商品字段: {key_fields or ['无']}。"
                f"动作结果摘要: {json.dumps(action_summary, ensure_ascii=False)}。"
                f"最近历史: {json.dumps(recent_history, ensure_ascii=False)}。"
                "如果仍在正确流程但本步目标没达到，返回 error 并说明偏差；如果截图无法判断，返回 unknown。"
            )

        window_diff = action_result.get("window_diff", {}) or {}
        if window_diff.get("risk_level") == "high":
            risk_hint = window_diff.get("risk_hint", "检测到窗口上下文高风险漂移")
            prompt = (
                f"{risk_hint}。请优先检查是否跳转到了错误窗口、错误页面、错误标签或非京麦发布上下文。"
                f"如果截图显示页面上下文明显不对，应优先返回 error。{prompt}"
            )

        extra_paths = self._extra_visual_paths_from_primary(screenshot_path)
        response = self._llm.invoke_multimodal(prompt, screenshot_path, extra_image_paths=extra_paths)
        if not response:
            return None

        result = self._parse_llm_json_relaxed(response)
        if result is not None:
            return self._normalize_vision_gate_result(result)

        self._log("warning", f"LLM 视觉验证返回非 JSON: {response[:200]}")
        return {"status": "unknown", "reason": f"LLM 返回无法解析: {response[:100]}"}

    def _extra_visual_paths_from_primary(self, screenshot_path: str) -> List[str]:
        for artifacts in self._step_artifacts.values():
            analysis_paths = list(artifacts.get("precheck_video_frames", []) or [])
            analysis_paths.extend(list(artifacts.get("postcheck_video_frames", []) or []))
            contact_sheet = artifacts.get("precheck_video_contact_sheet") or artifacts.get("postcheck_video_contact_sheet")
            if screenshot_path and screenshot_path in {
                artifacts.get("precheck_screenshot"),
                artifacts.get("postcheck_screenshot"),
                contact_sheet,
            }:
                extras: List[str] = []
                if contact_sheet and contact_sheet != screenshot_path:
                    extras.append(contact_sheet)
                for candidate in analysis_paths[:1] + analysis_paths[-1:]:
                    if candidate and candidate != screenshot_path and candidate not in extras:
                        extras.append(candidate)
                return extras
        return []

    def _run_opencli_state_probe(self, reason: str = "") -> Dict[str, Any]:
        import json as _json
        import shutil
        import subprocess
        from pathlib import Path

        prefixes: List[List[str]] = []
        opencli_bin = shutil.which("opencli")
        if opencli_bin:
            prefixes.append([opencli_bin])
        tsx_cmd = Path(r"E:\PY\opencli\node_modules\.bin\tsx.cmd")
        tsx_bin = Path(r"E:\PY\opencli\node_modules\.bin\tsx")
        main_ts = Path(r"E:\PY\opencli\src\main.ts")
        if main_ts.exists():
            if tsx_cmd.exists():
                prefixes.append([str(tsx_cmd), str(main_ts)])
            elif tsx_bin.exists():
                prefixes.append([str(tsx_bin), str(main_ts)])

        if not prefixes:
            return {"success": False, "error": "opencli-not-found", "result": {}}

        session = self._opencli_session or "jingmai-publish-recovery"
        command_sets = [
            ["browser", "--session", session, "state"],
            ["browser", "--session", session, "get", "title"],
            ["browser", "state", "--session", session],
            ["browser", "get", "title", "--session", session],
            ["browser", "state"],
            ["browser", "get", "title"],
        ]
        last_output = ""
        for prefix in prefixes:
            command_results: List[Dict[str, Any]] = []
            successful_outputs: List[str] = []
            for args in command_sets:
                try:
                    completed = subprocess.run(
                        [*prefix, *args],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        timeout=20,
                        check=False,
                    )
                except Exception as exc:
                    command_results.append({"args": args, "success": False, "error": str(exc)})
                    continue
                output = (completed.stdout or completed.stderr or "").strip()
                if output:
                    last_output = output
                command_results.append(
                    {
                        "args": args,
                        "success": completed.returncode == 0,
                        "returncode": completed.returncode,
                        "output": output[:800],
                    }
                )
                if completed.returncode == 0 and output:
                    successful_outputs.append(output)
            if any(item.get("success") for item in command_results):
                raw_probe_text = "\n".join(successful_outputs[-3:]) if successful_outputs else last_output
                return {
                    "success": True,
                    "error": "",
                    "result": {
                        "reason": reason,
                        "session": session,
                        "commands": command_results,
                        "raw_output": raw_probe_text[:1200],
                        "observation": self._parse_opencli_probe_observation(raw_probe_text, reason=reason),
                    },
                }

        parsed: Dict[str, Any] = {}
        try:
            parsed = _json.loads(last_output) if last_output.startswith("{") else {}
        except Exception:
            parsed = {}
        return {
            "success": False,
            "error": parsed.get("error") or last_output[:200] or "opencli-probe-failed",
            "result": {
                "reason": reason,
                "session": session,
                "state": parsed,
                "raw_output": last_output[:1200],
                "observation": self._parse_opencli_probe_observation(last_output, reason=reason),
            },
        }

    def _parse_opencli_probe_observation(self, output: str, reason: str = "") -> Dict[str, Any]:
        text = str(output or "").strip()
        if not text:
            return {"status": "unknown", "reason": f"opencli probe produced no output ({reason or 'unknown'})"}

        parsed: Dict[str, Any] = {}
        if text.startswith("{"):
            try:
                parsed = json.loads(text)
            except Exception:
                parsed = {}

        candidates = [
            str(parsed.get("title", "") or ""),
            str(parsed.get("url", "") or ""),
            str(parsed.get("html", "") or ""),
            str(parsed.get("text", "") or ""),
            text,
        ]
        joined = "\n".join([item for item in candidates if item]).strip()
        page_state = self._detect_page_state({"reason": joined, "current_state": joined, "suggested_action": ""})
        status = "ok" if page_state in {
            "product_list_page",
            "category_page",
            "product_info_page",
            "description_page",
            "publish_confirm_page",
        } else "unknown"
        return {
            "status": status,
            "reason": f"opencli state probe inferred {page_state or 'unknown'}",
            "current_state": joined[:400],
            "suggested_action": "proceed" if status == "ok" else "recover",
            "page_state": page_state,
            "probe_reason": reason,
        }

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
                if step_num in self._step_artifacts:
                    step_copy.update(dict(self._step_artifacts[step_num]))
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
                if step_num in self._step_artifacts:
                    step_copy.update(dict(self._step_artifacts[step_num]))
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
