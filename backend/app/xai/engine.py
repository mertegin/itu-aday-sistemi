"""XAI — kararın deterministik açıklaması. LLM çağrısı yok."""
from dataclasses import dataclass, field

from ..arguments.catalog import get_argument
from ..profile.schema import CandidateProfile


@dataclass
class Explanation:
    argument_id: str
    argument_label: str
    fsm_from: str
    fsm_to: str
    fsm_trigger: str
    user_type: str
    reason_tr: str
    decision_factors: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "argument_id": self.argument_id,
            "argument_label": self.argument_label,
            "fsm_from": self.fsm_from,
            "fsm_to": self.fsm_to,
            "fsm_trigger": self.fsm_trigger,
            "user_type": self.user_type,
            "reason_tr": self.reason_tr,
            "decision_factors": self.decision_factors,
        }


def build_explanation(
    argument_id: str,
    fsm_from: str,
    fsm_to: str,
    fsm_trigger: str,
    fsm_weight: float,
    user_type: str,
    profile: CandidateProfile,
    bandit_score: float,
    exploration_bonus: float,
    alternatives: list[tuple[str, float]],
    policy_meta: dict | None = None,
) -> Explanation:
    arg = get_argument(argument_id)
    label = arg.label if arg else argument_id
    technique = arg.technique if arg else "unknown"

    parts = []
    parts.append(f"Kullanıcı tipi: {user_type}.")

    if profile.yks_rank:
        parts.append(f"YKS sıralaması: {profile.yks_rank} (bilinen).")
    else:
        parts.append("YKS sıralaması henüz alınmadı.")

    dom = profile.indecision.dominant_motivation()
    if dom != "unknown":
        parts.append(f"Dominant motivasyon: {dom}.")

    axis = profile.indecision.main_indecision_axis()
    overall_indecision = profile.indecision.overall_indecision()
    parts.append(f"Ana kararsızlık ekseni: {axis} (netlik en düşük olan).")

    parts.append(
        f"FSM: {fsm_from} → {fsm_to} (trigger: {fsm_trigger}, weight {fsm_weight:.2f})."
    )
    parts.append(
        f"Argüman seçimi: '{label}' ({technique}). Bandit skor {bandit_score:.2f}, "
        f"exploration bonus {exploration_bonus:.2f}."
    )

    if alternatives:
        alt_str = ", ".join(f"{a} ({s:.2f})" for a, s in alternatives[:3])
        parts.append(f"Alternatifler: {alt_str}.")

    if profile.revealed_arguments:
        parts.append(f"Önce sunulan argümanlar: {', '.join(profile.revealed_arguments[-4:])}.")

    policy_meta = policy_meta or {}
    route = policy_meta.get("route", {})
    if route.get("primary_topic") and route.get("primary_topic") != "general":
        parts.append(
            f"Güncel konu: {route['primary_topic']} (router güveni {route.get('confidence', 0):.2f})."
        )
    utility = policy_meta.get("utility", {})
    if utility.get("overridden"):
        parts.append(
            f"Utility override: {utility.get('original_argument_id')} -> {argument_id} "
            f"(fark {utility.get('margin', 0):.2f})."
        )

    reason_tr = " ".join(parts)

    return Explanation(
        argument_id=argument_id,
        argument_label=label,
        fsm_from=fsm_from,
        fsm_to=fsm_to,
        fsm_trigger=fsm_trigger,
        user_type=user_type,
        reason_tr=reason_tr,
        decision_factors={
            "user_type": user_type,
            "yks_rank": profile.yks_rank,
            "dominant_motivation": dom,
            "main_indecision_axis": axis,
            "overall_indecision": round(overall_indecision, 3),
            "top_alternatives": profile.indecision.top_alternatives,
            "bandit_score": bandit_score,
            "exploration_bonus": exploration_bonus,
            "fsm_weight": fsm_weight,
            "alternatives": alternatives[:3],
            "revealed_arguments_count": len(profile.revealed_arguments),
            "route": route,
            "utility": utility,
            "previous_reward": policy_meta.get("previous_reward"),
        },
    )
