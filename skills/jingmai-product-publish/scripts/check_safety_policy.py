"""检查桌面动作入口是否调用 SafetyPolicy。"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path


GUARDED_METHODS = {"click", "fill", "submit"}


@dataclass(frozen=True)
class SafetyFinding:
    """静态安全检查发现。"""

    path: Path
    line: int
    method_name: str
    message: str


def main(argv: list[str] | None = None) -> int:
    """执行安全检查。"""

    # 默认扫描 jm_ufo_agent 包，也允许测试传入临时目录。
    # 该脚本只读取 Python 源码，不导入项目模块，避免触发外部副作用。
    # 发现问题时输出文件和行号，并用非 0 退出码阻断 CI。
    args = argv if argv is not None else sys.argv[1:]
    roots = [Path(arg) for arg in args] or [Path("jm_ufo_agent")]
    findings: list[SafetyFinding] = []
    for root in roots:
        findings.extend(scan_path(root))
    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.method_name}: {finding.message}")
    return 1 if findings else 0


def scan_path(root: Path) -> list[SafetyFinding]:
    """扫描文件或目录。"""

    # 文件路径直接扫描单文件，目录路径递归扫描 py 文件。
    # __pycache__ 不包含源码，直接跳过。
    # 路径不存在时返回一条 finding，让 CI 配置错误能暴露。
    if not root.exists():
        return [SafetyFinding(root, 0, "-", "扫描路径不存在")]
    if root.is_file():
        return scan_file(root)
    findings: list[SafetyFinding] = []
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        findings.extend(scan_file(path))
    return findings


def scan_file(path: Path) -> list[SafetyFinding]:
    """扫描单个 Python 文件。"""

    # 使用 ast.parse 避免误把注释或字符串当作方法定义。
    # 语法错误也应阻断 CI，因为安全扫描无法确认该文件是否安全。
    # 只检查 click/fill/submit 三类高危桌面动作入口。
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [SafetyFinding(path, exc.lineno or 0, "-", f"语法错误: {exc.msg}")]

    findings: list[SafetyFinding] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in GUARDED_METHODS:
            if not _has_assert_allowed_near_start(node):
                findings.append(SafetyFinding(path, node.lineno, node.name, "方法开头缺少 safety_policy.assert_allowed(cmd)"))
    return findings


def _has_assert_allowed_near_start(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """判断方法体前几条语句是否调用 assert_allowed。"""

    # 允许开头存在 docstring、简单赋值构造 cmd、注释不会进入 AST。
    # 只检查前 5 条真实语句，避免把末尾补调用误判为安全。
    # 调用形式支持 self.safety_policy.assert_allowed(cmd) 或 safety_policy.assert_allowed(cmd)。
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    for stmt in body[:5]:
        for child in ast.walk(stmt):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute) and child.func.attr == "assert_allowed":
                return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
