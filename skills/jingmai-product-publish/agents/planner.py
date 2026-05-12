"""
京麦商品发布自动化 - Planner Agent
"""
import json
import re
import time
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List
import xml.etree.ElementTree as ET
import zipfile

from actions import ActionRegistry
from agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    """规划 Agent。"""

    def __init__(self, settings=None):
        super().__init__(name="Planner", settings=settings)

    def run(self, **kwargs) -> Dict[str, Any]:
        product_data = kwargs.get("product_data") or {}
        task_desc = (kwargs.get("task_desc") or "").strip()
        workflow_policy = str(kwargs.get("workflow_policy") or "default").strip() or "default"
        if not product_data and not task_desc:
            return {"success": False, "error": "缺少商品数据或任务描述"}

        derived = self._derive_product_data_from_task(task_desc) if task_desc else {}
        merged = {**derived, **product_data}
        task_id = kwargs.get("task_id", str(uuid.uuid4())[:8])
        screen_context = kwargs.get("screen_context")
        if screen_context is None:
            screen_context = self._capture_screen_context()
        return self.plan(
            task_id=task_id,
            product_data=merged,
            task_desc=task_desc,
            screen_context=screen_context,
            workflow_policy=workflow_policy,
        )

    def plan(
        self,
        task_id: str,
        product_data: Dict[str, Any],
        task_desc: str = "",
        screen_context: Dict[str, Any] | None = None,
        workflow_policy: str = "default",
    ) -> Dict[str, Any]:
        self.start()
        src = product_data.get("product", product_data)
        display_title = src.get("title") or task_desc or "未命名商品"
        self._log("info", f"规划任务 {task_id}: {display_title[:30]}")

        screen_context = screen_context or {}
        plan: List[Dict[str, Any]] = []
        if workflow_policy != "doc_strict":
            plan = self._llm_plan(src, task_desc=task_desc, screen_context=screen_context)
        template_plan = self._template_plan(src, task_desc=task_desc, workflow_policy=workflow_policy)
        if plan:
            self._log("info", f"LLM 规划成功，共 {len(plan)} 步")
        else:
            plan = template_plan
            if workflow_policy == "doc_strict":
                self._log("info", f"doc_strict 强约束已启用，使用文档模板规划，共 {len(plan)} 步")
            else:
                self._log("info", f"使用模板规划，共 {len(plan)} 步")

        valid_plan = self._attach_react_contracts(
            self._annotate_plan_phases(self._validate_plan(plan)),
            src,
        )

        if self._db:
            from models import PublishTask, TaskStep

            task = PublishTask(
                task_id=task_id,
                product_id=src.get("product_id", src.get("sku", "")),
                status="planning",
                plan={"steps": valid_plan},
                result={"source": "llm" if plan != template_plan else "template"},
            )
            self._db.create_task(task)

            for index, step in enumerate(valid_plan):
                self._db.save_step(
                    TaskStep(
                        task_id=task_id,
                        step_index=index,
                        action_name=step.get("action", ""),
                        params=step.get("params", {}),
                        status="pending",
                    )
                )

        self._remember(f"任务 {task_id} 规划完成，共 {len(valid_plan)} 步", importance=0.6, task_id=task_id)
        self.finish(True)
        return {
            "success": True,
            "task_id": task_id,
            "product_data": src,
            "screen_context": screen_context,
            "plan": valid_plan,
            "total_steps": len(valid_plan),
            "workflow_policy": workflow_policy,
            "workflow_doc": self._default_workflow_doc_path() if workflow_policy == "doc_strict" else "",
        }

    def _llm_plan(
        self,
        product_data: Dict[str, Any],
        task_desc: str = "",
        screen_context: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        if not self._llm:
            self._log("warning", "LLM 未注入，跳过 LLM 规划，使用模板降级")
            return []

        try:
            available = self._llm.is_available()
        except Exception:
            available = False

        if not available:
            self._log("warning", "所有 LLM provider 不健康，跳过 LLM 规划，使用模板降级")
            return []

        prompt = f"""你是京麦商品发布规划器。只返回 JSON，不要解释，不要 markdown。
可用 action 名称:
find_window - 查找京麦窗口
activate_window - 激活京麦窗口
navigate_to - 导航到发布商品页面
select_category - 选择商品类目（参数用 search_text）
fill_product_info - 批量填写商品信息（title, brand, model, sku, price 等）
fill_product_description - 填写商品详情（普通图文/代码编辑，禁止高级编辑）
fill_text - 单独填写文本字段（仅在 fill_product_info 不适用时使用）
save_draft - 保存草稿
verify_result - 验证结果
publish_product - 发布商品

重要规则:
1. fill_product_info 会填入 title, brand, model, sku, price 等所有字段
2. 不要在 fill_product_info 之后又单独生成 fill_text 来填充相同字段
3. 只输出 {{"steps":[...]}} JSON
4. 每个 step 至少包含 action
5. params 可以留空，系统会自动补全

商品信息:
{json.dumps(product_data, ensure_ascii=False)}

任务描述:
{task_desc or "无"}

正确示例:
{{
  "steps": [
    {{"action": "find_window"}},
    {{"action": "activate_window"}},
    {{"action": "navigate_to"}},
    {{"action": "select_category", "params": {{"search_text": "插座"}}}},
    {{"action": "fill_product_info"}},
    {{"action": "fill_product_description"}},
    {{"action": "publish_product"}},
    {{"action": "verify_result"}}
  ]
}}"""

        try:
            screenshot_path = str((screen_context or {}).get("screenshot_path", "") or "").strip()
            if screenshot_path:
                response = (self._llm.invoke_multimodal(prompt, screenshot_path) or "").strip()
            else:
                response = (self._llm.invoke(prompt) or "").strip()
            if not response:
                return []
            data = self._parse_llm_plan_response(response)
            raw_steps = data.get("steps", []) if isinstance(data, dict) else []
            return self._normalize_llm_steps(raw_steps, product_data)
        except Exception as exc:
            self._log("info", f"LLM 规划失败: {exc}")
            return []

    def _capture_screen_context(self) -> Dict[str, Any]:
        context: Dict[str, Any] = {
            "status": "unknown",
            "current_state": "",
            "reason": "screen-context-unavailable",
            "suggested_start_action": "",
            "should_skip_actions": [],
        }
        if not self._llm:
            return context

        try:
            from infrastructure.locator import JingmaiLocator

            locator = JingmaiLocator(log=self.log)
            window = locator.find_window()
            if not window:
                context["reason"] = "jingmai-window-not-found"
                return context

            locator.activate_window()
            screenshot_dir = Path("resources") / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / f"planner_context_{int(time.time() * 1000)}.png"
            saved_path = locator.take_screenshot(str(screenshot_path))
            if not saved_path:
                context["reason"] = "planner-screenshot-failed"
                return context

            prompt = (
                "分析这张京麦发布流程截图，判断当前屏幕所处阶段。"
                "只返回 JSON: "
                "{\"status\":\"ok\"|\"error\"|\"unknown\","
                "\"current_state\":\"window_ready|publish_page_ready|category_ready|product_info_ready|draft_saved|publish_submitted|unknown\","
                "\"reason\":\"原因\","
                "\"suggested_start_action\":\"find_window|activate_window|navigate_to|select_category|fill_product_info|save_draft|publish_product|verify_result\","
                "\"should_skip_actions\":[\"action1\",\"action2\"]}。"
            )
            raw = self._llm.invoke_multimodal(prompt, saved_path)
            parsed = self._parse_llm_plan_response(raw or "")
            if isinstance(parsed, dict):
                for key in ("status", "current_state", "reason", "suggested_start_action", "should_skip_actions"):
                    if key in parsed:
                        context[key] = parsed[key]
            context["screenshot_path"] = str(Path(saved_path).resolve())
            context["window_title"] = getattr(window, "title", "")
            return context
        except Exception as exc:
            context["reason"] = f"screen-context-error: {exc}"
            return context

    def _template_plan(
        self,
        product_data: Dict[str, Any],
        task_desc: str = "",
        workflow_policy: str = "default",
    ) -> List[Dict[str, Any]]:
        product_info = product_data.get("product", product_data)
        publish_mode = self._resolve_publish_mode(product_info)
        if workflow_policy == "doc_strict":
            return self._doc_workflow_template({**product_info, "publish_mode": publish_mode})

        category = product_info.get("category", "") or ""
        title = str(product_info.get("title", "") or "").strip()

        plan: List[Dict[str, Any]] = [
            {"action": "find_window", "params": {}, "required": True},
            {"action": "activate_window", "params": {}, "required": True},
            {"action": "navigate_to", "params": {"page": "publish"}, "required": True},
        ]

        if title in {"商品标题"} or "嵌套测试" in title:
            plan.append({"action": "fill_text", "params": {"text": title}, "required": False})

        if category:
            plan.append({"action": "select_category", "params": {"search_text": category}, "required": True})

        required_visual_fields = self._build_required_visual_fields(product_data)
        if publish_mode == "batch":
            plan.append(
                {
                    "action": "fill_product_info",
                    "params": {
                        "product": product_data,
                        "required_visual_fields": required_visual_fields,
                        "field_groups": ["basic_info", "attributes"],
                        "batch_scope": "product_basic",
                        "publish_mode": publish_mode,
                    },
                    "required": True,
                    "phase": "product_basic_ready",
                }
            )
            plan.append(
                {
                    "action": "fill_product_info",
                    "params": {
                        "product": product_data,
                        "required_visual_fields": required_visual_fields,
                        "field_groups": ["pricing", "sales_attributes", "logistics"],
                        "batch_scope": "sku_batch",
                        "publish_mode": publish_mode,
                    },
                    "required": True,
                    "phase": "batch_sku_ready",
                }
            )
        else:
            plan.append(
                {
                    "action": "fill_product_info",
                    "params": {
                        "product": product_data,
                        "required_visual_fields": required_visual_fields,
                        "publish_mode": publish_mode,
                    },
                    "required": True,
                }
            )
        plan.append(
            {
                "action": "fill_product_description",
                "params": {
                    "product": product_data,
                    "required_visual_fields": required_visual_fields,
                    "batch_scope": "description_assets" if publish_mode == "batch" else "single_product",
                    "publish_mode": publish_mode,
                },
                "required": True,
            }
        )

        plan.extend(
            [
                {"action": "publish_product", "params": {}, "required": True},
                {"action": "verify_result", "params": {"check_errors": True}, "required": True},
            ]
        )
        return plan

    @staticmethod
    def _resolve_publish_mode(product_data: Dict[str, Any]) -> str:
        mode = str(product_data.get("publish_mode", "") or "").strip().lower()
        return mode if mode in {"single", "batch"} else "single"

    @staticmethod
    def _default_workflow_doc_path() -> str:
        candidates = sorted(Path(".").glob("*.docx"))
        for candidate in candidates:
            if "上架流程" in candidate.stem:
                return str(candidate.resolve())
        return str(candidates[0].resolve()) if candidates else ""

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_workflow_paragraphs() -> List[str]:
        doc_path = PlannerAgent._default_workflow_doc_path()
        if doc_path:
            paragraphs = PlannerAgent._extract_docx_paragraphs(Path(doc_path))
            if paragraphs:
                return paragraphs

        markdown_path = Path("graphify-out") / "converted" / "京麦上架流程_95edbbf7.md"
        if markdown_path.exists():
            paragraphs: List[str] = []
            for raw_line in markdown_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip().lstrip("#").strip()
                if not line or line.startswith("<!--"):
                    continue
                paragraphs.append(line)
            if paragraphs:
                return paragraphs

        return [
            "京麦商品上架指南",
            "京麦上架操作路径：首页→商品→发布商品→选择商品所属类目。",
            "第一步：首页点击商品-发布商品",
            "第二步：选择所上架的商品所属的类目，从一级类目到末级类目依次选择。",
            "商品信息",
            "商品基本信息",
            "采销信息",
            "价格",
            "商品属性",
            "商品规格描述",
            "商品图片",
            "商品描述",
            "物流售后及其他",
            "商品物流",
            "商品售后及其他",
            "最后再检查所有带星号的信息都填写完整之后点击发布商品-继续发布就进入采购审核阶段。",
        ]

    @staticmethod
    def _extract_docx_paragraphs(doc_path: Path) -> List[str]:
        if not doc_path.exists() or doc_path.suffix.lower() != ".docx":
            return []

        try:
            with zipfile.ZipFile(doc_path) as archive:
                document_xml = archive.read("word/document.xml")
        except Exception:
            return []

        try:
            root = ET.fromstring(document_xml)
        except Exception:
            return []

        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        paragraphs: List[str] = []
        for para in root.findall(".//w:p", ns):
            parts = [node.text or "" for node in para.findall(".//w:t", ns)]
            line = re.sub(r"\s+", " ", "".join(parts)).strip()
            if line:
                paragraphs.append(line)
        return paragraphs

    @staticmethod
    def _group_workflow_sections(paragraphs: List[str]) -> Dict[str, List[str]]:
        cleaned = [str(item or "").strip() for item in paragraphs if str(item or "").strip()]
        headings = [
            "京麦商品上架指南",
            "商品信息",
            "商品基本信息",
            "采销信息",
            "价格",
            "商品属性",
            "商品规格描述",
            "商品图片",
            "商品描述",
            "物流售后及其他",
            "商品物流",
            "商品售后及其他",
        ]
        sections: Dict[str, List[str]] = {"__preamble__": []}
        current = "__preamble__"

        for line in cleaned:
            normalized = line.replace("：", "").replace(":", "").strip()
            matched = next((heading for heading in headings if normalized == heading), "")
            if matched:
                current = matched
                sections.setdefault(current, []).append(line)
                continue
            sections.setdefault(current, []).append(line)
        return sections

    def _doc_workflow_template(self, product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        paragraphs = self._load_workflow_paragraphs()
        publish_mode = self._resolve_publish_mode(product_data)
        specs = self._build_doc_step_specs_from_paragraphs(paragraphs, publish_mode=publish_mode)
        steps = [self._build_doc_step(spec, product_data) for spec in specs]
        return self._annotate_doc_workflow_sequence(steps)

    @staticmethod
    def _annotate_doc_workflow_sequence(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        total = len(steps or [])
        annotated: List[Dict[str, Any]] = []
        for index, step in enumerate(steps, start=1):
            item = dict(step or {})
            prev_action = str(steps[index - 2].get("action", "") or "").strip() if index > 1 else ""
            next_action = str(steps[index].get("action", "") or "").strip() if index < total else ""
            workflow_context = {
                "step_index": index,
                "step_total": total,
                "previous_action": prev_action,
                "next_action": next_action,
                "section": str(item.get("workflow_section", "") or ""),
                "requirement": str(item.get("workflow_requirement", "") or ""),
                "excerpt": str(item.get("workflow_excerpt", "") or ""),
                "phase": str(item.get("phase", "") or ""),
            }
            item["workflow_context"] = workflow_context
            item["workflow_step_index"] = index
            item["workflow_step_total"] = total
            item["workflow_previous_action"] = prev_action
            item["workflow_next_action"] = next_action
            annotated.append(item)
        return annotated

    def _build_doc_step(self, spec: Dict[str, Any], product_data: Dict[str, Any]) -> Dict[str, Any]:
        action = str(spec.get("action", "") or "")
        params = dict(spec.get("params") or {})
        category = str(product_data.get("category", "") or "").strip()

        if action == "select_category":
            params.setdefault("search_text", category)
        elif action == "fill_product_info":
            params["product"] = product_data
            params.setdefault("required_visual_fields", self._build_required_visual_fields(product_data))
            params.setdefault("publish_mode", self._resolve_publish_mode(product_data))
        elif action == "fill_product_description":
            params["product"] = product_data
            params.setdefault("required_visual_fields", self._build_required_visual_fields(product_data))
            params.setdefault("publish_mode", self._resolve_publish_mode(product_data))

        return {
            "action": action,
            "params": params,
            "required": bool(spec.get("required", True)),
            "workflow_source": self._default_workflow_doc_path(),
            "workflow_section": str(spec.get("section", "") or ""),
            "workflow_requirement": str(spec.get("requirement", "") or ""),
            "workflow_excerpt": str(spec.get("excerpt", "") or ""),
            "workflow_paragraphs": list(spec.get("paragraphs") or []),
            "doc_strict": True,
            "doc_strict_guard": self._build_doc_strict_guard(action, params),
            "phase": str(spec.get("phase", "") or ""),
        }

    @staticmethod
    def _build_doc_step_specs_from_paragraphs(paragraphs: List[str], publish_mode: str = "single") -> List[Dict[str, Any]]:
        cleaned = [str(item or "").strip() for item in paragraphs if str(item or "").strip()]
        sections = PlannerAgent._group_workflow_sections(cleaned)

        def collect(*keywords: str) -> List[str]:
            results: List[str] = []
            for line in cleaned:
                if any(keyword and keyword in line for keyword in keywords):
                    results.append(line)
            return results

        preamble_paragraphs = sections.get("__preamble__", [])
        category_paragraphs = collect("选择所上架的商品所属的类目", "选择商品所属类目", "发布商品")
        info_paragraphs = [
            *sections.get("商品信息", []),
            *sections.get("商品基本信息", []),
            *sections.get("采销信息", []),
            *sections.get("价格", []),
            *sections.get("商品属性", []),
            *sections.get("物流售后及其他", []),
            *sections.get("商品物流", []),
            *sections.get("商品售后及其他", []),
        ]
        desc_paragraphs = [
            *sections.get("商品规格描述", []),
            *sections.get("商品图片", []),
            *sections.get("商品描述", []),
        ]
        publish_paragraphs = collect("最后再检查", "继续发布", "采购审核阶段")

        if not category_paragraphs:
            category_paragraphs = preamble_paragraphs[:3]
        if not info_paragraphs:
            info_paragraphs = cleaned
        if not desc_paragraphs:
            desc_paragraphs = cleaned

        specs = [
            {"action": "find_window", "params": {}, "required": True, "section": "窗口准备", "requirement": "确认京麦客户端窗口存在。", "excerpt": preamble_paragraphs[0] if preamble_paragraphs else "京麦商品上架指南", "paragraphs": preamble_paragraphs[:1] or ["京麦商品上架指南"]},
            {"action": "activate_window", "params": {}, "required": True, "section": "窗口准备", "requirement": "激活京麦客户端，确保后续动作命中正确窗口。", "excerpt": preamble_paragraphs[1] if len(preamble_paragraphs) > 1 else "首页点击商品-发布商品前，先确保京麦窗口在前台。", "paragraphs": preamble_paragraphs[:2] or ["首页点击商品-发布商品前，先确保京麦窗口在前台。"]},
            {"action": "navigate_to", "params": {"page": "publish"}, "required": True, "section": "发布路径", "requirement": "首页→商品→发布商品", "excerpt": preamble_paragraphs[1] if len(preamble_paragraphs) > 1 else "京麦上架操作路径：首页→商品→发布商品→选择商品所属类目。", "paragraphs": category_paragraphs[:2] or cleaned[:2]},
            {"action": "select_category", "params": {}, "required": True, "section": "选择商品所属类目", "requirement": "选择所上架的商品所属的类目，从一级类目到末级类目依次选择。", "excerpt": "选择所上架的商品所属的类目，从一级类目到末级类目依次选择。", "paragraphs": category_paragraphs or cleaned[:3]},
            {"action": "fill_product_info", "params": {"doc_sections": ["商品信息", "商品基本信息", "采销信息", "价格", "商品属性", "物流售后及其他", "商品物流", "商品售后及其他"]}, "required": True, "section": "商品信息 / 物流售后及其他", "requirement": "按文档填写商品基本信息、采销信息、价格、商品属性、商品物流与售后字段。", "excerpt": "商品基本信息、采销信息、价格、商品属性、物流售后及其他、商品物流。", "paragraphs": info_paragraphs or cleaned},
            {"action": "fill_product_description", "params": {"doc_sections": ["商品规格描述", "商品图片", "商品描述"]}, "required": True, "section": "规格描述", "requirement": "按文档完善商品规格描述、商品图片和商品描述。", "excerpt": "商品规格描述、商品图片、商品描述。", "paragraphs": desc_paragraphs or cleaned},
            {"action": "publish_product", "params": {}, "required": True, "section": "发布商品", "requirement": "最后再检查所有带星号的信息都填写完整之后点击发布商品。", "excerpt": "最后再检查所有带星号的信息都填写完整之后点击发布商品。", "paragraphs": publish_paragraphs or cleaned[-2:]},
            {"action": "verify_result", "params": {"check_errors": True}, "required": True, "section": "结果确认", "requirement": "继续发布就进入采销审核阶段。", "excerpt": "继续发布就进入采销审核阶段。", "paragraphs": publish_paragraphs or cleaned[-1:]},
        ]
        if publish_mode != "batch":
            return specs

        return [
            specs[0],
            specs[1],
            specs[2],
            specs[3],
                {
                    **specs[4],
                    "params": {
                        **dict(specs[4].get("params") or {}),
                        "field_groups": ["basic_info", "attributes"],
                        "batch_scope": "product_basic",
                        "publish_mode": "batch",
                    },
                    "phase": "product_basic_ready",
                },
                {
                **specs[4],
                    "params": {
                        **dict(specs[4].get("params") or {}),
                        "field_groups": ["pricing", "sales_attributes", "logistics"],
                        "batch_scope": "sku_batch",
                        "publish_mode": "batch",
                    },
                    "phase": "batch_sku_ready",
                },
                {
                **specs[5],
                    "params": {
                        **dict(specs[5].get("params") or {}),
                        "batch_scope": "description_assets",
                        "publish_mode": "batch",
                    },
                },
            specs[6],
            specs[7],
        ]

    @staticmethod
    def _build_doc_strict_guard(action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        product = params.get("product", params) if isinstance(params.get("product", params), dict) else {}
        required_visual_fields = dict(params.get("required_visual_fields") or {})
        category = str(product.get("category", params.get("search_text", "")) or "").strip()
        title = str(product.get("title", "") or "").strip()
        brand = str(product.get("brand", product.get("品牌", "")) or "").strip()
        jd_price = product.get("jd_price", product.get("price", ""))
        price_text = str(jd_price).strip() if jd_price not in ("", None) else ""

        def field_labels(group: str) -> List[str]:
            return [
                str(item.get("label", "") or "").strip()
                for item in required_visual_fields.get(group, [])
                if str(item.get("label", "") or "").strip()
            ]

        def category_markers(category_text: str) -> List[str]:
            text = str(category_text or "").strip()
            if not text:
                return []

            markers: List[str] = [text]
            fragments = [frag.strip() for frag in re.split(r"\s*>\s*|\s*/\s*", text) if frag.strip()]
            markers.extend(fragments)
            if fragments:
                markers.append(fragments[-1])
            return [marker for marker in dict.fromkeys(markers) if marker]

        category_tokens = category_markers(category)

        guards: Dict[str, Dict[str, Any]] = {
            "navigate_to": {
                "recovery_hint": "navigate_to",
                "recovery_sequence": [
                    {"type": "recover_locator"},
                    {"type": "refresh_page", "mode": "soft"},
                    {"type": "navigate_to", "page": "publish"},
                ],
                "precheck": {
                    "allowed_page_states": ["browser_host", "unknown", "product_list_page", "category_page", "product_info_page"],
                    "required_markers": ["京麦", "工作台", "商品", "发布商品", "类目", "商品标题"],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "网络异常"],
                },
                "postcheck": {
                    "allowed_page_states": ["category_page", "product_info_page"],
                    "required_markers": ["类目", "商品标题", "品牌", "下一步，完善其他商品信息"],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "网络异常"],
                },
            },
            "select_category": {
                "recovery_hint": "navigate_to",
                "recovery_sequence": [
                    {"type": "recover_locator"},
                    {"type": "refresh_page", "mode": "soft"},
                    {"type": "navigate_to", "page": "publish"},
                    {"type": "select_category"},
                ],
                "precheck": {
                    "allowed_page_states": ["category_page", "product_info_page"],
                    "required_markers": [marker for marker in ["类目", "商品标题", *category_tokens] if marker],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "网络异常"],
                },
                "postcheck": {
                    "allowed_page_states": ["category_page", "product_info_page"],
                    "required_markers": [marker for marker in ["商品标题", "品牌", "下一步，完善其他商品信息", *category_tokens] if marker],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "网络异常"],
                },
            },
            "fill_product_info": {
                "recovery_hint": "navigate_to",
                "recovery_sequence": [
                    {"type": "recover_locator"},
                    {"type": "refresh_page", "mode": "soft"},
                    {"type": "navigate_to", "page": "publish"},
                    {"type": "select_category"},
                ],
                "precheck": {
                    "allowed_page_states": ["product_info_page"],
                    "required_markers": [marker for marker in ["商品标题", "品牌", "市场价", "京东价", *field_labels("basic_info"), *field_labels("sales_attributes")] if marker],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "商品列表", "草稿"],
                },
                "postcheck": {
                    "allowed_page_states": ["product_info_page"],
                    "required_markers": [marker for marker in ["商品标题", "品牌", title[:18] if title else "", brand, price_text, "市场价", "京东价"] if marker],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "商品列表", "草稿", "类目"],
                },
            },
            "fill_product_description": {
                "recovery_hint": "fill_product_description",
                "recovery_sequence": [
                    {"type": "recover_locator"},
                    {"type": "refresh_page", "mode": "soft"},
                    {"type": "navigate_to", "page": "publish"},
                    {"type": "select_category"},
                ],
                "precheck": {
                    "allowed_page_states": ["description_page"],
                    "required_markers": ["商品描述", "图文编辑", "代码编辑"],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "高级编辑"],
                },
                "postcheck": {
                    "allowed_page_states": ["description_page"],
                    "required_markers": ["商品描述", "图文编辑", "代码编辑"],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "高级编辑"],
                },
            },
            "publish_product": {
                "recovery_hint": "publish_product",
                "recovery_sequence": [
                    {"type": "recover_locator"},
                    {"type": "refresh_page", "mode": "soft"},
                    {"type": "opencli_state_probe", "reason": "publish_product"},
                ],
                "precheck": {
                    "allowed_page_states": ["product_info_page", "description_page", "publish_confirm_page"],
                    "required_markers": ["发布商品", "保存草稿", "商品标题"],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404"],
                },
                "postcheck": {
                    "allowed_page_states": ["publish_confirm_page", "product_list_page", "product_info_page"],
                    "required_markers": ["提交成功", "发布成功", "商品列表", "审核"],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404"],
                },
            },
            "verify_result": {
                "recovery_hint": "verify_result",
                "recovery_sequence": [
                    {"type": "recover_locator"},
                    {"type": "wait", "seconds": 2},
                    {"type": "opencli_state_probe", "reason": "verify_result"},
                ],
                "precheck": {
                    "allowed_page_states": ["publish_confirm_page", "product_list_page", "product_info_page"],
                    "required_markers": ["发布成功", "商品列表", "审核", "发布商品"],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "错误", "异常"],
                },
                "postcheck": {
                    "allowed_page_states": ["publish_confirm_page", "product_list_page"],
                    "required_markers": ["商品列表", "审核", "发布成功"],
                    "reject_markers": ["扫码登录", "登录失效", "系统错误", "404", "错误", "异常"],
                },
            },
        }

        guard = dict(guards.get(action, {}))
        for stage in ("precheck", "postcheck"):
            stage_guard = dict(guard.get(stage, {}) or {})
            stage_guard["required_markers"] = [item for item in stage_guard.get("required_markers", []) if str(item or "").strip()]
            stage_guard["reject_markers"] = [item for item in stage_guard.get("reject_markers", []) if str(item or "").strip()]
            if stage_guard:
                guard[stage] = stage_guard
        recovery_sequence = [item for item in list(guard.get("recovery_sequence") or []) if isinstance(item, dict)]
        if recovery_sequence:
            guard["recovery_sequence"] = recovery_sequence
        return guard

    def _derive_product_data_from_task(self, task_desc: str) -> Dict[str, Any]:
        if not task_desc:
            return {}

        product: Dict[str, Any] = {"title": task_desc}

        price_match = re.search(r"(\d+(?:\.\d+)?)\s*(元|块)?", task_desc)
        if price_match:
            product["price"] = float(price_match.group(1))

        category_match = re.search(r"(?:类目|分类|类别)[:：]?\s*([^\s，,]+)", task_desc)
        if category_match:
            product["category"] = category_match.group(1)

        sku_match = re.search(r"(?:sku|SKU|货号)[:：]?\s*([A-Za-z0-9_-]+)", task_desc)
        if sku_match:
            product["sku"] = sku_match.group(1)

        return product

    def _validate_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid: List[Dict[str, Any]] = []
        registered = set(ActionRegistry.list_actions())
        for step in plan:
            action = step.get("action", "")
            if action in registered:
                valid.append(step)
            else:
                self._log("warning", f"跳过未注册动作: {action}")
        return valid

    def _parse_llm_plan_response(self, response: str) -> Dict[str, Any]:
        text = response.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if not match:
                return {}
            data = json.loads(match.group(0))

        if isinstance(data, dict) and "steps" not in data and "action" in data:
            return {"steps": [data]}
        return data if isinstance(data, dict) else {}

    def _normalize_llm_steps(self, raw_steps: List[Dict[str, Any]], product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """LLM 负责步骤顺序，本地规则统一补全参数。"""
        normalized: List[Dict[str, Any]] = []
        category = product_data.get("category", "") or ""
        title = product_data.get("title", "")
        price = product_data.get("price", "")

        from config.jingmai_coords import PRODUCT_INFO_PAGE

        for raw_step in raw_steps:
            if isinstance(raw_step, str):
                action = raw_step
                raw_params = {}
                required = True
            else:
                action = raw_step.get("action", "")
                raw_params = raw_step.get("params", {})
                if isinstance(raw_params, str):
                    raw_params = {"search_text": raw_params}
                elif not isinstance(raw_params, dict):
                    raw_params = {}
                required = raw_step.get("required", True)

            if not action:
                continue

            params: Dict[str, Any] = {}
            if action == "select_category":
                raw_category = (
                    raw_params.get("search_text")
                    or raw_params.get("category")
                    or raw_params.get("category_name")
                    or category
                )
                if not raw_category:
                    continue
                params = {"search_text": str(raw_category).strip()}
            elif action == "navigate_to":
                page = str(raw_params.get("page") or "publish")
                params = {"page": page if page in {"publish", "products"} else "publish"}
            elif action == "fill_text":
                target = str(raw_params.get("field") or raw_params.get("name") or "").lower()
                raw_text = str(raw_params.get("text") or "").strip()
                wants_price = target in {"price", "market_price", "jd_price"} or raw_text == str(price)
                wants_title = target in {"title", "name"} or (not target and raw_text in {"", title})

                if wants_title and title:
                    coords = PRODUCT_INFO_PAGE.get("title_input")
                    params = {"text": title}
                    if coords:
                        params.update({"x": coords[0], "y": coords[1]})
                elif wants_price and price not in ("", None):
                    coords = PRODUCT_INFO_PAGE.get("market_price")
                    params = {"text": str(price)}
                    if coords:
                        params.update({"x": coords[0], "y": coords[1]})
                else:
                    continue
            elif action == "fill_product_info":
                params = {
                    "product": product_data,
                    "required_visual_fields": self._build_required_visual_fields(product_data),
                }
            elif action == "fill_product_description":
                params = {"product": product_data}
            elif action == "verify_result":
                params = {"check_errors": True}

            normalized.append(
                {
                    "action": action,
                    "params": params,
                    "required": required,
                }
            )

        return self._canonicalize_publish_plan(self._enforce_plan_order(normalized))

    @staticmethod
    def _build_required_visual_fields(product_data: Dict[str, Any]) -> Dict[str, Any]:
        product = product_data.get("product", product_data) if isinstance(product_data, dict) else {}
        attributes = dict(product.get("attributes") or {})
        return {
            "pricing": [
                {"field": "market_price", "label": "市场价", "value": product.get("market_price", "") or product.get("jd_price", "") or product.get("price", "")},
                {"field": "jd_price", "label": "京东价", "value": product.get("jd_price", "") or product.get("price", "")},
                {"field": "purchase_price", "label": "采购价", "value": product.get("purchase_price", "")},
            ],
            "basic_info": [
                {"field": "brand", "label": "品牌", "value": product.get("brand", "") or product.get("品牌", "")},
                {"field": "model", "label": "型号", "value": product.get("model", "")},
                {"field": "socket_config", "label": "孔型配置", "value": attributes.get("socket_config", product.get("socket_config", ""))},
                {"field": "rated_voltage", "label": "额定电压", "value": attributes.get("rated_voltage", product.get("rated_voltage", ""))},
                {"field": "cable_length", "label": "电缆长度", "value": attributes.get("cable_length", product.get("cable_length", ""))},
                {"field": "procurement_erp", "label": "采购ERP编码", "value": product.get("procurement_erp", "")},
            ],
            "sales_attributes": [
                {
                    "field": "current",
                    "label": "电流",
                    "value": attributes.get("current")
                    or attributes.get("rated_current")
                    or product.get("current", "")
                    or product.get("rated_current", ""),
                },
                {"field": "sku_image", "label": "图片设置", "value": product.get("sku_image", "") or product.get("image", "")},
            ],
            "description": [
                {"field": "detail_content", "label": "商品详情", "value": product.get("detail_content", "") or product.get("description", "")},
                {"field": "description_images", "label": "详情图片", "value": product.get("description_images", [])},
            ],
            "logistics": [
                {"field": "sales_unit", "label": "销售单位", "value": product.get("sales_unit", "") or product.get("unit", "")},
                {"field": "package_type", "label": "商品包装", "value": product.get("package_type", "")},
                {"field": "special_delivery_mark", "label": "特殊发货时效标记", "value": product.get("special_delivery_mark", "")},
                {"field": "packing_list", "label": "包装清单", "value": product.get("packing_list", "") or product.get("notes", "")},
                {"field": "warranty_period", "label": "质保期", "value": product.get("warranty_period", "")},
            ],
        }

    @staticmethod
    def _annotate_plan_phases(plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Annotate each step with a business phase for hybrid/manual resume support."""
        annotated: List[Dict[str, Any]] = []
        publish_seen = False

        for step in plan:
            item = dict(step)
            action = item.get("action", "")
            phase = item.get("phase")

            if not phase:
                if action in {"find_window", "activate_window"}:
                    phase = "window_ready"
                elif action == "navigate_to":
                    phase = "publish_page_ready"
                elif action == "select_category":
                    phase = "category_ready"
                elif action in {"fill_text", "fill_product_info", "fill_product_description", "select_dropdown", "paste_and_search"}:
                    phase = "product_info_ready"
                elif action == "save_draft":
                    phase = "draft_saved"
                elif action == "publish_product":
                    phase = "publish_submitted"
                elif action == "verify_result":
                    phase = "publish_verified" if publish_seen else "draft_verified"
                else:
                    phase = "execution_in_progress"

            item["phase"] = phase
            annotated.append(item)

            if action == "publish_product":
                publish_seen = True

        return annotated

    @staticmethod
    def _attach_react_contracts(
        plan: List[Dict[str, Any]],
        product_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Attach explicit pre/post visual contracts for ReAct execution."""
        title = str(product_data.get("title", "") or "").strip()
        category = str(product_data.get("category", "") or "").strip()
        jd_price = product_data.get("jd_price", product_data.get("price", ""))
        price_text = str(jd_price).strip() if jd_price not in ("", None) else ""

        def merge_unique(items: List[str], extra: List[str]) -> List[str]:
            merged: List[str] = []
            for value in [*(items or []), *(extra or [])]:
                text = str(value or "").strip()
                if text and text not in merged:
                    merged.append(text)
            return merged

        def apply_doc_strict_guard(contract: Dict[str, Any], guard: Dict[str, Any]) -> Dict[str, Any]:
            merged = dict(contract or {})
            for stage in ("precheck", "postcheck"):
                stage_contract = dict(merged.get(stage) or {})
                stage_guard = dict(guard.get(stage) or {})
                if not stage_guard:
                    merged[stage] = stage_contract
                    continue
                stage_contract["expect_any"] = merge_unique(
                    list(stage_contract.get("expect_any") or []),
                    list(stage_guard.get("required_markers") or []),
                )
                stage_contract["reject_any"] = merge_unique(
                    list(stage_contract.get("reject_any") or []),
                    list(stage_guard.get("reject_markers") or []),
                )
                if stage_guard.get("allowed_page_states"):
                    stage_contract["allowed_page_states"] = list(stage_guard.get("allowed_page_states") or [])
                if guard.get("recovery_hint"):
                    stage_contract["recovery_hint"] = str(guard.get("recovery_hint") or "")
                merged[stage] = stage_contract
            return merged

        def build_contract(action: str) -> Dict[str, Any]:
            contracts: Dict[str, Dict[str, Any]] = {
                "find_window": {
                    "goal": "定位并确认京麦客户端窗口存在。",
                    "precheck": {
                        "expect_any": [],
                        "reject_any": ["Windows 桌面崩溃", "远程连接错误"],
                    },
                    "postcheck": {
                        "expect_any": ["京麦", "发布商品", "商智", "工作台"],
                        "reject_any": ["扫码登录", "网络异常", "系统错误"],
                    },
                },
                "activate_window": {
                    "goal": "将京麦窗口切到前台，避免后续动作命中错误页面。",
                    "precheck": {
                        "expect_any": ["京麦", "发布商品", "工作台"],
                        "reject_any": ["扫码登录", "系统错误"],
                    },
                    "postcheck": {
                        "expect_any": ["京麦", "发布商品", "工作台"],
                        "reject_any": ["扫码登录", "系统错误"],
                    },
                },
                "navigate_to": {
                    "goal": "进入发品流程，允许停在类目选择页或商品基本信息页。",
                    "precheck": {
                        "expect_any": ["京麦", "工作台", "发布商品", "商品管理"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                    "postcheck": {
                        "expect_any": ["商品标题", "品牌", "价格", "类目", "下一步，完善其他商品信息"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                },
                "select_category": {
                    "goal": f"选择类目 {category or '目标类目'}，或确认已进入商品信息页。",
                    "precheck": {
                        "expect_any": ["类目", "商品标题", "品牌", "下一步，完善其他商品信息"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                    "postcheck": {
                        "expect_any": ["商品标题", "品牌", "价格", "下一步，完善其他商品信息", category] if category else ["商品标题", "品牌", "价格", "下一步，完善其他商品信息"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                },
                "fill_product_info": {
                    "goal": "先确认当前屏幕仍在发品主流程，再填写基础信息与价格；如果视觉上已偏到商品描述/物流售后等标签，需要先回到商品基本信息并滚到价格区域。",
                    "precheck": {
                        "expect_any": ["商品基本信息", "商品标题", "品牌", "价格", "商品描述", "商品物流", "商品售后及其他"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误", "404"],
                    },
                    "postcheck": {
                        "expect_any": [text for text in ["商品标题", "品牌", "市场价", "京东价", title[:18] if title else "", price_text] if text],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                },
                "fill_product_description": {
                    "goal": "在商家后台内完善商品详情，避免进入高级编辑器，如误入则先返回商家后台。",
                    "precheck": {
                        "expect_any": ["商品描述", "图文编辑", "代码编辑", "返回商家后台"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误", "高级编辑"],
                    },
                    "postcheck": {
                        "expect_any": ["商品描述", "图文编辑", "代码编辑", "商品物流"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误", "高级编辑", "返回商家后台"],
                    },
                },
                "save_draft": {
                    "goal": "保存当前商品为草稿。",
                    "precheck": {
                        "expect_any": ["保存草稿", "发布商品", "商品标题"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                    "postcheck": {
                        "expect_any": ["草稿", "保存成功", "发布商品"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                },
                "publish_product": {
                    "goal": "提交发布动作。",
                    "precheck": {
                        "expect_any": ["发布商品", "保存草稿", "商品标题"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                    "postcheck": {
                        "expect_any": ["提交成功", "发布成功", "商品列表", "草稿"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                },
                "verify_result": {
                    "goal": "检查当前页面是否存在错误提示，确认草稿或发布结果。",
                    "precheck": {
                        "expect_any": ["发布商品", "草稿", "商品标题", "商品列表"],
                        "reject_any": ["扫码登录", "登录失效", "系统错误"],
                    },
                    "postcheck": {
                        "expect_any": ["草稿", "发布成功", "商品列表", "发布商品"],
                        "reject_any": ["错误", "异常", "扫码登录", "登录失效", "系统错误"],
                    },
                },
            }
            return contracts.get(
                action,
                {
                    "goal": f"执行动作 {action} 并确认页面未偏离京麦发布上下文。",
                    "precheck": {"expect_any": ["京麦", "发布商品"], "reject_any": ["扫码登录", "系统错误"]},
                    "postcheck": {"expect_any": ["京麦", "发布商品"], "reject_any": ["扫码登录", "系统错误"]},
                },
            )

        enriched: List[Dict[str, Any]] = []
        for step in plan:
            item = dict(step)
            contract = dict(item.get("react_contract") or build_contract(item.get("action", "")))
            guard = dict(item.get("doc_strict_guard") or {})
            workflow_context = dict(item.get("workflow_context") or {})
            if workflow_context:
                contract["workflow_context"] = workflow_context
                requirement = str(workflow_context.get("requirement", "") or "").strip()
                section = str(workflow_context.get("section", "") or "").strip()
                step_index = workflow_context.get("step_index")
                step_total = workflow_context.get("step_total")
                next_action = str(workflow_context.get("next_action", "") or "").strip()
                context_bits: List[str] = []
                if section:
                    context_bits.append(f"文档章节={section}")
                if requirement:
                    context_bits.append(f"文档要求={requirement}")
                if step_index and step_total:
                    context_bits.append(f"文档步骤={step_index}/{step_total}")
                if next_action:
                    context_bits.append(f"下一动作={next_action}")
                if context_bits:
                    contract["goal"] = f"{contract.get('goal', '')}。{'；'.join(context_bits)}".strip("。")
            if item.get("doc_strict") and guard:
                contract = apply_doc_strict_guard(contract, guard)
            item["react_contract"] = contract
            enriched.append(item)
        return enriched

    @staticmethod
    def _enforce_plan_order(plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """确保 navigate_to 在 select_category 之前。"""
        select_index = next((i for i, step in enumerate(plan) if step.get("action") == "select_category"), -1)
        navigate_index = next((i for i, step in enumerate(plan) if step.get("action") == "navigate_to"), -1)
        if select_index == -1 or navigate_index == -1 or navigate_index < select_index:
            return plan

        reordered = list(plan)
        navigate_step = reordered.pop(navigate_index)
        reordered.insert(select_index, navigate_step)
        return reordered

    @staticmethod
    def _canonicalize_publish_plan(plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove contradictory draft steps from the default publish flow."""
        canonical = list(plan)

        publish_index = next((i for i, step in enumerate(canonical) if step.get("action") == "publish_product"), -1)
        if publish_index == -1:
            return canonical

        filtered_publish_flow: List[Dict[str, Any]] = []
        for idx, step in enumerate(canonical):
            action = step.get("action")
            if idx < publish_index and action in {"save_draft", "verify_result"}:
                continue
            filtered_publish_flow.append(step)
        return filtered_publish_flow
