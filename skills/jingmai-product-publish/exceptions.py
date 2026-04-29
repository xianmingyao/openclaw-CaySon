"""
京麦商品发布自动化 - 异常层级体系
"""


class JingmaiError(Exception):
    """基础异常"""
    pass


class WindowNotFoundError(JingmaiError):
    """窗口未找到"""
    pass


class ElementNotFoundError(JingmaiError):
    """元素未找到"""
    pass


class ActionFailedError(JingmaiError):
    """Action 执行失败"""
    pass


class LLMError(JingmaiError):
    """LLM 调用失败"""
    pass


class DatabaseError(JingmaiError):
    """数据库错误"""
    pass


class MemoryError(JingmaiError):
    """记忆系统错误"""
    pass
