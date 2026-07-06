# tests/test_v2_ufo_backend.py
"""UfoDesktopBackend 真实 GUI 闭环测试。"""

from unittest.mock import MagicMock

import pytest

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.commands.base import Command
from jm_ufo_agent.backends.ufo_backend import UfoDesktopBackend, _StubController


class TestUfoDesktopBackendProtocol:
    def test_implements_desktop_backend(self):
        """UfoDesktopBackend 应实现 DesktopBackend 协议。"""
        from jm_ufo_agent.agents.desktop import DesktopBackend

        backend = UfoDesktopBackend.__new__(UfoDesktopBackend)
        assert hasattr(backend, "execute")
        assert callable(backend.execute)

    def test_init_with_ufo_root(self):
        """应接受 ufo_root 路径参数。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        assert backend.ufo_root == Path("/fake/ufo")


class TestUfoDesktopBackendExecute:
    @pytest.mark.asyncio
    async def test_click_delegates_to_ufo(self):
        """click 命令应委托给 UFO controller。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        backend._controller = MagicMock()
        backend._controller.click = MagicMock(return_value=True)

        cmd = Command(action="click", target="价格输入框", label="点击价格")
        result = await backend.execute(cmd)
        assert isinstance(result, AgentResult)
        assert result.ok is True
        assert result.data["action"] == "click"

    @pytest.mark.asyncio
    async def test_fill_uses_clipboard(self):
        """fill 命令应通过剪贴板+粘贴方式输入。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        backend._controller = MagicMock()
        backend._controller.set_text = MagicMock(return_value=True)

        cmd = Command(action="fill", target="标题", label="填写标题", value="测试商品")
        result = await backend.execute(cmd)
        assert isinstance(result, AgentResult)
        assert result.ok is True
        assert result.data["action"] == "fill"

    @pytest.mark.asyncio
    async def test_submit_delegates_to_ufo(self):
        """submit 命令应委托给 UFO。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        backend._controller = MagicMock()
        backend._controller.click = MagicMock(return_value=True)

        cmd = Command(action="submit", target="draft", label="保存草稿")
        result = await backend.execute(cmd)
        assert isinstance(result, AgentResult)
        assert result.ok is True
        assert result.data["action"] == "submit"

    @pytest.mark.asyncio
    async def test_execute_returns_failure_on_error(self):
        """UFO 调用失败应返回 AgentResult(ok=False)。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        backend._controller = MagicMock()
        backend._controller.click = MagicMock(side_effect=RuntimeError("窗口未找到"))

        cmd = Command(action="click", target="不存在", label="测试失败")
        result = await backend.execute(cmd)
        assert result.ok is False
        assert "窗口未找到" in result.message

    @pytest.mark.asyncio
    async def test_unknown_action_returns_failure(self):
        """未知 action 应返回失败。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        cmd = Command(action="unknown_action", target="x", label="y")
        result = await backend.execute(cmd)
        assert result.ok is False

    @pytest.mark.asyncio
    async def test_fill_with_none_value(self):
        """fill 命令 value=None 时应返回空字符串填充结果。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        backend._controller = MagicMock()
        backend._controller.set_text = MagicMock(return_value=True)

        cmd = Command(action="fill", target="备注", label="填写备注", value=None)
        result = await backend.execute(cmd)
        assert result.ok is True
        assert result.data["action"] == "fill"
        assert result.data["value_preview"] == ""

    @pytest.mark.asyncio
    async def test_ensure_loaded_with_missing_ufo_root(self):
        """ufo_root 不存在时 execute 应返回 ok=False。"""
        from pathlib import Path

        backend = UfoDesktopBackend(ufo_root=Path("/nonexistent/ufo/path"))
        cmd = Command(action="click", target="按钮", label="测试")
        result = await backend.execute(cmd)
        assert result.ok is False


class TestStubController:
    def test_stub_controller_click_raises(self):
        """StubController.click 应抛出 RuntimeError。"""
        stub = _StubController()
        with pytest.raises(RuntimeError, match="UFO 未安装"):
            stub.click("任意目标")

    def test_stub_controller_set_text_raises(self):
        """StubController.set_text 应抛出 RuntimeError。"""
        stub = _StubController()
        with pytest.raises(RuntimeError, match="UFO 未安装"):
            stub.set_text("任意目标", "任意值")
