"""
京麦商品发布自动化 - Planner Agent
LLM 生成执行计划，将商品信息转化为动作序列
"""
import json
import uuid
from typing import Dict, Any, List

from agents.base import BaseAgent
from actions import ActionRegistry


class PlannerAgent(BaseAgent):
    """规划 Agent — 商品信息 → 动作序列"""

    def __init__(self, settings=None):
        super().__init__(name="Planner", settings=settings)

    def run(self, **kwargs) -> Dict[str, Any]:
        """入口 — 生成执行计划"""
        product_data = kwargs.get("product_data", {})
        if not product_data:
            return {"success": False, "error": "缺少商品数据"}

        task_id = kwargs.get("task_id", str(uuid.uuid4())[:8])
        return self.plan(task_id, product_data)

    def plan(self, task_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成执行计划"""
        self.start()
        self._log("info", f"规划任务 {task_id}: {product_data.get('title', '?')[:30]}")

        # 先尝试 LLM 规划
        plan = self._llm_plan(product_data)
        if plan:
            self._log("info", f"LLM 规划成功，{len(plan)} 步")
        else:
            # 降级：基于规则生成模板计划
            plan = self._template_plan(product_data)
            self._log("info", f"使用模板规划，{len(plan)} 步")

        # 验证计划中动作是否有效
        valid_plan = self._validate_plan(plan)

        # 保存到 DB
        if self._db:
            from models import PublishTask
            task = PublishTask(
                task_id=task_id,
                product_id=product_data.get("product_id", ""),
                status="pending",
                plan={"steps": valid_plan},
            )
            self._db.create_task(task)

            # 保存步骤
            for i, step in enumerate(valid_plan):
                from models import TaskStep
                self._db.save_step(TaskStep(
                    task_id=task_id,
                    step_index=i,
                    action_name=step.get("action", ""),
                    params=step.get("params", {}),
                ))

        self._remember(f"任务 {task_id} 规划完成，{len(valid_plan)} 步", importance=0.6, task_id=task_id)
        self.finish(True)
        return {
            "success": True,
            "task_id": task_id,
            "plan": valid_plan,
            "total_steps": len(valid_plan),
        }

    def _llm_plan(self, product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """LLM 生成计划"""
        if not self._llm:
            return []

        # 获取可用动作列表
        actions_summary = ActionRegistry.summary()

        prompt = f"""根据商品信息，生成京麦商品发布的操作步骤。

## 可用动作
{actions_summary}

## 商品信息
{json.dumps(product_data, ensure_ascii=False, indent=2)}

请生成 JSON 格式的操作计划：
{{
  "steps": [
    {{"action": "动作名", "params": {{...}}, "required": true}},
    ...
  ]
}}

注意：
1. 先 find_window 找到京麦窗口
2. 再 navigate_to 进入商品发布页
3. 填写商品信息
4. 最后 publish_product
5. 只使用上面列出的可用动作"""

        try:
            response = self._llm.invoke(prompt)
            data = json.loads(response)
            return data.get("steps", [])
        except Exception as e:
            self._log("warning", f"LLM 规划失败: {e}")
            return []

    def _template_plan(self, product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """模板计划 — 基于商品信息的默认流程"""
        title = product_data.get("title", "")
        price = product_data.get("price", "")
        category = product_data.get("category", "")

        plan = [
            {"action": "find_window", "params": {}, "required": True},
            {"action": "activate_window", "params": {}, "required": True},
        ]

        # 类目选择
        if category:
            plan.append({"action": "select_category", "params": {"category": category}, "required": True})

        # 导航到发布页
        plan.append({"action": "navigate_to", "params": {"target": "publish_page"}, "required": True})

        # 填写基本信息
        if title:
            plan.append({"action": "fill_text", "params": {"field": "title", "value": title}, "required": True})

        # 填写商品详情
        plan.append({
            "action": "fill_product_info",
            "params": {"product_data": product_data},
            "required": True,
        })

        if price:
            plan.append({"action": "fill_text", "params": {"field": "price", "value": str(price)}, "required": True})

        # 发布
        plan.append({"action": "save_draft", "params": {}})
        plan.append({"action": "verify_result", "params": {"expected": "草稿保存成功"}})
        plan.append({"action": "publish_product", "params": {}, "required": True})
        plan.append({"action": "verify_result", "params": {"expected": "发布成功"}})

        return plan

    def _validate_plan(self, plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """验证计划中动作是否已注册"""
        valid = []
        registered = set(ActionRegistry.list_actions())
        for step in plan:
            action = step.get("action", "")
            if action in registered:
                valid.append(step)
            else:
                self._log("warning", f"跳过未注册动作: {action}")
        return valid
