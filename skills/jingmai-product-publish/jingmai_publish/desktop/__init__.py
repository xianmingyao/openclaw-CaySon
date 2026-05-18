"""Windows 桌面自动化适配层。"""

from .adapter import DesktopAutomationAdapter, WindowInfo
from .uia_adapter import RealWindowsUIAAdapter, UIATuningConfig
from .window_manager import WindowManager

__all__ = ["DesktopAutomationAdapter", "RealWindowsUIAAdapter", "UIATuningConfig", "WindowInfo", "WindowManager"]
