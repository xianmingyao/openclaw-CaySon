"""表单完成度评分策略。"""

from __future__ import annotations


class FormCompletionScoreStrategy:
    """计算表单完成度闸门。"""

    def __init__(self, threshold: float = 0.90):
        """初始化完成度阈值。"""

        # threshold 来自配置，默认 90%。
        # 阈值只决定是否允许保存草稿，不修改字段状态。
        # 这里不调用 LLM，保持结果可重复。
        self.threshold = threshold

    def score(self, required_fields: list[str], verified_fields: set[str], blockers: list[str] | None = None) -> tuple[float, bool]:
        """计算完成度分数和是否通过。

        # required_fields 为空时返回 1.0，避免除零。
        # blockers 代表页面不一致、焦点丢失等硬阻断项，有阻断则必定不通过。
        # 分数只由 verified/required 决定，保证重复运行一致。
        """

        if not required_fields:
            return 1.0, not blockers
        completed = len(set(required_fields) & verified_fields)
        value = completed / len(required_fields)
        return value, value >= self.threshold and not blockers
