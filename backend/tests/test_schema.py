"""Pydantic MessageAnalysis şema testleri — clamp, fallback davranışı."""
import pytest
from pydantic import ValidationError

from app.llm.schema import MessageAnalysis


def test_defaults():
    a = MessageAnalysis()
    assert a.intent == "neutral"
    assert a.reception_signal == 0.5


def test_sentiment_clamped():
    a = MessageAnalysis(sentiment=5.0)
    assert a.sentiment == 1.0
    a = MessageAnalysis(sentiment=-3.0)
    assert a.sentiment == -1.0


def test_motivation_clamped():
    a = MessageAnalysis(motivation_signals={"money": 7.0, "science": -1.0})
    assert a.motivation_signals.money == 1.0
    assert a.motivation_signals.science == 0.0


def test_insane_rank_rejected():
    a = MessageAnalysis(yks_rank_mentioned=99_999_999)
    assert a.yks_rank_mentioned is None
    a = MessageAnalysis(yks_rank_mentioned=0)
    assert a.yks_rank_mentioned is None
    a = MessageAnalysis(yks_rank_mentioned=1200)
    assert a.yks_rank_mentioned == 1200


def test_bad_intent_raises():
    with pytest.raises(ValidationError):
        MessageAnalysis(intent="quantum_state")


def test_display_name_sentence_rejected():
    a = MessageAnalysis(display_name_mentioned="ben aslında tam bilmiyorum ama olabilir")
    assert a.display_name_mentioned is None
    a = MessageAnalysis(display_name_mentioned="deniz")
    assert a.display_name_mentioned == "Deniz"


def test_to_orchestrator_dict_shape():
    d = MessageAnalysis().to_orchestrator_dict()
    for key in ("intent", "field_signals", "university_signals", "department_signals",
                "motivation_signals", "interests_mentioned", "concerns_mentioned"):
        assert key in d
