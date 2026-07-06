"""UFO v1 底层能力审计。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class UfoCapabilityReport:
    """UFO v1 可适配能力报告。"""

    ufo_root: str
    root_exists: bool
    source_files: dict[str, str]
    existing_files: dict[str, bool]
    capabilities: dict[str, bool]
    missing_capabilities: list[str] = field(default_factory=list)

    def ready_for_observe(self) -> bool:
        """判断是否至少具备真实窗口观察能力。"""

        # observe 模式只允许窗口事实识别、截图、控件树读取，不允许点击和填写。
        # 这里把“UFO 目录存在”和“关键文件存在”分开判断，避免误报生产可用。
        # 后续 CLI 可以用该结果决定是否允许 inspect-jingmai-window 进入真实 backend。
        required = ("controller", "inspector", "screenshot", "ui_tree")
        return self.root_exists and all(self.capabilities.get(name, False) for name in required)

    def ready_for_write(self) -> bool:
        """判断是否具备真实写操作所需的最小来源能力。"""

        # 写操作必须在 observe 能力之外再具备 action_execution。
        # 即便返回 True，也只说明 UFO v1 有可适配来源，不代表当前进程允许写京麦。
        # 真正写入仍要经过 SafetyPolicy、allow_write 和用户显式确认。
        return self.ready_for_observe() and self.capabilities.get("action_execution", False)

    def to_dict(self) -> dict[str, Any]:
        """转换为可输出、可落库的 JSON 字典。"""

        # source_files 用于审计“能力来自 UFO 的哪个文件”。
        # existing_files 用于快速定位缺失安装或路径错误。
        # capabilities 用于 production readiness 和小批量验收前置门禁。
        return {
            "ufo_root": self.ufo_root,
            "root_exists": self.root_exists,
            "source_files": dict(self.source_files),
            "existing_files": dict(self.existing_files),
            "capabilities": dict(self.capabilities),
            "missing_capabilities": list(self.missing_capabilities),
            "ready_for_observe": self.ready_for_observe(),
            "ready_for_write": self.ready_for_write(),
        }


class UfoCapabilityScanner:
    """扫描本机 UFO v1 源码并生成能力报告。"""

    def __init__(self, ufo_root: Path = Path("E:/PY/UFO/ufo")):
        """保存 UFO v1 根目录。"""

        # 构造函数只保存路径，不 import UFO 包，避免触发它的全局初始化副作用。
        # 测试可以传入 tmp_path 构造假的 UFO 目录。
        # 真实运行默认读取设计文档指定的 E:/PY/UFO/ufo。
        self.ufo_root = Path(ufo_root)

    def source_files(self) -> dict[str, str]:
        """返回 v2 需要适配的 UFO v1 来源文件。"""

        # 这些文件覆盖动作执行、UI 控制、窗口检查、截图和控件树。
        # 只暴露文件映射，不复制代码，便于先做能力审计。
        # 路径统一转成字符串，方便 CLI JSON 输出。
        return {
            "action_execution": str(self.ufo_root / "automator" / "action_execution.py"),
            "controller": str(self.ufo_root / "automator" / "ui_control" / "controller.py"),
            "inspector": str(self.ufo_root / "automator" / "ui_control" / "inspector.py"),
            "screenshot": str(self.ufo_root / "automator" / "ui_control" / "screenshot.py"),
            "ui_tree": str(self.ufo_root / "automator" / "ui_control" / "ui_tree.py"),
            "path_validator": str(self.ufo_root / "automator" / "path_validator.py"),
            "puppeteer": str(self.ufo_root / "automator" / "puppeteer.py"),
        }

    def scan(self) -> UfoCapabilityReport:
        """扫描 UFO v1 文件并生成能力状态。"""

        # 文件存在性是第一层证据，确保后续适配不是空中楼阁。
        # clipboard/native_dialog 使用关键词和候选文件做保守推断。
        # 缺失项不会抛异常，而是进入 missing_capabilities，方便生产 readiness 汇总。
        source_files = self.source_files()
        existing_files = {name: Path(path).exists() for name, path in source_files.items()}
        capabilities = {
            "action_execution": existing_files["action_execution"],
            "controller": existing_files["controller"],
            "inspector": existing_files["inspector"],
            "screenshot": existing_files["screenshot"],
            "ui_tree": existing_files["ui_tree"],
            "native_dialog": existing_files["path_validator"] or existing_files["puppeteer"],
            "clipboard": self._file_mentions_any(Path(source_files["controller"]), ("clipboard", "pyperclip", "hotkey", "set_clipboard")),
        }
        missing = [name for name, ok in capabilities.items() if not ok]
        return UfoCapabilityReport(
            ufo_root=str(self.ufo_root),
            root_exists=self.ufo_root.exists(),
            source_files=source_files,
            existing_files=existing_files,
            capabilities=capabilities,
            missing_capabilities=missing,
        )

    def _file_mentions_any(self, path: Path, keywords: tuple[str, ...]) -> bool:
        """检查文件内容是否包含任意能力关键词。"""

        # 关键词扫描只是审计线索，不等同于完成真实 clipboard 适配。
        # 读取失败时返回 False，让报告保守地暴露能力缺口。
        # 使用小写比较，兼容 UFO 源码中的不同大小写写法。
        if not path.exists():
            return False
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            return False
        return any(keyword.lower() in text for keyword in keywords)

