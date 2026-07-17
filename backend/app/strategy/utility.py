"""Negotiation utility overlay for argument selection.

The bandit learns reaction payoff. This layer protects the fixed negotiation
goal (persuasion toward ITU Computer Engineering) while requiring current
candidate compatibility. It may override a bandit pick only by a meaningful
utility margin, keeping exploration intact.
"""
from dataclasses import dataclass, field

from ..fsm.states import FSMState
from ..profile.schema import CandidateProfile
from .bandit import SelectionResult
from .router import RouteDecision


@dataclass
class UtilityDecision:
    selection: SelectionResult
    overridden: bool = False
    original_argument_id: str = ""
    margin: float = 0.0
    utilities: dict[str, dict] = field(default_factory=dict)
    reason: str = "Bandit seçimi utility eşiğini geçti; seçim korundu."

    def to_dict(self) -> dict:
        return {
            "overridden": self.overridden,
            "original_argument_id": self.original_argument_id,
            "selected_argument_id": self.selection.argument_id,
            "margin": round(self.margin, 3),
            "reason": self.reason,
            "utilities": self.utilities,
        }


_GOAL_ALIGNMENT = {
    "compe_priority_top1000": 1.00,
    "compe_borderline_1000_1500": 0.96,
    "ai_vs_compe_foundation": 0.96,
    "electronics_vs_compe_overlap": 0.90,
    "software_vs_compe": 0.96,
    "future_of_compe": 0.94,
    "itu_faculty_research": 0.94,
    "itu_curriculum_flexibility": 0.94,
    "itu_first_year_curriculum": 0.98,
    "itu_curriculum_beginner": 0.96,
    "itu_curriculum_overview": 0.96,
    "itu_curriculum_details": 0.97,
    "itu_academic_workload": 0.91,
    "itu_technical_resources": 0.94,
    "itu_internship_pathways": 0.95,
    "itu_research_projects": 0.97,
    "itu_specialization": 0.97,
    "itu_double_major_transfer": 0.92,
    "itu_erasmus_mobility": 0.94,
    "itu_clubs_teams": 0.92,
    "itu_housing_details": 0.92,
    "itu_istanbul_life": 0.90,
    "itu_student_wellbeing": 0.88,
    "itu_graduation_requirements": 0.92,
    "itu_global_opportunities": 0.92,
    "itu_clubs_projects": 0.90,
    "itu_student_life_support": 0.88,
    "itu_campus_life": 0.92,
    "itu_dining": 0.90,
    "itu_career_evidence": 0.96,
    "itu_english_prep": 0.92,
    "itu_compe_differentiators": 0.98,
    "itu_financial_support": 0.94,
    "itu_entrepreneurship_ecosystem": 0.94,
    "itu_admission_reality": 0.90,
    "money_motivated_data": 0.90,
    "science_motivated_labs": 0.90,
    "med_vs_eng_health_tech": 0.86,
    "koc_vs_itu_value": 0.90,
    "university_comparison_general": 0.88,
    "concern_math_difficulty": 0.82,
    "concern_family_pressure": 0.84,
    "balanced_perspective": 0.72,
    "active_listening": 0.62,
    "socratic_probe": 0.58,
    "rank_probe": 0.55,
}


def apply_utility_overlay(
    selection: SelectionResult,
    profile: CandidateProfile,
    fsm_state: FSMState,
    route: RouteDecision,
    override_threshold: float = 0.08,
) -> UtilityDecision:
    candidates = [(selection.argument_id, selection.score), *selection.alternatives]
    # Preserve ordering while removing duplicate candidate ids.
    candidates = list(dict(candidates).items())

    utilities: dict[str, dict] = {}
    for argument_id, raw_bandit_score in candidates:
        bandit_score = max(0.0, min(1.0, float(raw_bandit_score) / 1.15))
        compatibility = _compatibility(argument_id, profile, fsm_state, route)
        goal_alignment = _GOAL_ALIGNMENT.get(argument_id, 0.70)
        total = 0.55 * bandit_score + 0.30 * compatibility + 0.15 * goal_alignment
        utilities[argument_id] = {
            "total": round(total, 3),
            "bandit": round(bandit_score, 3),
            "candidate_compatibility": round(compatibility, 3),
            "itu_compe_goal_alignment": round(goal_alignment, 3),
        }

    original_id = selection.argument_id
    best_id = max(utilities, key=lambda arg_id: utilities[arg_id]["total"])
    margin = utilities[best_id]["total"] - utilities[original_id]["total"]
    if best_id == original_id or margin < override_threshold:
        return UtilityDecision(
            selection=selection,
            original_argument_id=original_id,
            margin=margin,
            utilities=utilities,
        )

    best_score = dict(candidates)[best_id]
    alternatives = [
        (arg_id, score) for arg_id, score in candidates if arg_id != best_id
    ][:3]
    adjusted = SelectionResult(
        argument_id=best_id,
        score=best_score,
        exploration_bonus=0.0,
        reasoning=(
            f"Utility overlay override: {original_id} -> {best_id}; "
            f"margin={margin:.3f}, threshold={override_threshold:.3f}."
        ),
        alternatives=alternatives,
    )
    return UtilityDecision(
        selection=adjusted,
        overridden=True,
        original_argument_id=original_id,
        margin=margin,
        utilities=utilities,
        reason="Aday uyumu ve İTÜ Bilgisayar hedef faydası bandit seçimini anlamlı farkla geçti.",
    )


def _compatibility(
    argument_id: str,
    profile: CandidateProfile,
    fsm_state: FSMState,
    route: RouteDecision,
) -> float:
    if argument_id == route.forced_argument_id:
        return 1.0
    if argument_id in route.preferred_arguments:
        return 0.95

    ind = profile.indecision
    dom = ind.dominant_motivation()
    score = 0.45

    if argument_id == "itu_financial_support" and (
        profile.constraints.cost_sensitivity is not None and profile.constraints.cost_sensitivity >= 0.5
    ):
        score = 0.98
    elif argument_id == "compe_priority_top1000" and profile.yks_rank and profile.yks_rank <= 1000:
        score = 0.95
    elif argument_id == "compe_borderline_1000_1500" and profile.yks_rank and profile.yks_rank <= 1500:
        score = 0.95
    elif argument_id == "itu_admission_reality" and profile.yks_rank is not None:
        score = 0.88
    elif argument_id == "med_vs_eng_health_tech" and "tip" in ind.field_alternatives:
        score = 0.95
    elif argument_id in ("koc_vs_itu_value", "university_comparison_general") and ind.university_alternatives:
        score = 0.92
    elif argument_id == "ai_vs_compe_foundation" and "yapay_zeka_veri" in ind.department_alternatives:
        score = 0.96
    elif argument_id == "electronics_vs_compe_overlap" and any(
        d in ind.department_alternatives for d in ("elektronik_haberlesme", "elektrik", "kontrol_otomasyon")
    ):
        score = 0.95
    elif argument_id in ("money_motivated_data", "itu_student_life_support", "itu_financial_support") and dom in (
        "money", "entrepreneurship", "job_security",
    ):
        score = 0.90
    elif argument_id == "itu_entrepreneurship_ecosystem" and dom == "entrepreneurship":
        score = 0.96
    elif argument_id in ("science_motivated_labs", "itu_faculty_research", "itu_global_opportunities") and dom in (
        "science", "abroad",
    ):
        score = 0.92
    elif argument_id == "concern_family_pressure" and "family" in profile.concerns:
        score = 0.96
    elif argument_id == "concern_math_difficulty" and set(profile.concerns) & {
        "math", "difficulty", "self_efficacy",
    }:
        score = 0.96
    elif argument_id == "future_of_compe" and "employment" in profile.concerns:
        score = 0.96

    if fsm_state == FSMState.S7_CONCERN_HANDLING and argument_id in (
        "active_listening", "balanced_perspective", "concern_family_pressure",
        "concern_math_difficulty", "future_of_compe",
    ):
        score = max(score, 0.80)
    if fsm_state in (FSMState.S1_GREETING, FSMState.S2_INDECISION_PROBE) and argument_id in (
        "rank_probe", "socratic_probe", "active_listening",
    ):
        score = max(score, 0.82)
    return score
