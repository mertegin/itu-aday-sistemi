"""Profil şeması testleri — provenance, kısıtlar, roundtrip."""
from app.profile.schema import CandidateProfile, PreferenceConstraints, MOTIVATION_KEYS


def test_motivation_has_nine_keys():
    p = CandidateProfile()
    assert set(p.indecision.motivation.keys()) == set(MOTIVATION_KEYS)
    assert len(MOTIVATION_KEYS) == 9


def test_provenance_record_and_classify():
    p = CandidateProfile()
    p.record_provenance("yks_rank", 0.95, turn=2, evidence="sıralamam 800")
    p.record_provenance("motivation:money", 0.55, turn=3)
    assert "yks_rank" in p.confident_facts()
    assert "motivation:money" in p.uncertain_guesses()


def test_provenance_repeat_increases_confidence():
    p = CandidateProfile()
    p.record_provenance("interest:ai", 0.70, turn=1)
    first = p.provenance["interest:ai"]["confidence"]
    p.record_provenance("interest:ai", 0.70, turn=4)
    entry = p.provenance["interest:ai"]
    assert entry["confidence"] > first          # tekrar sinyal güveni artırır
    assert entry["source_turn"] == 1            # ilk kaynak korunur
    assert entry["updated_turn"] == 4


def test_constraints_none_means_unknown():
    c = PreferenceConstraints()
    assert c.known_items() == {}
    c.cost_sensitivity = 0.8
    c.housing_needed = True
    known = c.known_items()
    assert known == {"cost_sensitivity": 0.8, "housing_needed": True}


def test_rank_confidence_by_type():
    p = CandidateProfile(yks_rank=800, yks_rank_type="actual")
    assert p.rank_confidence() == 0.95
    p.yks_rank_type = "practice"
    assert p.rank_confidence() == 0.70
    p.yks_rank_type = "target"
    assert p.rank_confidence() == 0.50


def test_roundtrip_preserves_new_fields():
    p = CandidateProfile(display_name="Deniz", yks_rank=700)
    p.indecision.must_have = ["İstanbul"]
    p.indecision.deal_breakers = ["özel üniversite"]
    p.indecision.top_alternatives = ["koc", "bilgisayar"]
    p.indecision.decision_stage = "kiyaslama"
    p.indecision.motivation["entrepreneurship"] = 0.7
    p.constraints.city_istanbul = 0.9
    p.constraints.housing_needed = False
    p.record_provenance("yks_rank", 0.95, 1)
    p.inactive_alternatives["field"] = ["tip"]
    p.resolved_concerns = ["math"]
    p.decision_status = "still_deciding"
    p.preference_events = [{"turn": 2, "event": "retracted", "category": "field", "value": "tip"}]

    p2 = CandidateProfile.from_dict(p.to_dict())
    assert p2.display_name == "Deniz"
    assert p2.indecision.must_have == ["İstanbul"]
    assert p2.indecision.deal_breakers == ["özel üniversite"]
    assert p2.indecision.top_alternatives == ["koc", "bilgisayar"]
    assert p2.indecision.decision_stage == "kiyaslama"
    assert p2.indecision.motivation["entrepreneurship"] == 0.7
    assert p2.constraints.city_istanbul == 0.9
    assert p2.constraints.housing_needed is False
    assert p2.provenance["yks_rank"]["confidence"] == 0.95
    assert p2.inactive_alternatives["field"] == ["tip"]
    assert p2.resolved_concerns == ["math"]
    assert p2.decision_status == "still_deciding"
    assert p2.preference_events[0]["event"] == "retracted"


def test_from_dict_old_format_backward_compat():
    """Eski (5 motivasyonlu, kısıtsız) kayıtlar sorunsuz yüklenmeli."""
    old = {
        "display_name": "Ali",
        "yks_rank": 900,
        "indecision": {
            "field_certainty": 0.8,
            "motivation": {"money": 0.5, "science": 0.2, "prestige": 0.0, "interest": 0.3, "family": 0.0},
        },
        "interests": {"ai": 0.5},
    }
    p = CandidateProfile.from_dict(old)
    assert p.yks_rank == 900
    assert p.indecision.motivation["money"] == 0.5
    assert p.indecision.motivation["entrepreneurship"] == 0.0  # yeni key default
    assert p.constraints.known_items() == {}
    assert p.provenance == {}


def test_dominant_motivation_new_keys():
    p = CandidateProfile()
    p.indecision.motivation["job_security"] = 0.8
    assert p.indecision.dominant_motivation() == "job_security"


def test_concern_normalization():
    """Ham/duplike kaygı stringleri kanonik kategorilere inmeli (L03/L08 bulgusu)."""
    from app.orchestrator import Orchestrator
    from tests.fake_llm import FakeLLMClient
    orch = Orchestrator(llm_client=FakeLLMClient())
    assert orch._normalize_concern("matematik") == "math"
    assert orch._normalize_concern("mathematics") == "math"
    assert orch._normalize_concern("ailem de üzülür") == "family"
    assert orch._normalize_concern("aile") == "family"
    assert orch._normalize_concern("family") == "family"
    assert orch._normalize_concern("korkularım") == "self_efficacy"
    assert orch._normalize_concern("kalanlar") == "difficulty"
    assert orch._normalize_concern("job_security") == "employment"
    assert orch._normalize_concern("alakasız serbest metin xyz") is None
    assert orch._normalize_concern("") is None


def test_profile_retracts_and_reactivates_alternative():
    p = CandidateProfile()
    p.indecision.field_alternatives = ["tip"]
    p.retire_alternative("field", "tip", turn=2)
    assert "tip" not in p.indecision.field_alternatives
    assert "tip" in p.inactive_alternatives["field"]

    p.activate_alternative("field", "tip", turn=4)
    p.indecision.field_alternatives.append("tip")
    assert "tip" in p.indecision.field_alternatives
    assert "tip" not in p.inactive_alternatives["field"]
    assert [e["event"] for e in p.preference_events] == ["retracted", "reactivated"]


def test_orchestrator_text_fallback_retracts_stale_option():
    from app.orchestrator import Orchestrator
    from tests.fake_llm import FakeLLMClient

    p = CandidateProfile()
    p.indecision.field_alternatives = ["tip"]
    orch = Orchestrator(llm_client=FakeLLMClient())
    orch._update_profile_from_analysis(
        p,
        {"field_signals": {}, "university_signals": {}, "department_signals": {},
         "motivation_signals": {}, "constraint_signals": {}},
        turn=3,
        user_text="Tıptan vazgeçtim, artık düşünmüyorum.",
    )
    assert p.indecision.field_alternatives == []
    assert p.inactive_alternatives["field"] == ["tip"]


def test_orchestrator_marks_concern_resolved_and_decision():
    from app.orchestrator import Orchestrator
    from tests.fake_llm import FakeLLMClient

    p = CandidateProfile()
    p.concerns = ["math"]
    orch = Orchestrator(llm_client=FakeLLMClient())
    orch._update_profile_from_analysis(
        p,
        {"field_signals": {}, "university_signals": {}, "department_signals": {},
         "motivation_signals": {}, "constraint_signals": {},
         "concerns_resolved": ["math"], "decision_status": "itu_compe_committed"},
        turn=5,
        user_text="Matematik artık sorun değil; İTÜ Bilgisayar birinci tercihim.",
    )
    assert "math" not in p.concerns
    assert "math" in p.resolved_concerns
    assert p.decision_status == "itu_compe_committed"
    assert p.decision_confidence == 0.95
