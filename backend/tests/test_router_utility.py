from app.fsm.states import FSMState
from app.profile.schema import CandidateProfile
from app.strategy.bandit import SelectionResult
from app.strategy.router import route_current_turn
from app.strategy.utility import apply_utility_overlay


def _analysis(**overrides):
    base = {
        "asked_followup": True,
        "wants_detail": True,
        "concerns_mentioned": [],
    }
    base.update(overrides)
    return base


def test_faculty_question_forces_faculty_argument():
    route = route_current_turn(
        "Yapay zeka alanında çalışan hocalar var mı?",
        _analysis(),
        CandidateProfile(),
    )
    assert route.primary_topic == "faculty_research"
    assert route.forced_argument_id == "itu_faculty_research"


def test_housing_question_does_not_route_to_ai_argument():
    route = route_current_turn(
        "Yurtlar ve burs imkanları nasıl?",
        _analysis(),
        CandidateProfile(),
    )
    assert route.forced_argument_id == "itu_financial_support"
    assert "ai_vs_compe_foundation" not in route.preferred_arguments


def test_housing_only_question_stays_in_student_support():
    route = route_current_turn(
        "Yurt ve yemekhane imkanları nasıl?",
        _analysis(),
        CandidateProfile(),
    )
    assert route.primary_topic == "student_support"
    assert route.forced_argument_id == "itu_student_life_support"


def test_financial_hardship_forces_financial_support():
    route = route_current_turn(
        "Ailem masrafları karşılayamaz, para sıkıntısı çeker miyim?",
        _analysis(concerns_mentioned=["cost"]),
        CandidateProfile(),
    )
    assert route.primary_topic == "financial_support"
    assert route.forced_argument_id == "itu_financial_support"


def test_startup_question_forces_entrepreneurship_ecosystem():
    route = route_current_turn(
        "İTÜ Çekirdek girişim kurmama nasıl yardımcı olur?",
        _analysis(),
        CandidateProfile(),
    )
    assert route.primary_topic == "entrepreneurship"
    assert route.forced_argument_id == "itu_entrepreneurship_ecosystem"


def test_double_major_question_routes_to_dedicated_conditions():
    route = route_current_turn(
        "Bilgisayardan yapay zekaya çift anadal yapabilir miyim?",
        _analysis(),
        CandidateProfile(),
    )
    assert route.primary_topic == "double_major_transfer"
    assert route.forced_argument_id == "itu_double_major_transfer"


def test_electronics_double_major_uses_the_same_official_conditions():
    route = route_current_turn(
        "Elektronikten bilgisayara çift anadal yapabilir miyim?",
        _analysis(),
        CandidateProfile(),
    )
    assert route.primary_topic == "double_major_transfer"
    assert route.forced_argument_id == "itu_double_major_transfer"


def test_abroad_does_not_get_confused_with_housing():
    route = route_current_turn(
        "Yurt dışına açılmak istersem İTÜ ağı işe yarar mı?",
        _analysis(),
        CandidateProfile(),
    )
    assert route.primary_topic == "global"
    assert route.forced_argument_id == "itu_global_opportunities"


def test_ready_family_company_routes_to_family_objection():
    route = route_current_turn(
        "Hazır aile şirketi varken neden bilgisayar seçeyim?",
        _analysis(),
        CandidateProfile(),
    )
    assert route.primary_topic == "family"
    assert route.forced_argument_id == "concern_family_pressure"


def test_utility_overlay_can_override_mismatched_generic_pick():
    profile = CandidateProfile(yks_rank=800)
    profile.indecision.motivation["science"] = 0.9
    route = route_current_turn("Araştırma yapmak istiyorum", _analysis(asked_followup=False), profile)
    selection = SelectionResult(
        argument_id="balanced_perspective",
        score=0.82,
        exploration_bonus=0.12,
        reasoning="test",
        alternatives=[("itu_faculty_research", 0.80), ("active_listening", 0.78)],
    )
    decision = apply_utility_overlay(selection, profile, FSMState.S4_ARGUMENT_DELIVERY, route)
    assert decision.overridden is True
    assert decision.selection.argument_id == "itu_faculty_research"
    assert decision.utilities["itu_faculty_research"]["itu_compe_goal_alignment"] > 0.9


def test_sticky_profile_flag_does_not_hijack_vague_followups():
    """sess_f450 regresyonu: 'kalacak yerim yok' diyen adayın (housing_needed=True)
    SONRAKİ belirsiz/follow-up soruları yurt argümanına force edilmemeli."""
    profile = CandidateProfile(yks_rank=561)
    profile.constraints.housing_needed = True

    for vague in ["örnek verir misin nelerdir ?",
                  "dersleri düzenli takip etmek yeterli oluyor mu ?",
                  "ders desteği falan filan"]:
        route = route_current_turn(
            vague,
            {"asked_followup": True, "wants_detail": True, "concerns_mentioned": []},
            profile,
        )
        assert route.forced_argument_id != "itu_student_life_support", vague
        assert route.primary_topic != "housing", vague

    # Gerçek yurt sorusu hâlâ yurt argümanına gitmeli
    real = route_current_turn(
        "yurtlar nasıl, bana yurt çıkar mı?",
        {"asked_followup": True, "wants_detail": True, "concerns_mentioned": []},
        profile,
    )
    assert real.forced_argument_id in ("itu_student_life_support", "itu_housing_details")
