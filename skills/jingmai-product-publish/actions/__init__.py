"""
京麦商品发布自动化 - Actions Package
导入即触发 @register 装饰器注册
"""
from actions.registry import ActionRegistry, auto_discover
from actions import window, form, popup, navigation, verification

__all__ = ['ActionRegistry', 'auto_discover']
