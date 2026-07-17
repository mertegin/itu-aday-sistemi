"""Bandit testleri — prior fallback, tekrar blokajı, rank_probe limiti, reward."""
from app.fsm.states import FSMState
from app.profile.schema import CandidateProfile
from app.strategy.bandit import (
    ArgumentSelector, compute_reward, compute_reward_breakdown, derive_user_type,
)


def make_profile(**kwargs) -> CandidateProfile:
    p = CandidateProfile()
    for k, v in kwargs.items():
        setattr(p, k, v)
    return p


def test_user_type_unranked():
    p = make_profile()
    assert derive_user_type(p) == "unranked_discovery"


def test_user_type_bands():
    assert derive_user_type(make_profile(yks_rank=500)).startswith("top1000")
    assert derive_user_type(make_profile(yks_rank=1200)).startswith("borderline")
    assert derive_user_type(make_profile(yks_rank=3000)).startswith("below_compe")


def test_user_type_motivation_suffix():
    p = make_profile(yks_rank=800)
    p.indecision.motivation["money"] = 0.9
    assert derive_user_type(p) == "top1000_money"


def test_prior_fallback_does_not_leak_family_cell():
    """REGRESYON: top1000_science isteyen arm, top1000_family hücresinin 0.90'ını almamalı."""
    sel = ArgumentSelector()
    prior = sel._prior("concern_family_pressure", "top1000_science")
    # concern_family_pressure'da top1000_general hücresi yok → DEFAULT (0.5) dönmeli, 0.90 DEĞİL
    assert prior == 0.5


def test_prior_exact_match():
    sel = ArgumentSelector()
    assert sel._prior("concern_family_pressure", "top1000_family") == 0.90


def test_prior_general_fallback():
    sel = ArgumentSelector()
    # compe_priority_top1000: top1000_general=0.90 var; top1000_interest yok → general'a düşer
    assert sel._prior("compe_priority_top1000", "top1000_interest") == 0.90


def test_repeat_hard_block():
    """Son seçilen argüman, alternatif varken bir daha seçilemez."""
    sel = ArgumentSelector()
    p = make_profile(yks_rank=800)
    stats: dict = {}
    first = sel.select("top1000_general", FSMState.S3_ARGUMENT_SELECTION, p, stats, recent_arguments=[])
    second = sel.select("top1000_general", FSMState.S3_ARGUMENT_SELECTION, p, stats,
                        recent_arguments=[first.argument_id])
    assert second.argument_id != first.argument_id


def test_rank_probe_max_twice():
    """rank_probe en fazla 2 kez — aday cevap vermiyorsa ısrar edilmez."""
    sel = ArgumentSelector()
    p = make_profile()  # rank yok
    stats: dict = {}
    picks = []
    recents: list[str] = []
    for _ in range(4):
        r = sel.select("unranked_discovery", FSMState.S2_INDECISION_PROBE, p, stats, recent_arguments=recents)
        picks.append(r.argument_id)
        recents.append(r.argument_id)
    assert picks.count("rank_probe") <= 2


def test_s8_forces_summary_argument():
    sel = ArgumentSelector()
    p = make_profile(yks_rank=800)
    r = sel.select("top1000_general", FSMState.S8_IDEAL_MATCH_SUMMARY, p, {}, recent_arguments=[])
    assert r.argument_id == "ideal_match_summary"


def test_koc_argument_eligible_when_alternative_mentioned():
    sel = ArgumentSelector()
    p = make_profile(yks_rank=800)
    p.indecision.university_alternatives = ["koc"]
    eligible = sel._eligible_for_state(FSMState.S3_ARGUMENT_SELECTION, p, {})
    assert "koc_vs_itu_value" in eligible


def test_reward_reject_not_penalized():
    """Etik ikna felsefesi: reject cezalandırılmaz (0 delta), disengage cezalandırılır."""
    reject = compute_reward({"intent": "reject", "sentiment": 0.0, "response_length": 10})
    disengaged = compute_reward({"intent": "disengaged", "sentiment": 0.0, "response_length": 10})
    assert reject > disengaged


def test_reward_followup_increases_engagement_without_dominating_effectiveness():
    with_q = compute_reward({"intent": "neutral", "asked_followup": True, "response_length": 10})
    without_q = compute_reward({"intent": "neutral", "asked_followup": False, "response_length": 10})
    assert with_q > without_q
    assert with_q - without_q < 0.10


def test_reward_separates_engagement_from_argument_effectiveness():
    accepted = compute_reward_breakdown({
        "intent": "engaged", "asked_followup": True, "response_length": 14,
        "argument_reaction": "accepted", "reception_signal": 0.9,
        "response_relevance": 0.9,
    })
    rejected = compute_reward_breakdown({
        "intent": "reject", "asked_followup": True, "response_length": 14,
        "argument_reaction": "rejected", "reception_signal": 0.2,
        "response_relevance": 0.9,
    })
    assert rejected["engagement"] > 0.4  # conversation is still alive
    assert rejected["argument_effectiveness"] < 0.25
    assert accepted["bandit_reward"] > rejected["bandit_reward"]


def test_topic_shift_does_not_get_full_credit_for_followup():
    shifted = compute_reward_breakdown({
        "intent": "seek_info", "asked_followup": True, "response_length": 20,
        "argument_reaction": "topic_shift", "reception_signal": 0.5,
        "response_relevance": 0.1,
    })
    assert shifted["engagement"] > shifted["argument_effectiveness"]
    assert shifted["bandit_reward"] < 0.6


def test_ewma_update():
    sel = ArgumentSelector()
    stats: dict = {}
    sel.update(stats, "top1000_general", "active_listening", 1.0)
    sel.update(stats, "top1000_general", "active_listening", 0.0)
    key = "top1000_general::active_listening"
    assert stats[key]["n"] == 2
    assert stats[key]["reward_sum"] == 1.0
