"""工作流节点函数集合。"""

from __future__ import annotations

from jm_ufo_agent.workflow.nodes.assess_form_completion import assess_form_completion_node
from jm_ufo_agent.workflow.nodes.bootstrap import bootstrap_node
from jm_ufo_agent.workflow.nodes.calibrate_locators import calibrate_locators_node
from jm_ufo_agent.workflow.nodes.commit_row import commit_row_node
from jm_ufo_agent.workflow.nodes.fill_field import fill_fields_node
from jm_ufo_agent.workflow.nodes.halt import halt_node
from jm_ufo_agent.workflow.nodes.minimax_review_score import minimax_review_score_node
from jm_ufo_agent.workflow.nodes.observe_page import observe_page_node
from jm_ufo_agent.workflow.nodes.open_page import open_page_node
from jm_ufo_agent.workflow.nodes.plan_fields import plan_fields_node
from jm_ufo_agent.workflow.nodes.prepare_assets import prepare_assets_node
from jm_ufo_agent.workflow.nodes.recover import recover_node
from jm_ufo_agent.workflow.nodes.reflect_failure import reflect_failure_node
from jm_ufo_agent.workflow.nodes.save_draft import save_draft_node
from jm_ufo_agent.workflow.nodes.select_row import select_row_node
from jm_ufo_agent.workflow.nodes.verify_draft import verify_draft_node
from jm_ufo_agent.workflow.nodes.verify_field import fill_fields_node as verify_field_node
from jm_ufo_agent.workflow.nodes.assert_page_signature import assert_page_signature_node

__all__ = [
    "assess_form_completion_node",
    "assert_page_signature_node",
    "bootstrap_node",
    "calibrate_locators_node",
    "commit_row_node",
    "fill_fields_node",
    "halt_node",
    "minimax_review_score_node",
    "observe_page_node",
    "open_page_node",
    "plan_fields_node",
    "prepare_assets_node",
    "recover_node",
    "reflect_failure_node",
    "save_draft_node",
    "select_row_node",
    "verify_draft_node",
    "verify_field_node",
]
