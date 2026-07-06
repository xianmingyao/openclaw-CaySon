"""UIA 后端 — Windows UIAutomation 操作封装。"""

from jm_ufo_agent.backends.uia.controller import UIAController
from jm_ufo_agent.backends.uia.inspector import UIAInspector
from jm_ufo_agent.backends.uia.ui_tree import UITree

__all__ = ["UIAController", "UIAInspector", "UITree"]
