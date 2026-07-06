import pytest

from jm_ufo_agent.agents.base import AgentContext
from jm_ufo_agent.agents.desktop import RecordingDesktopBackend
from jm_ufo_agent.agents.excel_parse import ExcelParseAgent
from jm_ufo_agent.agents.jm_product_form import JmProductFormAgent
from jm_ufo_agent.safety.policy import SafetyViolation


async def test_product_form_agent_records_safe_fill_command():
    backend = RecordingDesktopBackend()
    agent = JmProductFormAgent(backend=backend)

    result = await agent.fill_field("title", "测试商品", evidence={"row_index": 82})

    assert result.ok is True
    assert backend.commands[0].target == "title"
    assert backend.commands[0].value == "测试商品"
    assert backend.commands[0].metadata == {"row_index": 82}


async def test_product_form_agent_blocks_publish_submit():
    agent = JmProductFormAgent()

    with pytest.raises(SafetyViolation):
        await agent.submit("publish", label="发布商品")


async def test_excel_parse_agent_uses_context_product_in_dryrun():
    agent = ExcelParseAgent()
    context = AgentContext(task_id="task-1", product={"product_id": "sku-1", "title": "测试商品"})

    result = await agent.parse_rows(context)

    assert result.ok is True
    assert result.data["rows"] == [{"product_id": "sku-1", "title": "测试商品"}]
