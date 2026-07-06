import json

import pytest

from jm_ufo_agent.core.settings import ReviewScorerSettings
from jm_ufo_agent.integrations.minimax_review import MiniMaxReviewClient, ReviewRubricItem
from jm_ufo_agent.strategies.review_score import MiniMaxReviewScoreStrategy


class FakeReviewTransport:
    def __init__(self):
        self.post_payload = None

    async def get_json(self, url, headers):
        return {"data": [{"id": "MiniMax-M3", "type": "model"}]}

    async def post_json(self, url, headers, payload):
        self.post_payload = payload
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {
                            "overall_score": 97,
                            "max_score": 100,
                            "blocking_gaps": [],
                            "recommendations": ["继续补真实环境证据"],
                        },
                        ensure_ascii=False,
                    ),
                }
            ]
        }


async def test_minimax_review_client_preflight_and_score_with_fake_transport():
    transport = FakeReviewTransport()
    client = MiniMaxReviewClient(ReviewScorerSettings(api_key="token"), transport)

    available = await client.preflight()
    score = await client.score("spec", [ReviewRubricItem(item="安全策略", evidence=["SafetyPolicy"])])

    assert available is True
    assert score.overall_score == 97
    assert score.recommendations == ["继续补真实环境证据"]
    assert transport.post_payload["model"] == "MiniMax-M3"


async def test_minimax_review_strategy_uses_injected_client():
    transport = FakeReviewTransport()
    client = MiniMaxReviewClient(ReviewScorerSettings(api_key="token"), transport)
    strategy = MiniMaxReviewScoreStrategy(client=client)

    decision = await strategy.decide_async(1.0, blockers=[])

    assert decision.decision == "save_draft"
    assert decision.overall_score == 97
    assert transport.post_payload["model"] == "MiniMax-M3"


def test_minimax_review_client_parses_fenced_json():
    client = MiniMaxReviewClient(ReviewScorerSettings(), FakeReviewTransport())

    score = client.parse_content('```json\n{"overall_score": 88, "max_score": 100, "blocking_gaps": ["缺证据"]}\n```')

    assert score.overall_score == 88
    assert score.blocking_gaps == ["缺证据"]


def test_minimax_review_client_rejects_invalid_json():
    client = MiniMaxReviewClient(ReviewScorerSettings(), FakeReviewTransport())

    with pytest.raises(json.JSONDecodeError):
        client.parse_content("not json")
