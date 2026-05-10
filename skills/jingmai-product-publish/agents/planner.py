"""
京麦商品发布自动化 - Planner Agent
"""
import json
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

from actions import ActionRegistry
from agents.base import BaseAgent


class PlannerAgent(BaseAgent):
    """规划 Agent。"""

    def __init__(self, settings=None):
        super().__init__(name="Planner", settings=settings)

    def run(self, **kwargs) -> Dict[str, Any]:
        product_data = kwargs.get("product_data") or {}
        task_desc = (kwargs.get("task_desc") or "").strip()
        if not product_data and not task_desc:
            return {"success": False, "error": "缺少商品数据或任务描述"}

        derived = self._derive_product_data_from_task(task_desc) if task_desc else {}
        merged = {**derived, **product_data}
        task_id = kwargs.get("task_id", str(uuid.uuid4())[:8])
        screen_context = kwargs.get("screen_context")
        if screen_context is None:
            screen_context = self._capture_screen_context()
        return self.plan(task_id=task_id, product_data=merged, task_desc=task_desc, screen_context=screen_context)

    def plan(
        self,
        task_id: str,
        product_data: Dict[str, Any],
        task_desc: str = "",
        screen_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        self.start()
        src = product_data.get("product", product_data)
        display_title = src.get("title") or task_desc or "未命名商品"
        self._log("info", f"规划任务 {task_id}: {display_title[:30]}")

        screen_context = screen_context or {}
        plan = self._llm_plan(src, task_desc=task_desc, screen_context=screen_context)
        template_plan = self._template_plan(src, task_desc=task_desc)
        if plan:
            self._log("info", f"LLM 规划成功，共 {len(plan)} 步")
        else:
            plan = template_plan
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

    def _template_plan(self, product_data: Dict[str, Any], task_desc: str = "") -> List[Dict[str, Any]]:
        product_info = product_data.get("product", product_data)
        category = product_info.get("category", "") or ""

        plan: List[Dict[str, Any]] = [
            {"action": "find_window", "params": {}, "required": True},
            {"action": "activate_window", "params": {}, "required": True},
            {"action": "navigate_to", "params": {"page": "publish"}, "required": True},
        ]

        if category:
            plan.append({"action": "select_category", "params": {"search_text": category}, "required": True})

        plan.append(
            {
                "action": "fill_product_info",
                "params": {
                    "product": product_data,
                    "required_visual_fields": self._build_required_visual_fields(product_data),
                },
                "required": True,
            }
        )
        plan.append({"action": "fill_product_description", "params": {"product": product_data}, "required": True})

        plan.extend(
            [
                {"action": "publish_product", "params": {}, "required": True},
                {"action": "verify_result", "params": {"check_errors": True}, "required": True},
            ]
        )
        return plan

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
            "basic_info": [
                {"field": "brand", "label": "品牌", "value": product.get("brand", "") or product.get("品牌", "")},
                {"field": "model", "label": "型号", "value": product.get("model", "")},
                {"field": "socket_config", "label": "孔型配置", "value": attributes.get("socket_config", product.get("socket_config", ""))},
                {"field": "rated_voltage", "label": "额定电压", "value": attributes.get("rated_voltage", product.get("rated_voltage", ""))},
                {"field": "cable_length", "label": "电缆长度", "value": attributes.get("cable_length", product.get("cable_length", ""))},
            ],
            "sales_attributes": [
                {"field": "current", "label": "电流", "value": attributes.get("current", product.get("current", ""))},
                {"field": "sku_image", "label": "图片设置", "value": product.get("sku_image", "") or product.get("image", "")},
            ],
            "description": [
                {"field": "detail_content", "label": "商品详情", "value": product.get("detail_content", "") or product.get("description", "")},
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
                    "goal": "鍦ㄥ晢瀹跺悗鍙板唴瀹岀粨鍟嗗搧璇︽儏锛岄伩鍏嶈繘鍏ラ珮绾х紪杈戝櫒锛屽宸茶鍏ラ珮绾х紪杈戝櫒鍒欏厛杩斿洖鍟嗗鍚庡彴銆?",
                    "precheck": {
                        "expect_any": ["鍟嗗搧鎻忚堪", "鍥炬枃缂栬緫", "浠ｇ爜缂栬緫", "楂樼骇缂栬緫", "杩斿洖鍟嗗鍚庡彴"],
                        "reject_any": ["鎵爜鐧诲綍", "鐧诲綍澶辨晥", "绯荤粺閿欒"],
                    },
                    "postcheck": {
                        "expect_any": ["鍟嗗搧鎻忚堪", "鍥炬枃缂栬緫", "浠ｇ爜缂栬緫", "鍟嗗搧鐗╂祦"],
                        "reject_any": ["鎵爜鐧诲綍", "鐧诲綍澶辨晥", "绯荤粺閿欒", "杩斿洖鍟嗗鍚庡彴"],
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
            item.setdefault("react_contract", build_contract(item.get("action", "")))
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
