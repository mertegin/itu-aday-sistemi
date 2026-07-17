"""UCB1 contextual bandit — argüman seçimi.

Context = user_type (kararsızlık matrisinden türetilir).
Arm = argument_id (arguments/catalog.py'daki DefenseArgument.id).
Reward = compute_reward(user_analysis) → [0, 1].
"""
import math
from dataclasses import dataclass, field

from ..arguments.catalog import ARGUMENTS, all_argument_ids
from ..fsm.states import FSMState
from ..profile.schema import CandidateProfile


# ============ USER TYPE DERIVATION ============

def derive_user_type(profile: CandidateProfile) -> str:
    """Kararsızlık matrisi + motivasyondan discrete user_type üret."""
    ind = profile.indecision
    dom = ind.dominant_motivation()

    # Sıralama yoksa: erken keşif tipi
    if profile.yks_rank is None:
        return "unranked_discovery"

    # Sıralama biliniyor — 3 dallı ana yol (Majidov Bölüm 4)
    if profile.yks_rank <= 1000:
        base = "top1000"
    elif profile.yks_rank <= 1500:
        base = "borderline"
    else:
        base = "below_compe"

    # Motivasyon eki — payoff matrix'te anlamlı hücresi olan motivasyonlar suffix olur;
    # yakın motivasyonlar en benzer banda map'lenir (matrix sparse kalmasın)
    _MOTIVATION_MAP = {
        "money": "money", "entrepreneurship": "money",   # girişimci de kariyer/kazanç argümanlarına iyi yanıt verir
        "science": "science", "abroad": "science",       # yurt dışı hedefi → akademik/Erasmus argümanları
        "prestige": "prestige",
        "family": "family", "job_security": "family",    # güvenli meslek isteği aile-tipi kaygıya yakın
    }
    mapped = _MOTIVATION_MAP.get(dom)
    if mapped:
        return f"{base}_{mapped}"
    return f"{base}_general"


# ============ PAYOFF MATRIX ============
# Rows = argument_id, Cols = user_type → prior belief (0-1)

_DEFAULT_PRIOR = 0.5

# Priorlar: hangi argüman hangi kullanıcı tipine iyi gelir (Majidov'un decision tree'sinden)
PAYOFF_MATRIX: dict[str, dict[str, float]] = {
    "socratic_probe": {
        "unranked_discovery": 0.85,
        "top1000_general": 0.55, "top1000_money": 0.45,
        "borderline_general": 0.60, "below_compe_general": 0.75,
    },
    "rank_probe": {
        "unranked_discovery": 0.95,  # Sıralama yoksa MUST
    },
    "active_listening": {
        "unranked_discovery": 0.55,
        "top1000_general": 0.60, "borderline_general": 0.65,
        "below_compe_general": 0.65,
        "top1000_family": 0.75, "borderline_family": 0.75, "below_compe_family": 0.75,
    },
    "compe_priority_top1000": {
        "top1000_general": 0.90, "top1000_money": 0.75, "top1000_science": 0.80,
        "top1000_prestige": 0.85, "top1000_family": 0.70,
    },
    "compe_borderline_1000_1500": {
        "borderline_general": 0.90, "borderline_money": 0.80, "borderline_science": 0.80,
        "borderline_prestige": 0.85, "borderline_family": 0.75,
    },
    "med_vs_eng_health_tech": {
        # Aktifleşme koşulu: field_alternatives = ["tıp"] (bandit filter'da)
        "top1000_general": 0.70, "top1000_science": 0.80,
        "borderline_general": 0.70, "below_compe_general": 0.60,
    },
    "koc_vs_itu_value": {
        "top1000_general": 0.80, "top1000_money": 0.85, "top1000_prestige": 0.80,
        "borderline_general": 0.75,
    },
    "ai_vs_compe_foundation": {
        "top1000_general": 0.80, "top1000_science": 0.85,
        "borderline_general": 0.75, "borderline_science": 0.85,
        "below_compe_general": 0.80, "below_compe_science": 0.85,
        # (1500+ sıralamada YZ-Veri zaten daha erişilebilir — bu karşılaştırma tam da o adaya lazım)
    },
    "electronics_vs_compe_overlap": {
        "top1000_general": 0.70, "borderline_general": 0.70,
        "below_compe_general": 0.85,
        # (Bilgisayar tabanının gerisindeki elektronik meraklısı için ana argüman)
    },
    "money_motivated_data": {
        "top1000_money": 0.90, "borderline_money": 0.85,
        "below_compe_money": 0.75,
    },
    "science_motivated_labs": {
        "top1000_science": 0.90, "borderline_science": 0.85,
        "below_compe_science": 0.70,
    },
    "itu_faculty_research": {
        "top1000_science": 0.94, "borderline_science": 0.90,
        "below_compe_science": 0.82, "top1000_general": 0.72,
    },
    "itu_curriculum_flexibility": {
        "top1000_general": 0.82, "borderline_general": 0.84, "below_compe_general": 0.82,
    },
    "itu_curriculum_details": {
        "top1000_general": 0.88, "borderline_general": 0.88, "below_compe_general": 0.86,
    },
    "itu_academic_workload": {
        "top1000_general": 0.84, "borderline_general": 0.86, "below_compe_general": 0.84,
    },
    "itu_technical_resources": {
        "top1000_science": 0.92, "borderline_science": 0.90, "below_compe_science": 0.86,
    },
    "itu_internship_pathways": {
        "top1000_money": 0.92, "borderline_money": 0.92, "below_compe_money": 0.88,
    },
    "itu_research_projects": {
        "top1000_science": 0.96, "borderline_science": 0.94, "below_compe_science": 0.88,
    },
    "itu_specialization": {
        "top1000_general": 0.90, "borderline_general": 0.90, "below_compe_general": 0.88,
    },
    "itu_double_major_transfer": {
        "top1000_general": 0.86, "borderline_general": 0.86, "below_compe_general": 0.84,
    },
    "itu_erasmus_mobility": {
        "top1000_science": 0.92, "borderline_science": 0.92, "below_compe_science": 0.88,
    },
    "itu_clubs_teams": {
        "top1000_general": 0.86, "borderline_general": 0.86, "below_compe_general": 0.86,
    },
    "itu_housing_details": {
        "top1000_money": 0.92, "borderline_money": 0.92, "below_compe_money": 0.90,
    },
    "itu_istanbul_life": {
        "top1000_general": 0.84, "borderline_general": 0.84, "below_compe_general": 0.84,
    },
    "itu_student_wellbeing": {
        "top1000_general": 0.86, "borderline_general": 0.88, "below_compe_general": 0.88,
    },
    "itu_graduation_requirements": {
        "top1000_general": 0.86, "borderline_general": 0.86, "below_compe_general": 0.84,
    },
    "itu_student_life_support": {
        "top1000_money": 0.86, "borderline_money": 0.88, "below_compe_money": 0.82,
        "top1000_family": 0.82, "borderline_family": 0.84,
    },
    "itu_campus_life": {
        "top1000_general": 0.84, "borderline_general": 0.84, "below_compe_general": 0.82,
    },
    "itu_dining": {
        "top1000_money": 0.86, "borderline_money": 0.86, "below_compe_money": 0.84,
    },
    "itu_career_evidence": {
        "top1000_money": 0.94, "borderline_money": 0.92, "below_compe_money": 0.88,
        "top1000_family": 0.88, "borderline_family": 0.86,
    },
    "itu_english_prep": {
        "top1000_general": 0.86, "borderline_general": 0.86, "below_compe_general": 0.84,
    },
    "itu_compe_differentiators": {
        "top1000_general": 0.92, "borderline_general": 0.90, "below_compe_general": 0.88,
        "top1000_prestige": 0.96, "borderline_prestige": 0.94,
    },
    "itu_financial_support": {
        "top1000_money": 0.96, "borderline_money": 0.94, "below_compe_money": 0.90,
        "top1000_family": 0.88, "borderline_family": 0.88, "below_compe_family": 0.84,
    },
    "itu_entrepreneurship_ecosystem": {
        "top1000_money": 0.95, "borderline_money": 0.90, "below_compe_money": 0.84,
        "top1000_general": 0.82, "borderline_general": 0.80,
    },
    "itu_global_opportunities": {
        "top1000_science": 0.88, "borderline_science": 0.86, "below_compe_science": 0.80,
    },
    "itu_clubs_projects": {
        "top1000_general": 0.78, "borderline_general": 0.78, "below_compe_general": 0.80,
    },
    "itu_admission_reality": {
        "top1000_general": 0.88, "borderline_general": 0.92, "below_compe_general": 0.94,
    },
    "concern_math_difficulty": {
        # Sadece kaygı sinyali varsa aktif
        "top1000_general": 0.85, "borderline_general": 0.90,
        "below_compe_general": 0.85,
    },
    "concern_family_pressure": {
        "top1000_family": 0.90, "borderline_family": 0.90,
        "below_compe_family": 0.85,
    },
    "balanced_perspective": {
        "top1000_general": 0.70, "borderline_general": 0.70,
        "below_compe_general": 0.70,
    },
    "ideal_match_summary": {
        # Kapanış argümanı — S8'de zorla seçilir
    },
    "software_vs_compe": {
        "top1000_general": 0.85, "borderline_general": 0.85, "below_compe_general": 0.85,
        # (yazılım-bilgisayar farkı sorusu geldiğinde bunun eşleşmemesi düşünülemez)
    },
    "university_comparison_general": {
        "top1000_general": 0.80, "borderline_general": 0.80, "below_compe_general": 0.80,
        "top1000_prestige": 0.85, "borderline_prestige": 0.85,
    },
    "future_of_compe": {
        "top1000_general": 0.80, "borderline_general": 0.80, "below_compe_general": 0.80,
        "top1000_family": 0.85, "borderline_family": 0.85,
        # (employment/AI kaygısı çoğu zaman aile kaynaklı geliyor — L08 gibi)
    },
}


# ============ REWARD FUNCTION ============

_REACTION_SCORES = {
    "accepted": 0.92,
    "curious": 0.74,
    "neutral": 0.50,
    "objection": 0.30,
    "rejected": 0.12,
    "topic_shift": 0.28,
    "not_applicable": 0.50,
}


def compute_reward_breakdown(analysis: dict) -> dict:
    """Separate conversational engagement from argument effectiveness.

    A rejection can still be a healthy conversation signal, but it must not
    teach the bandit that the rejected argument was effective.
    """
    intent = analysis.get("intent", "neutral")

    engagement = 0.45
    engagement += {
        "engaged": 0.15,
        "seek_info": 0.12,
        "concern": 0.08,
        "reject": 0.03,
        "close": -0.02,
        "disengaged": -0.20,
    }.get(intent, 0.0)
    engagement += max(-0.10, min(0.10, float(analysis.get("sentiment", 0.0)) * 0.10))
    if analysis.get("new_profile_info"):
        engagement += 0.10
    if analysis.get("asked_followup"):
        engagement += 0.12
    length = int(analysis.get("response_length", 0) or 0)
    if length >= 20:
        engagement += 0.05
    elif length <= 3:
        engagement -= 0.08
    engagement = max(0.0, min(1.0, engagement))

    reaction = analysis.get("argument_reaction", "not_applicable")
    reaction_score = _REACTION_SCORES.get(reaction, 0.50)
    reception = max(0.0, min(1.0, float(analysis.get("reception_signal", 0.5))))
    relevance = max(0.0, min(1.0, float(analysis.get("response_relevance", 0.5))))

    # Relevance controls causal credit: an unrelated follow-up should not be
    # credited to the previous argument.
    effectiveness = (0.55 * reaction_score + 0.30 * reception + 0.15 * relevance)
    if reaction == "topic_shift":
        effectiveness = min(effectiveness, 0.35)
    elif reaction == "rejected":
        effectiveness = min(effectiveness, 0.20)
    effectiveness = max(0.0, min(1.0, effectiveness))

    bandit_reward = 0.35 * engagement + 0.65 * effectiveness
    return {
        "engagement": round(engagement, 3),
        "argument_effectiveness": round(effectiveness, 3),
        "bandit_reward": round(max(0.0, min(1.0, bandit_reward)), 3),
        "reaction": reaction,
        "response_relevance": round(relevance, 3),
    }


def compute_reward(analysis: dict) -> float:
    """Backward-compatible scalar reward used by the bandit."""
    return compute_reward_breakdown(analysis)["bandit_reward"]


# ============ BANDIT ============

@dataclass
class ArmStats:
    n: int = 0                # Toplam çekiliş
    reward_sum: float = 0.0   # Toplam ödül

    def mean(self) -> float:
        return self.reward_sum / self.n if self.n > 0 else 0.0


@dataclass
class SelectionResult:
    argument_id: str
    score: float
    exploration_bonus: float
    reasoning: str
    alternatives: list[tuple[str, float]] = field(default_factory=list)


class ArgumentSelector:
    """UCB1 with contextual priors + repeat penalty."""

    def __init__(self, kappa: float = 1.41, repeat_penalty: float = 0.82,
                 recent_penalty: float = 0.90, cold_start_bonus: float = 0.12):
        self.kappa = kappa
        self.repeat_penalty = repeat_penalty
        self.recent_penalty = recent_penalty
        self.cold_start_bonus = cold_start_bonus

    def _get_stats(self, ctx_stats: dict, key: str) -> ArmStats:
        d = ctx_stats.setdefault(key, {"n": 0, "reward_sum": 0.0})
        return ArmStats(n=d["n"], reward_sum=d["reward_sum"])

    def _set_stats(self, ctx_stats: dict, key: str, stats: ArmStats):
        ctx_stats[key] = {"n": stats.n, "reward_sum": stats.reward_sum}

    def select(
        self,
        user_type: str,
        fsm_state: FSMState,
        profile: CandidateProfile,
        ctx_stats: dict,                # persistent bandit state (in conversation.context)
        recent_arguments: list[str],    # son N turnun argument_id'leri
        eligibility: dict[str, bool] | None = None,  # bazı argümanlar current context'te uygun mu?
        preferred_arguments: list[str] | None = None,
    ) -> SelectionResult:

        # FSM state → hangi argümanlar uygun
        eligible_ids = self._eligible_for_state(fsm_state, profile, eligibility or {})

        if not eligible_ids:
            # Emniyet: en azından socratic_probe her zaman kullanılabilir
            eligible_ids = ["socratic_probe"]

        meta = ctx_stats.setdefault("_meta", {})

        # HARD-BLOCK: son seçilen argüman üst üste tekrar edilemez (alternatif varsa)
        last_arg = recent_arguments[-1] if recent_arguments else None
        if last_arg and last_arg in eligible_ids and len(eligible_ids) > 1:
            eligible_ids = [a for a in eligible_ids if a != last_arg]

        # Sıralama yoksa rank_probe'u öne al — ama EN FAZLA 2 kez sor.
        # Aday cevap vermediyse ısrar etme; deneme sıralamasını doğal akışta öğrenmeye çalış.
        if profile.yks_rank is None and "rank_probe" in eligible_ids:
            rank_probe_count = meta.get("rank_probe_count", 0)
            if rank_probe_count >= 2:
                eligible_ids = [a for a in eligible_ids if a != "rank_probe"] or ["socratic_probe"]
            elif meta.get("total_turns", 0) <= 2:
                meta["rank_probe_count"] = rank_probe_count + 1
                return SelectionResult(
                    argument_id="rank_probe",
                    score=0.95,
                    exploration_bonus=0.0,
                    reasoning="YKS sıralaması bilinmiyor → önce onu al (Majidov Bölüm 3 zorunluluk).",
                )

        # UCB1 skorları
        total_n = sum(self._get_stats(ctx_stats, self._key(user_type, a)).n for a in eligible_ids)
        total_n = max(total_n, 1)

        scores = []
        for arg_id in eligible_ids:
            key = self._key(user_type, arg_id)
            stats = self._get_stats(ctx_stats, key)

            prior = self._prior(arg_id, user_type)

            if stats.n == 0:
                mu = prior
                bonus = self.cold_start_bonus
            else:
                mu = 0.5 * stats.mean() + 0.5 * prior  # prior ile blend (Bayes flavor)
                bonus = self.kappa * math.sqrt(math.log(total_n) / stats.n)
                bonus = min(bonus, 0.30)

            score = mu + bonus

            # Current-turn topic/profile router preference. Explicit questions
            # are forced before this point; this is for softer topic signals.
            if arg_id in (preferred_arguments or []):
                score += 0.22

            # Tekrar cezası
            if recent_arguments and arg_id == recent_arguments[-1]:
                score *= self.repeat_penalty
            elif arg_id in recent_arguments[-3:]:
                score *= self.recent_penalty

            scores.append((arg_id, score, bonus, mu))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_id, top_score, top_bonus, top_mu = scores[0]

        if top_id == "rank_probe":
            meta["rank_probe_count"] = meta.get("rank_probe_count", 0) + 1

        alternatives = [(a, s) for a, s, _, _ in scores[1:4]]

        reasoning = (
            f"user_type={user_type}, prior={top_mu:.2f}, exploration_bonus={top_bonus:.2f}, "
            f"eligible={len(eligible_ids)} argüman."
        )

        return SelectionResult(
            argument_id=top_id,
            score=top_score,
            exploration_bonus=top_bonus,
            reasoning=reasoning,
            alternatives=alternatives,
        )

    def update(self, ctx_stats: dict, user_type: str, argument_id: str, reward: float):
        key = self._key(user_type, argument_id)
        stats = self._get_stats(ctx_stats, key)
        stats.n += 1
        stats.reward_sum += reward
        self._set_stats(ctx_stats, key, stats)

        meta = ctx_stats.setdefault("_meta", {"total_turns": 0})
        meta["total_turns"] = meta.get("total_turns", 0) + 1

    def _key(self, user_type: str, arg_id: str) -> str:
        return f"{user_type}::{arg_id}"

    def _prior(self, arg_id: str, user_type: str) -> float:
        row = PAYOFF_MATRIX.get(arg_id, {})
        if user_type in row:
            return row[user_type]
        # Fallback: yalnızca aynı sıralama bandının _general hücresine düş.
        # (startswith araması yapma — "top1000_science" isteyen, "top1000_family"nin
        #  0.90'ını almamalı; bu concern argümanlarının alakasız seçilmesine yol açıyordu)
        base = user_type.rsplit("_", 1)[0] if "_" in user_type else user_type
        general_key = f"{base}_general"
        if general_key in row:
            return row[general_key]
        return _DEFAULT_PRIOR

    def _eligible_for_state(
        self,
        fsm_state: FSMState,
        profile: CandidateProfile,
        overrides: dict[str, bool],
    ) -> list[str]:
        """FSM state'e ve profile'a göre uygun argümanları filtrele."""

        # Kapanış states — sadece özet argümanı
        if fsm_state == FSMState.S8_IDEAL_MATCH_SUMMARY:
            return ["ideal_match_summary"]

        # Discovery states — probe/dinleme + eğer alan/bölüm alternatifi belirdiyse ilgili argüman
        if fsm_state in (FSMState.S1_GREETING, FSMState.S2_INDECISION_PROBE, FSMState.S2R_PROFILE_UPDATE):
            base = ["socratic_probe", "active_listening"]
            if profile.yks_rank is None:
                base.append("rank_probe")
            # Alternatifler artık canonical (normalize.py) — tekil eşitlik yeter
            ind = profile.indecision
            if "tip" in ind.field_alternatives:
                base.append("med_vs_eng_health_tech")
            if "koc" in ind.university_alternatives:
                base.append("koc_vs_itu_value")
            if "yapay_zeka_veri" in ind.department_alternatives:
                base.append("ai_vs_compe_foundation")
            if any(d in ind.department_alternatives for d in ("elektronik_haberlesme", "elektrik", "kontrol_otomasyon")):
                base.append("electronics_vs_compe_overlap")
            if "yazilim" in ind.department_alternatives or ind.target_department == "yazilim":
                base.append("software_vs_compe")
            if any(u in ind.university_alternatives for u in ("bogazici", "sabanci", "ytu", "bilkent", "odtu")):
                base.append("university_comparison_general")
            return base

        # Concern handling — kaygı-özel argümanlar YALNIZCA ilgili kaygı profilde varsa açılır.
        # (Bilinmeyen kaygıda genel argümanlar yeter; math/family'yi körlemesine açmak
        #  XAI kaydını kirletiyordu — uzun senaryo testi L01/L02 bulgusu)
        if fsm_state == FSMState.S7_CONCERN_HANDLING:
            args = ["active_listening", "balanced_perspective", "socratic_probe"]
            if any(c in profile.concerns for c in ("math", "difficulty", "self_efficacy")):
                args.append("concern_math_difficulty")
            if "family" in profile.concerns:
                args.append("concern_family_pressure")
            if "employment" in profile.concerns:
                args.append("future_of_compe")   # "AI işimizi alacak / işsiz kalırım" kaygısı
            if "cost" in profile.concerns:
                args.append("itu_financial_support")
            return args

        # RAG deep dive — bilgilendirici argümanlar
        if fsm_state == FSMState.S6_RAG_DEEP_DIVE:
            args = [
                "science_motivated_labs", "money_motivated_data",
                "ai_vs_compe_foundation", "electronics_vs_compe_overlap",
                "koc_vs_itu_value", "balanced_perspective",
                "itu_faculty_research", "itu_curriculum_flexibility",
                "itu_first_year_curriculum", "itu_curriculum_beginner", "itu_curriculum_overview",
                "itu_curriculum_details", "itu_academic_workload", "itu_technical_resources",
                "itu_internship_pathways", "itu_research_projects", "itu_specialization",
                "itu_double_major_transfer", "itu_erasmus_mobility", "itu_clubs_teams",
                "itu_housing_details", "itu_istanbul_life", "itu_student_wellbeing",
                "itu_graduation_requirements",
                "itu_student_life_support", "itu_global_opportunities",
                "itu_financial_support", "itu_entrepreneurship_ecosystem",
                "itu_clubs_projects", "itu_admission_reality",
                "itu_campus_life", "itu_dining", "itu_career_evidence",
                "itu_english_prep", "itu_compe_differentiators",
            ]
            if "yazilim" in profile.indecision.department_alternatives or \
               profile.indecision.target_department == "yazilim":
                args.append("software_vs_compe")
            if any(u in profile.indecision.university_alternatives
                   for u in ("bogazici", "sabanci", "ytu", "bilkent", "odtu")):
                args.append("university_comparison_general")
            if "employment" in profile.concerns:
                args.append("future_of_compe")
            return args

        # Argument selection & reception eval — full katalog
        # (bazı argümanlar profil şartı ister)
        eligible = []
        ind = profile.indecision

        # Sıralamaya göre ana argümanlar
        if profile.yks_rank is not None:
            if profile.yks_rank <= 1000:
                eligible.append("compe_priority_top1000")
            elif profile.yks_rank <= 1500:
                eligible.append("compe_borderline_1000_1500")

        # Alternatif-tetikli argümanlar (canonical değerler — normalize.py garantisi)
        if "tip" in ind.field_alternatives:
            eligible.append("med_vs_eng_health_tech")
        if "koc" in ind.university_alternatives:
            eligible.append("koc_vs_itu_value")
        if any(u in ind.university_alternatives for u in ("bogazici", "sabanci", "ytu", "bilkent", "odtu")):
            eligible.append("university_comparison_general")
        if "yapay_zeka_veri" in ind.department_alternatives:
            eligible.append("ai_vs_compe_foundation")
        if any(d in ind.department_alternatives for d in ("elektronik_haberlesme", "elektrik", "kontrol_otomasyon")):
            eligible.append("electronics_vs_compe_overlap")
        if "yazilim" in ind.department_alternatives or ind.target_department == "yazilim":
            eligible.append("software_vs_compe")
        if "employment" in profile.concerns:
            eligible.append("future_of_compe")

        # Motivasyon-tetikli argümanlar
        dom = ind.dominant_motivation()
        if dom == "entrepreneurship":
            eligible.append("itu_entrepreneurship_ecosystem")
        elif dom == "money":
            eligible.append("money_motivated_data")
        elif dom in ("science", "abroad"):
            eligible.append("science_motivated_labs")

        # Kısıt-tetikli argümanlar — aday sadece ilgiyle karar vermiyor
        c = profile.constraints
        if c.cost_sensitivity is not None and c.cost_sensitivity >= 0.5:
            eligible.append("itu_financial_support")
        if c.abroad_goal is not None and c.abroad_goal >= 0.5:
            eligible.append("science_motivated_labs")  # Erasmus + çift diploma + İngilizce
        if c.family_influence is not None and c.family_influence >= 0.6:
            eligible.append("concern_family_pressure")

        # Her zaman opsiyon
        eligible.extend(["active_listening", "balanced_perspective", "socratic_probe"])

        # Aday kaygı belirtmiş — kaygı argümanlarını da aç
        if "math" in profile.concerns or "difficulty" in profile.concerns:
            eligible.append("concern_math_difficulty")
        if "family" in profile.concerns:
            eligible.append("concern_family_pressure")
        if "cost" in profile.concerns:
            eligible.append("itu_financial_support")

        # Uniqueness + revealed_arguments filter
        eligible = list(set(eligible))
        eligible = [a for a in eligible if a not in profile.revealed_arguments[-4:]]

        return eligible or ["balanced_perspective"]
