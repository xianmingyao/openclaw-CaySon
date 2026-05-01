"""
京麦商品发布自动化 - Planner Agent
"""
import json
import re
import uuid
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
        return self.plan(task_id=task_id, product_data=merged, task_desc=task_desc)

    def plan(self, task_id: str, product_data: Dict[str, Any], task_desc: str = "") -> Dict[str, Any]:
        self.start()
        src = product_data.get("product", product_data)
        display_title = src.get("title") or task_desc or "未命名商品"
        self._log("info", f"规划任务 {task_id}: {display_title[:30]}")

        plan = self._llm_plan(src, task_desc=task_desc)
        template_plan = self._template_plan(src, task_desc=task_desc)
        if plan:
            self._log("info", f"LLM 规划成功，共 {len(plan)} 步")
        else:
            plan = template_plan
            self._log("info", f"使用模板规划，共 {len(plan)} 步")

        valid_plan = self._validate_plan(plan)

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
            "plan": valid_plan,
            "total_steps": len(valid_plan),
        }

    def _llm_plan(self, product_data: Dict[str, Any], task_desc: str = "") -> List[Dict[str, Any]]:
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
    {{"action": "save_draft"}},
    {{"action": "verify_result"}},
    {{"action": "publish_product"}}
  ]
}}"""

        try:
            response = (self._llm.invoke(prompt) or "").strip()
            if not response:
                return []
            data = self._parse_llm_plan_response(response)
            raw_steps = data.get("steps", []) if isinstance(data, dict) else []
            return self._normalize_llm_steps(raw_steps, product_data)
        except Exception as exc:
            self._log("info", f"LLM 规划失败: {exc}")
            return []

    def _template_plan(self, product_data: Dict[str, Any], task_desc: str = "") -> List[Dict[str, Any]]:
        product_info = product_data.get("product", product_data)
        title = product_info.get("title", "") or task_desc
        price = product_info.get("price", "")
        category = product_info.get("category", "") or ""

        plan: List[Dict[str, Any]] = [
            {"action": "find_window", "params": {}, "required": True},
            {"action": "activate_window", "params": {}, "required": True},
            {"action": "navigate_to", "params": {"page": "publish"}, "required": True},
        ]

        if category:
            plan.append({"action": "select_category", "params": {"search_text": category}, "required": True})

        if title:
            from config.jingmai_coords import PRODUCT_INFO_PAGE

            title_coords = PRODUCT_INFO_PAGE.get("title_input")
            params = {"text": title}
            if title_coords:
                params.update({"x": title_coords[0], "y": title_coords[1]})
            plan.append({"action": "fill_text", "params": params, "required": True})

        plan.append({"action": "fill_product_info", "params": {"product": product_data}, "required": True})

        if price not in ("", None):
            from config.jingmai_coords import PRODUCT_INFO_PAGE

            price_coords = PRODUCT_INFO_PAGE.get("market_price")
            params = {"text": str(price)}
            if price_coords:
                params.update({"x": price_coords[0], "y": price_coords[1]})
            plan.append({"action": "fill_text", "params": params, "required": True})

        plan.extend(
            [
                {"action": "save_draft", "params": {}, "required": False},
                {"action": "verify_result", "params": {"check_errors": True}, "required": False},
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

        return self._enforce_plan_order(normalized)

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
