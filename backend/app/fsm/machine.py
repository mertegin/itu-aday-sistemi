"""FSM — state transition mantığı.

Her state için priority-ordered `(condition_fn, to_state, trigger, weight)` listesi.
`transition()` ilk eşleşen satırı alır. `context` dict'i tüm predikat sinyallerini içerir.
"""
from dataclasses import dataclass
from typing import Callable

from .states import FSMState


@dataclass
class TransitionResult:
    from_state: FSMState
    to_state: FSMState
    trigger: str
    weight: float


# ============ PREDİKATLAR ============

def _has_fallback_signal(ctx: dict) -> bool:
    return bool(ctx.get("fallback_needed", False))


def _is_first_turn(ctx: dict) -> bool:
    return ctx.get("turn_count", 0) <= 1


def _rank_known(ctx: dict) -> bool:
    return ctx.get("yks_rank") is not None


def _new_profile_info(ctx: dict) -> bool:
    """Yeni önemli bilgi ortaya çıktı — profili güncellememiz gerekiyor."""
    return bool(ctx.get("new_profile_info", False))


def _has_concern(ctx: dict) -> bool:
    return ctx.get("intent") == "concern" or bool(ctx.get("has_objection", False))


def _wants_detail(ctx: dict) -> bool:
    return ctx.get("intent") == "seek_info" or bool(ctx.get("wants_detail", False))


def _positive_reception(ctx: dict) -> bool:
    return ctx.get("reception_signal", 0.5) >= 0.6


def _negative_reception(ctx: dict) -> bool:
    return ctx.get("reception_signal", 0.5) <= 0.3


def _wants_close(ctx: dict) -> bool:
    # Aktif bir soru varken ASLA kapanışa gitme — "burs var mı?" gibi sorular
    # S8 özetine kurban gidiyordu (sess_1329 ping-pong bulgusu).
    if ctx.get("asked_followup") or ctx.get("wants_detail"):
        return False
    return (
        ctx.get("intent") == "close"
        or ctx.get("decision_status") == "itu_compe_committed"
    )


def _soft_limit_reached(ctx: dict) -> bool:
    """Long conversations close only when they have actually gone quiet."""
    return (
        ctx.get("turn_count", 0) >= 18
        and ctx.get("intent") in ("neutral", "disengaged")
        and not ctx.get("wants_detail", False)
        and not ctx.get("new_profile_info", False)
    )


def _profile_ready_for_matching(ctx: dict) -> bool:
    """Yeterli profil var mı? Sıralama + (ilgi ALTERNATİF alan/bölüm sinyali) bilinmeli.

    Aday'ın kararsızlığı ANLAŞILMIŞ olsa yeter — "ilgi alanı"nı zorlayıp probe'da takılma.
    """
    if not _rank_known(ctx):
        return False
    if ctx.get("interests_known", 0) >= 1:
        return True
    # Alan/üniversite/bölüm alternatifleri de aday'ın gerçek karar noktasını gösterir
    if ctx.get("has_field_alternatives") or ctx.get("has_dept_alternatives") or ctx.get("has_univ_alternatives"):
        return True
    # Dominant motivasyon belirdiyse de yeter
    if ctx.get("has_dominant_motivation"):
        return True
    return False


def _greeting_done(ctx: dict) -> bool:
    return ctx.get("greeting_done", False) or ctx.get("turn_count", 0) >= 1


def _always(ctx: dict) -> bool:
    return True


# ============ TRANSITION TABLE ============

# Her state → priority-ordered list of (predicate, to_state, trigger, weight)
TRANSITION_TABLE: dict[FSMState, list[tuple[Callable[[dict], bool], FSMState, str, float]]] = {

    FSMState.S0_FALLBACK: [
        (_greeting_done, FSMState.S2_INDECISION_PROBE, "fallback_recovered_probe", 0.7),
        (_always, FSMState.S1_GREETING, "fallback_to_greeting", 0.7),
    ],

    FSMState.S1_GREETING: [
        (_has_fallback_signal, FSMState.S0_FALLBACK, "fallback", 0.9),
        (_wants_close, FSMState.S8_IDEAL_MATCH_SUMMARY, "close_from_greeting", 0.8),
        (_has_concern, FSMState.S7_CONCERN_HANDLING, "concern_from_greeting", 0.85),
        (_greeting_done, FSMState.S2_INDECISION_PROBE, "greeting_to_probe", 0.9),
        (_always, FSMState.S1_GREETING, "stay_greeting", 0.5),
    ],

    FSMState.S2_INDECISION_PROBE: [
        (_has_fallback_signal, FSMState.S0_FALLBACK, "fallback", 0.9),
        (_has_concern, FSMState.S7_CONCERN_HANDLING, "concern_during_probe", 0.9),
        (_wants_close, FSMState.S8_IDEAL_MATCH_SUMMARY, "close_during_probe", 0.8),
        (_new_profile_info, FSMState.S2R_PROFILE_UPDATE, "new_info_during_probe", 0.85),
        (_profile_ready_for_matching, FSMState.S4_ARGUMENT_DELIVERY, "profile_ready_deliver", 0.95),
        (_always, FSMState.S2_INDECISION_PROBE, "keep_probing", 0.6),
    ],

    FSMState.S2R_PROFILE_UPDATE: [
        (_wants_close, FSMState.S8_IDEAL_MATCH_SUMMARY, "close_after_update", 0.85),
        (_has_concern, FSMState.S7_CONCERN_HANDLING, "concern_after_update", 0.9),
        (_profile_ready_for_matching, FSMState.S4_ARGUMENT_DELIVERY, "ready_after_update_deliver", 0.95),
        (_always, FSMState.S2_INDECISION_PROBE, "back_to_probe", 0.7),
    ],

    FSMState.S3_ARGUMENT_SELECTION: [
        # Legacy sessions may still be persisted in S3. Respect the current
        # message before collapsing this internal computation state into S4.
        (_has_fallback_signal, FSMState.S0_FALLBACK, "fallback", 0.9),
        (_wants_close, FSMState.S8_IDEAL_MATCH_SUMMARY, "close_during_selection", 0.9),
        (_has_concern, FSMState.S7_CONCERN_HANDLING, "concern_during_selection", 0.9),
        (_wants_detail, FSMState.S6_RAG_DEEP_DIVE, "detail_during_selection", 0.88),
        (_new_profile_info, FSMState.S2R_PROFILE_UPDATE, "new_info_during_selection", 0.85),
        (_always, FSMState.S4_ARGUMENT_DELIVERY, "argument_selected", 0.9),
    ],

    FSMState.S4_ARGUMENT_DELIVERY: [
        (_has_fallback_signal, FSMState.S0_FALLBACK, "fallback", 0.9),
        (_wants_close, FSMState.S8_IDEAL_MATCH_SUMMARY, "close_after_argument", 0.85),
        (_has_concern, FSMState.S7_CONCERN_HANDLING, "concern_after_argument", 0.9),
        (_wants_detail, FSMState.S6_RAG_DEEP_DIVE, "wants_detail", 0.85),
        (_new_profile_info, FSMState.S2R_PROFILE_UPDATE, "new_info_after_argument", 0.85),
        (_always, FSMState.S5_RECEPTION_EVAL, "eval_reception", 0.9),
    ],

    FSMState.S5_RECEPTION_EVAL: [
        (_wants_close, FSMState.S8_IDEAL_MATCH_SUMMARY, "close_at_eval", 0.85),
        (_negative_reception, FSMState.S7_CONCERN_HANDLING, "negative_reaction", 0.85),
        (_wants_detail, FSMState.S6_RAG_DEEP_DIVE, "wants_more_detail", 0.85),
        (_positive_reception, FSMState.S4_ARGUMENT_DELIVERY, "positive_deepen_deliver", 0.85),
        (_new_profile_info, FSMState.S2R_PROFILE_UPDATE, "new_info_at_eval", 0.8),
        (_soft_limit_reached, FSMState.S8_IDEAL_MATCH_SUMMARY, "soft_limit_summary", 0.7),
        (_always, FSMState.S4_ARGUMENT_DELIVERY, "continue_arguments_deliver", 0.6),
    ],

    FSMState.S6_RAG_DEEP_DIVE: [
        (_has_concern, FSMState.S7_CONCERN_HANDLING, "concern_after_detail", 0.9),
        (_wants_close, FSMState.S8_IDEAL_MATCH_SUMMARY, "close_after_detail", 0.85),
        (_always, FSMState.S5_RECEPTION_EVAL, "eval_after_detail", 0.85),
    ],

    FSMState.S7_CONCERN_HANDLING: [
        (_wants_close, FSMState.S8_IDEAL_MATCH_SUMMARY, "close_after_concern", 0.85),
        (_positive_reception, FSMState.S4_ARGUMENT_DELIVERY, "concern_resolved_deliver", 0.85),
        (_new_profile_info, FSMState.S2R_PROFILE_UPDATE, "new_info_after_concern", 0.8),
        (_always, FSMState.S5_RECEPTION_EVAL, "eval_after_concern", 0.7),
    ],

    FSMState.S8_IDEAL_MATCH_SUMMARY: [
        (_has_concern, FSMState.S7_CONCERN_HANDLING, "reopen_summary_concern", 0.92),
        (_wants_detail, FSMState.S6_RAG_DEEP_DIVE, "reopen_summary_detail", 0.92),
        (_new_profile_info, FSMState.S2R_PROFILE_UPDATE, "reopen_summary_new_info", 0.88),
        (_wants_close, FSMState.S9_CLOSING, "summary_to_closing", 0.9),
        (_always, FSMState.S4_ARGUMENT_DELIVERY, "reopen_summary_continue", 0.75),
    ],

    FSMState.S9_CLOSING: [
        (_has_concern, FSMState.S7_CONCERN_HANDLING, "reopen_closed_concern", 0.92),
        (_wants_detail, FSMState.S6_RAG_DEEP_DIVE, "reopen_closed_detail", 0.92),
        (_new_profile_info, FSMState.S2R_PROFILE_UPDATE, "reopen_closed_new_info", 0.88),
        (_wants_close, FSMState.S9_CLOSING, "stay_closed", 0.9),
        (_always, FSMState.S4_ARGUMENT_DELIVERY, "reopen_closed_continue", 0.75),
    ],
}


class NegotiationFSM:
    def __init__(self, current: FSMState):
        self.current = current

    def transition(self, ctx: dict) -> TransitionResult:
        rows = TRANSITION_TABLE.get(self.current, [])
        for pred, to_state, trigger, weight in rows:
            try:
                if pred(ctx):
                    return TransitionResult(self.current, to_state, trigger, weight)
            except Exception:
                # Predikat exception atarsa görmezden gel, sonrakini dene
                continue
        # Hiçbir predikat eşleşmezse: yerinde kal (güvenli fallback)
        return TransitionResult(self.current, self.current, "no_match", 0.3)
