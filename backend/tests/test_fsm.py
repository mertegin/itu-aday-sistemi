"""FSM transition testleri — predikat ve öncelik davranışı."""
from app.fsm.machine import NegotiationFSM
from app.fsm.states import FSMState


def ctx(**kwargs) -> dict:
    """Varsayılan nötr context + override'lar."""
    base = {
        "turn_count": 3,
        "yks_rank": None,
        "interests_known": 0,
        "greeting_done": True,
        "intent": "neutral",
        "sentiment": 0.0,
        "reception_signal": 0.5,
        "wants_detail": False,
        "new_profile_info": False,
        "has_objection": False,
        "has_field_alternatives": False,
        "has_univ_alternatives": False,
        "has_dept_alternatives": False,
        "has_dominant_motivation": False,
        "fallback_needed": False,
    }
    base.update(kwargs)
    return base


def test_greeting_moves_to_probe():
    fsm = NegotiationFSM(FSMState.S1_GREETING)
    r = fsm.transition(ctx())
    assert r.to_state == FSMState.S2_INDECISION_PROBE


def test_probe_stays_without_profile():
    fsm = NegotiationFSM(FSMState.S2_INDECISION_PROBE)
    r = fsm.transition(ctx())
    assert r.to_state == FSMState.S2_INDECISION_PROBE
    assert r.trigger == "keep_probing"


def test_probe_advances_with_rank_and_interest():
    fsm = NegotiationFSM(FSMState.S2_INDECISION_PROBE)
    r = fsm.transition(ctx(yks_rank=800, interests_known=2))
    assert r.to_state == FSMState.S4_ARGUMENT_DELIVERY


def test_probe_advances_with_rank_and_field_alternative():
    """Aday 'tıp da düşünüyorum' dediğinde ilgi olmasa bile argümana geçilmeli."""
    fsm = NegotiationFSM(FSMState.S2_INDECISION_PROBE)
    r = fsm.transition(ctx(yks_rank=1200, has_field_alternatives=True))
    assert r.to_state == FSMState.S4_ARGUMENT_DELIVERY


def test_probe_does_not_advance_without_rank():
    fsm = NegotiationFSM(FSMState.S2_INDECISION_PROBE)
    r = fsm.transition(ctx(yks_rank=None, interests_known=3))
    assert r.to_state != FSMState.S3_ARGUMENT_SELECTION


def test_concern_goes_to_s7():
    fsm = NegotiationFSM(FSMState.S2_INDECISION_PROBE)
    r = fsm.transition(ctx(intent="concern", has_objection=True))
    assert r.to_state == FSMState.S7_CONCERN_HANDLING


def test_s3_always_delivers():
    fsm = NegotiationFSM(FSMState.S3_ARGUMENT_SELECTION)
    r = fsm.transition(ctx())
    assert r.to_state == FSMState.S4_ARGUMENT_DELIVERY


def test_delivery_wants_detail_goes_to_rag():
    fsm = NegotiationFSM(FSMState.S4_ARGUMENT_DELIVERY)
    r = fsm.transition(ctx(intent="seek_info", wants_detail=True))
    assert r.to_state == FSMState.S6_RAG_DEEP_DIVE


def test_delivery_concern_beats_detail():
    """Öncelik: concern, detail'den önce gelir."""
    fsm = NegotiationFSM(FSMState.S4_ARGUMENT_DELIVERY)
    r = fsm.transition(ctx(intent="concern", has_objection=True, wants_detail=True))
    assert r.to_state == FSMState.S7_CONCERN_HANDLING


def test_close_intent_goes_to_summary():
    fsm = NegotiationFSM(FSMState.S4_ARGUMENT_DELIVERY)
    r = fsm.transition(ctx(intent="close"))
    assert r.to_state == FSMState.S8_IDEAL_MATCH_SUMMARY


def test_turn_twelve_does_not_force_summary_during_active_conversation():
    fsm = NegotiationFSM(FSMState.S5_RECEPTION_EVAL)
    r = fsm.transition(ctx(turn_count=12))
    assert r.to_state == FSMState.S4_ARGUMENT_DELIVERY


def test_soft_limit_closes_only_quiet_long_conversation():
    fsm = NegotiationFSM(FSMState.S5_RECEPTION_EVAL)
    r = fsm.transition(ctx(turn_count=18, intent="disengaged"))
    assert r.to_state == FSMState.S8_IDEAL_MATCH_SUMMARY


def test_summary_moves_to_closing():
    fsm = NegotiationFSM(FSMState.S8_IDEAL_MATCH_SUMMARY)
    r = fsm.transition(ctx(intent="close"))
    assert r.to_state == FSMState.S9_CLOSING


def test_closing_stays_closed():
    fsm = NegotiationFSM(FSMState.S9_CLOSING)
    r = fsm.transition(ctx(intent="close"))
    assert r.to_state == FSMState.S9_CLOSING


def test_closing_reopens_for_new_detail_question():
    fsm = NegotiationFSM(FSMState.S9_CLOSING)
    r = fsm.transition(ctx(intent="seek_info", wants_detail=True))
    assert r.to_state == FSMState.S6_RAG_DEEP_DIVE


def test_positive_reception_deepens():
    fsm = NegotiationFSM(FSMState.S5_RECEPTION_EVAL)
    r = fsm.transition(ctx(reception_signal=0.8))
    assert r.to_state == FSMState.S4_ARGUMENT_DELIVERY


def test_legacy_selection_state_respects_new_concern():
    fsm = NegotiationFSM(FSMState.S3_ARGUMENT_SELECTION)
    r = fsm.transition(ctx(intent="concern", has_objection=True))
    assert r.to_state == FSMState.S7_CONCERN_HANDLING


def test_negative_reception_goes_to_concern():
    fsm = NegotiationFSM(FSMState.S5_RECEPTION_EVAL)
    r = fsm.transition(ctx(reception_signal=0.2))
    assert r.to_state == FSMState.S7_CONCERN_HANDLING
