"""Orchestrator — per-turn negotiation pipeline.

Adım:
1. Load conversation + profile + bandit stats
2. Analyze user message (LLM analyzer)
3. Update profile from analysis
4. Build FSM context, transition
5. Bandit reward for previous arm (using this turn's engagement signals)
6. Select next argument
7. LLM generate response
8. Ethics guardrail
9. Persist message + strategy log
10. Return response + XAI meta
"""
import json
import uuid
from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .arguments.catalog import get_argument
from .fsm.machine import NegotiationFSM
from .fsm.states import FSMState
from .guardrails.ethics import EthicsFilter, enforce_conversation_voice, enforce_spoken_length
from .kb.fact_gate import (
    build_safe_response,
    enforce_answer_relevance,
    enforce_fact_gate,
    enforce_non_repetition,
    enforce_scholarship_eligibility,
)
from .kb.evidence_gate import enforce_evidence_contract
from .kb.retriever import retrieve_facts
from .llm.client import LLMClient
from .models.db import Conversation, Message, StrategyLog
from .profile.schema import CandidateProfile
from .strategy.bandit import ArgumentSelector, compute_reward_breakdown, derive_user_type
from .strategy.router import route_current_turn
from .strategy.utility import apply_utility_overlay
from .xai.engine import build_explanation


class Orchestrator:
    def __init__(self, llm_client=None):
        from .config import settings
        self.llm = llm_client or LLMClient()
        self.selector = ArgumentSelector(
            kappa=settings.bandit_kappa,
            repeat_penalty=settings.bandit_repeat_penalty,
            recent_penalty=settings.bandit_recent_penalty,
            cold_start_bonus=settings.bandit_cold_start_bonus,
        )
        self.ethics = EthicsFilter()

    async def handle_turn(self, session_id: str, text: str, db: AsyncSession) -> dict:
        # 1. Load or create conversation
        conv = await self._get_or_create_conversation(session_id, db)
        profile = CandidateProfile.from_dict(conv.profile or {})
        # JSON columns are not mutation-tracked deeply; a fresh outer dict makes
        # last_route and nested bandit updates persist on every turn.
        ctx = dict(conv.context or {})
        bandit_stats = ctx.setdefault("bandit_stats", {})

        # 2. Analyze user message
        history = await self._load_history(conv.id, db)
        self._backfill_identity_from_history(profile, history)
        analysis = await self.llm.analyze_message(text, history)

        # 3. Update profile from analysis (provenance ile — turn numarası kaydedilir)
        current_turn = (conv.turn_count or 0) + 1
        self._update_profile_from_analysis(profile, analysis, current_turn, text)

        # 4. Update engagement based on analysis (before bandit reward)
        profile.engagement_level = self._compute_engagement(analysis, profile.engagement_level)
        profile.reception_signal = float(analysis.get("reception_signal", 0.5))
        profile.trust_level = self._compute_trust(analysis, profile.trust_level)

        # 5. Bandit reward for previous arm (compute_reward from this turn's analysis)
        prev_arg = ctx.get("last_argument_id")
        prev_user_type = ctx.get("last_user_type")
        reward_computed = None
        reward_breakdown = None
        if prev_arg and prev_user_type:
            reward_breakdown = compute_reward_breakdown({
                "intent": analysis.get("intent", "neutral"),
                "sentiment": analysis.get("sentiment", 0.0),
                "new_profile_info": analysis.get("new_profile_info", False),
                "asked_followup": analysis.get("asked_followup", False),
                "response_length": analysis.get("response_length", 0),
                "reception_signal": analysis.get("reception_signal", 0.5),
                "response_relevance": analysis.get("response_relevance", 0.5),
                "argument_reaction": analysis.get("argument_reaction", "not_applicable"),
            })
            reward = reward_breakdown["bandit_reward"]
            self.selector.update(bandit_stats, prev_user_type, prev_arg, reward)
            reward_computed = reward

        # 6. Persist user message
        await self._save_message(conv.id, "user", text, db)
        conv.turn_count = (conv.turn_count or 0) + 1

        # 7. FSM transition
        fsm_ctx = self._build_fsm_context(conv, profile, analysis)
        fsm = NegotiationFSM(FSMState(conv.fsm_state))
        transition = fsm.transition(fsm_ctx)
        conv.fsm_state = transition.to_state.value
        profile.indecision.decision_stage = self._decision_stage(transition.to_state)

        # 8. Select argument
        user_type = derive_user_type(profile)
        route = route_current_turn(text, analysis, profile, previous_route=ctx.get("last_route"))
        for topic in route.topics:
            if topic not in profile.covered_topics:
                profile.covered_topics.append(topic)
        if len(profile.covered_topics) > 30:
            profile.covered_topics = profile.covered_topics[-30:]

        utility_meta = {
            "overridden": False,
            "reason": "Current-turn router doğrudan seçim yaptı.",
        }
        # ÖNCELİK: adayın GÜNCEL sorusu (route force) her zaman kazanır — S8 özeti bile ezemez.
        # (sess_1329 bulgusu: "burs var mı?" sorusu S8 ping-pong'unda özet argümanına eziliyordu)
        if route.forced_argument_id:
            selection = self._forced_selection(
                route.forced_argument_id,
                f"Current-turn router: {route.reason}",
                score=route.confidence,
            )
        elif transition.to_state == FSMState.S8_IDEAL_MATCH_SUMMARY:
            selection = self._forced_selection("ideal_match_summary", "FSM kapanış özeti seçti.")
        else:
            selection = self.selector.select(
                user_type=user_type,
                fsm_state=transition.to_state,
                profile=profile,
                ctx_stats=bandit_stats,
                recent_arguments=profile.revealed_arguments,
                preferred_arguments=route.preferred_arguments,
            )
            utility_decision = apply_utility_overlay(
                selection=selection,
                profile=profile,
                fsm_state=transition.to_state,
                route=route,
            )
            selection = utility_decision.selection
            utility_meta = utility_decision.to_dict()

        argument = get_argument(selection.argument_id)
        if argument is None:
            argument = get_argument("balanced_perspective")

        # 8.5. Topic-aware RAG: bu turdaki soru/argüman/profil için ilgili fact'leri seç.
        rag_result = retrieve_facts(
            user_text=text,
            profile=profile,
            argument_id=argument.id,
            max_facts=6,
        )

        # 9. Build XAI explanation
        explanation = build_explanation(
            argument_id=selection.argument_id,
            fsm_from=transition.from_state.value,
            fsm_to=transition.to_state.value,
            fsm_trigger=transition.trigger,
            fsm_weight=transition.weight,
            user_type=user_type,
            profile=profile,
            bandit_score=selection.score,
            exploration_bonus=selection.exploration_bonus,
            alternatives=selection.alternatives,
            policy_meta={
                "route": route.to_dict(),
                "utility": utility_meta,
                "previous_reward": reward_breakdown,
            },
        )

        # 10. LLM generate response
        response_text = await self.llm.generate_response(
            argument_id=argument.id,
            argument_label=argument.label,
            argument_technique=argument.technique,
            talking_points=argument.talking_points,
            expected_pushback=argument.expected_pushback,
            profile_summary=self._profile_summary(profile),
            fsm_state=transition.to_state.value,
            turn_count=conv.turn_count,
            main_indecision_axis=profile.indecision.main_indecision_axis(),
            dominant_motivation=profile.indecision.dominant_motivation(),
            revealed_arguments=profile.revealed_arguments,
            history=history + [{"role": "user", "text": text}],
            rag_context=rag_result.prompt_block(),
        )

        generation_fallback = {
            "used": False,
            "reason": None,
        }
        if response_text.lstrip().startswith("(Sistem hatası"):
            generation_fallback = {
                "used": True,
                "reason": response_text,
            }
            response_text = build_safe_response(rag_result, question=text, compact=True)

        # 11. Ethics guardrail — sanitize + check + gerekirse güvenli metinle değiştir
        response_text, ethics_result = self.ethics.enforce(response_text)
        response_text, fact_gate_result = enforce_fact_gate(response_text, rag_result, question=text)
        response_text, relevance_result = enforce_answer_relevance(response_text, rag_result, text)
        response_text, scholarship_result = enforce_scholarship_eligibility(response_text, rag_result, text)
        fact_gate_result["scholarship_eligibility"] = scholarship_result
        response_text, pre_evidence_speech = enforce_spoken_length(response_text, max_words=65)
        response_text, evidence_result = enforce_evidence_contract(
            response_text,
            rag_result,
            argument.id,
        )
        response_text, repetition_result = enforce_non_repetition(
            response_text,
            rag_result,
            text,
            history,
        )
        allow_followup = self._should_ask_followup(history, analysis, argument.id)
        response_text, followup_result = self._append_contextual_followup(
            response_text,
            route.primary_topic,
            argument.id,
            allow_followup,
            history,
            text,
        )
        response_text, voice_result = enforce_conversation_voice(
            response_text,
            argument.id,
            user_asked_question=bool(analysis.get("asked_followup")),
            wants_detail=bool(analysis.get("wants_detail")),
            allow_followup=allow_followup,
        )
        response_text, speech_result = enforce_spoken_length(response_text, max_words=65)
        evidence_result["pre_evidence_speech"] = pre_evidence_speech

        # 12. Update profile with newly revealed argument
        profile.revealed_arguments.append(argument.id)
        # trim
        if len(profile.revealed_arguments) > 20:
            profile.revealed_arguments = profile.revealed_arguments[-20:]

        # 13. Persist assistant message + strategy log
        await self._save_message(conv.id, "assistant", response_text, db)

        strat_log = StrategyLog(
            conversation_id=conv.id,
            turn=conv.turn_count,
            fsm_from=transition.from_state.value,
            fsm_to=transition.to_state.value,
            fsm_trigger=transition.trigger,
            argument_id=argument.id,
            reward=reward_computed,
            xai_reason=explanation.reason_tr,
            decision_factors=explanation.decision_factors,
        )
        db.add(strat_log)

        # 14. Save conversation state
        ctx["last_argument_id"] = argument.id
        ctx["last_user_type"] = user_type
        ctx["last_route"] = route.to_dict()
        ctx["last_reward_breakdown"] = reward_breakdown
        ctx["greeting_done"] = True if conv.turn_count >= 1 else False
        ctx["bandit_stats"] = bandit_stats
        conv.context = ctx
        conv.profile = profile.to_dict()
        if profile.display_name and not conv.display_name:
            conv.display_name = profile.display_name

        await db.commit()

        # 15. Return
        from .profile.academic import risk_band, risk_bands_for, eligible_departments

        # Adayın masasındaki bölümler: bilgisayar (hedefimiz) + adayın hedefi + alternatifleri
        table_departments = ["bilgisayar"]
        if profile.indecision.target_department:
            table_departments.append(profile.indecision.target_department)
        table_departments.extend(profile.indecision.department_alternatives)

        return {
            "session_id": session_id,
            "response_text": response_text,
            "xai_meta": explanation.to_dict(),
            "profile": profile.to_dict(),
            "academic": {
                "risk_band": risk_band(profile.yks_rank, "bilgisayar"),  # geriye uyum
                "risk_bands": risk_bands_for(profile.yks_rank, table_departments),
                "eligible_departments": eligible_departments(profile.yks_rank),
            },
            "fsm_state": conv.fsm_state,
            "turn_count": conv.turn_count,
            "reward_previous_turn": reward_computed,
            "reward_breakdown_previous_turn": reward_breakdown,
            "ethics_check": ethics_result,
            "voice_check": voice_result,
            "fact_gate": fact_gate_result,
            "answer_relevance": relevance_result,
            "repetition_check": repetition_result,
            "followup_check": followup_result,
            "evidence_check": evidence_result,
            "generation_fallback": generation_fallback,
            "speech_check": speech_result,
            "rag": rag_result.to_dict(),
            "analysis": analysis,
        }

    # ============ HELPERS ============

    @staticmethod
    def _should_ask_followup(history: list[dict], analysis: dict, argument_id: str) -> bool:
        if argument_id in {"socratic_probe", "rank_probe", "koc_vs_itu_value"}:
            return True
        if analysis.get("intent") in {"close", "disengaged", "reject"}:
            return False
        recent_assistant = [
            str(message.get("text", ""))
            for message in history
            if message.get("role") == "assistant"
        ][-2:]
        return not any("?" in message for message in recent_assistant)

    @staticmethod
    def _append_contextual_followup(
        text: str,
        primary_topic: str,
        argument_id: str,
        allowed: bool,
        history: list[dict],
        user_text: str,
    ) -> tuple[str, dict]:
        if not allowed:
            return text, {"added": False, "reason": "not_needed"}

        from .kb.fact_gate import split_sentences_tr

        previous_assistant = [
            str(message.get("text", ""))
            for message in history
            if message.get("role") == "assistant"
        ]
        used_questions = {
            " ".join(sentence.casefold().split())
            for answer in previous_assistant
            for sentence in split_sentences_tr(answer)
            if sentence.rstrip().endswith("?")
        }

        repeated_removed = None
        current_sentences = split_sentences_tr(text)
        if current_sentences and current_sentences[-1].rstrip().endswith("?"):
            trailing = current_sentences[-1].strip()
            if " ".join(trailing.casefold().split()) in used_questions and len(current_sentences) > 1:
                repeated_removed = trailing
                text = " ".join(current_sentences[:-1]).strip()
            else:
                return text, {"added": False, "reason": "model_asked_question"}

        topic_questions = {
            "faculty_research": [
                "Sen hocalarla daha çok ders desteği için mi, yoksa erkenden bir projeye katılmak için mi iletişim kurmak istiyorsun?",
                "Hoca iletişiminde seni düşündüren şey e-postana dönüş almak mı, yoksa birebir görüşebilmek mi?",
            ],
            "academic_workload": ["Seni daha çok kod yazmak mı, yoksa matematiksel analiz kısmı mı düşündürüyor?"],
            "difficulty": ["Seni daha çok kod yazmak mı, yoksa matematiksel analiz kısmı mı düşündürüyor?"],
            "financial_support": ["Maddi tarafta senin için aylık burs mu, yoksa yurt desteği mi daha kritik?"],
            "housing_details": ["Yurtta senin için oda tipi mi, bütçe mi, yoksa kampüse yakınlık mı daha önemli?"],
            "career_evidence": ["Kariyerde hedefin büyük bir teknoloji şirketi mi, girişim mi, yoksa araştırma tarafı mı?"],
            "career": ["Kariyerde hedefin büyük bir teknoloji şirketi mi, girişim mi, yoksa araştırma tarafı mı?"],
            "campus_life": ["Kampüste senin için sosyal ortam mı, spor imkânı mı daha belirleyici?"],
            "clubs_teams": ["Sen daha çok yazılım ekibine mi, robotik-İHA tarafına mı yakınsın?"],
            "curriculum_year1": ["Şimdiden en çok yazılım, yapay zekâ, donanım veya siber güvenlikten hangisi ilgini çekiyor?"],
            "curriculum_details": ["Şimdiden en çok yazılım, yapay zekâ, donanım veya siber güvenlikten hangisi ilgini çekiyor?"],
            "dept_info": ["Şimdiden en çok yazılım, yapay zekâ, donanım veya siber güvenlikten hangisi ilgini çekiyor?"],
            "comparison": ["Kararında eğitim, kampüs, maliyet ve kariyerden hangisi daha ağır basıyor?"],
            "comparison_financial_offer": ["Koç'un teklif ettiği desteğin net aylık veya yıllık tutarı ne kadar?"],
            "differentiators": ["Kararında eğitim, kampüs, maliyet ve kariyerden hangisi daha ağır basıyor?"],
        }
        candidates = list(topic_questions.get(primary_topic, []))
        folded_user = user_text.casefold()
        if argument_id == "koc_vs_itu_value" and any(word in folded_user for word in ("para", "burs", "teklif")):
            candidates = topic_questions["comparison_financial_offer"] + candidates
        if not candidates and argument_id == "itu_faculty_research":
            candidates = topic_questions["faculty_research"]
        for question in candidates:
            if " ".join(question.casefold().split()) not in used_questions:
                return f"{text.rstrip()} {question}", {
                    "added": True,
                    "question": question,
                    "repeated_removed": repeated_removed,
                }
        return text, {
            "added": False,
            "reason": "all_topic_questions_used",
            "repeated_removed": repeated_removed,
        }

    async def _get_or_create_conversation(self, session_id: str, db: AsyncSession) -> Conversation:
        result = await db.execute(select(Conversation).where(Conversation.session_id == session_id))
        conv = result.scalar_one_or_none()
        if conv:
            return conv
        conv = Conversation(
            session_id=session_id,
            fsm_state=FSMState.S1_GREETING.value,
            context={},
            profile={},
            turn_count=0,
        )
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
        return conv

    async def _load_history(self, conv_id: int, db: AsyncSession) -> list[dict]:
        result = await db.execute(
            select(Message).where(Message.conversation_id == conv_id).order_by(Message.id.asc())
        )
        msgs = result.scalars().all()
        return [{"role": m.role, "text": m.text} for m in msgs]

    @staticmethod
    def _backfill_identity_from_history(profile: CandidateProfile, history: list[dict]) -> None:
        """Recover deterministic identity fields missing in conversations created by older parsers."""
        user_turn = 0
        for message in history:
            if message.get("role") != "user":
                continue
            user_turn += 1
            text = str(message.get("text", ""))
            if profile.display_name is None:
                name = LLMClient._extract_display_name(text)
                if name is not None:
                    profile.display_name = name
                    profile.record_provenance("display_name", 0.95, user_turn, text)
            if profile.yks_rank is None:
                rank = LLMClient._extract_rank(text)
                if rank is not None:
                    profile.yks_rank = rank
                    profile.yks_rank_type = "actual"
                    profile.record_provenance("yks_rank", profile.rank_confidence(), user_turn, text)
            if profile.display_name is not None and profile.yks_rank is not None:
                break

    async def _save_message(self, conv_id: int, role: str, text: str, db: AsyncSession):
        msg = Message(conversation_id=conv_id, role=role, text=text)
        db.add(msg)

    def _update_profile_from_analysis(self, profile: CandidateProfile, analysis: dict,
                                      turn: int, user_text: str = ""):
        from .profile.schema import MOTIVATION_KEYS
        evidence = user_text[:100]
        folded_user = user_text.lower().translate(str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU"))

        # İsim ("ben Deniz", "adım Zeynep"...)
        explicit_name = LLMClient._extract_display_name(user_text)
        if explicit_name and not profile.display_name:
            profile.display_name = explicit_name.strip().title()
            profile.record_provenance("display_name", 0.95, turn, evidence)

        # Rank — confidence tipine göre (actual > practice > target)
        explicit_rank = LLMClient._extract_rank(user_text)
        if explicit_rank is not None:
            profile.yks_rank = explicit_rank
            profile.yks_rank_type = analysis.get("yks_rank_type") or "actual"
            profile.record_provenance("yks_rank", profile.rank_confidence(), turn, evidence)

        from .profile.normalize import normalize_department, normalize_field, normalize_university, TARGET_DEPT

        # Field — canonical normalize ("tıp"/"doktorluk"/"medicine" → "tip")
        f = analysis.get("field_signals", {})
        if f.get("engineering_certain") is not None:
            profile.indecision.field_certainty = float(f["engineering_certain"])
        for alt in f.get("field_alternatives_mentioned", []):
            canon = normalize_field(alt)
            if canon and canon not in profile.indecision.field_alternatives:
                profile.activate_alternative("field", canon, turn)
                profile.indecision.field_alternatives.append(canon)
                profile.record_provenance(f"field_alt:{canon}", 0.90, turn, evidence)

        # University — canonical normalize ("koç"/"Koc üniversitesi" → "koc")
        u = analysis.get("university_signals", {})
        if u.get("itu_certain") is not None:
            profile.indecision.university_certainty = float(u["itu_certain"])
        for alt in u.get("university_alternatives_mentioned", []):
            canon = normalize_university(alt)
            if canon == "itu":
                continue  # İTÜ alternatif değil, bizim okulumuz
            if canon and canon not in profile.indecision.university_alternatives:
                profile.activate_alternative("university", canon, turn)
                profile.indecision.university_alternatives.append(canon)
                profile.record_provenance(f"univ_alt:{canon}", 0.90, turn, evidence)

        # Department — canonical normalize + HEDEF/ALTERNATİF ayrımı.
        # "bilgisayar" alternatif listesine GİRMEZ: o bizim hedef bölümümüz —
        # geldiyse certainty sinyalidir (aday bilgisayarı masaya koymuş demektir).
        d = analysis.get("department_signals", {})
        if d.get("compe_certain") is not None and "bilgisayar" in folded_user:
            profile.indecision.department_certainty = float(d["compe_certain"])

        target_raw = d.get("target_department_mentioned")
        if target_raw:
            target_canon = normalize_department(target_raw)
            target_terms = {
                "bilgisayar": ("bilgisayar",),
                "yapay_zeka_veri": ("yapay zeka", "veri muhendis"),
                "elektronik_haberlesme": ("elektronik", "haberlesme"),
            }.get(target_canon, (str(target_canon or "").replace("_", " "),))
            if target_canon and any(term and term in folded_user for term in target_terms):
                profile.indecision.target_department = target_canon
                profile.record_provenance(f"target_dept:{target_canon}", 0.90, turn, evidence)
                if target_canon == TARGET_DEPT:
                    profile.indecision.department_certainty = max(
                        profile.indecision.department_certainty, 0.75)

        for alt in d.get("department_alternatives_mentioned", []):
            canon = normalize_department(alt)
            if not canon:
                continue
            if canon == TARGET_DEPT:
                # Bilgisayar masada — alternatif değil; hedef boşsa hedefe yaz
                if profile.indecision.target_department is None:
                    profile.indecision.target_department = TARGET_DEPT
                    profile.record_provenance(f"target_dept:{TARGET_DEPT}", 0.80, turn, evidence)
                continue
            if canon not in profile.indecision.department_alternatives:
                profile.activate_alternative("department", canon, turn)
                profile.indecision.department_alternatives.append(canon)
                profile.record_provenance(f"dept_alt:{canon}", 0.90, turn, evidence)

        # Motivation — EWMA update, 9 boyut. Güçlü sinyal (>=0.6) = orta güven, zayıf = tahmin.
        m = analysis.get("motivation_signals", {})
        for k in MOTIVATION_KEYS:
            new_val = m.get(k)
            if new_val is None or float(new_val) < 0.05:
                continue
            old = profile.indecision.motivation.get(k, 0.0)
            profile.indecision.motivation[k] = 0.7 * old + 0.3 * float(new_val)
            if float(new_val) >= 0.5:
                conf = 0.70 if float(new_val) >= 0.6 else 0.55
                profile.record_provenance(f"motivation:{k}", conf, turn, evidence)

        # Kısıtlar — None olmayanlar profile'a işlenir
        cs = analysis.get("constraint_signals", {})
        constraint_terms = {
            "city_istanbul": ("istanbul",),
            "public_university": ("devlet univers", "ozel univers", "vakif univers"),
            "cost_sensitivity": ("para", "burs", "maddi", "butce", "ucret", "maliyet", "masraf", "gecin"),
            "family_influence": ("aile", "annem", "babam"),
            "english_medium": ("ingilizce", "hazirlik"),
            "abroad_goal": ("yurt dis", "yurtdis", "erasmus"),
            "campus_social": ("sosyal", "arkadas", "kampus", "takilacak"),
        }
        for key in ("city_istanbul", "public_university", "cost_sensitivity",
                    "family_influence", "english_medium", "abroad_goal", "campus_social"):
            val = cs.get(key)
            if val is None or not any(term in folded_user for term in constraint_terms[key]):
                continue
            old = getattr(profile.constraints, key)
            setattr(profile.constraints, key, float(val) if old is None else 0.6 * old + 0.4 * float(val))
            profile.record_provenance(f"constraint:{key}", 0.70, turn, evidence)
        housing_terms = ("yurt", "barin", "kalacak yer", "konakla", "eve cik", "ev kirala")
        if cs.get("housing_needed") is not None and any(term in folded_user for term in housing_terms):
            profile.constraints.housing_needed = bool(cs["housing_needed"])
            profile.record_provenance("constraint:housing_needed", 0.80, turn, evidence)

        strong_offer = any(term in folded_user for term in ("para teklif", "maddi teklif", "burs teklif", "nakit teklif"))
        financial_signal = strong_offer or any(term in folded_user for term in ("burs", "maddi", "butce", "gecinem", "odeyem"))
        if financial_signal:
            strength = 0.90 if strong_offer else 0.75
            profile.indecision.motivation["money"] = max(profile.indecision.motivation.get("money", 0.0), strength)
            current_cost = profile.constraints.cost_sensitivity or 0.0
            profile.constraints.cost_sensitivity = max(current_cost, strength)
            profile.record_provenance("motivation:money", 0.85, turn, evidence)
            profile.record_provenance("constraint:cost_sensitivity", 0.85, turn, evidence)

        # Must-have / deal-breakers — aday açıkça söyledi, yüksek güven
        for mh in analysis.get("must_have_mentioned", []):
            if mh and mh not in profile.indecision.must_have:
                profile.indecision.must_have.append(mh)
                profile.record_provenance(f"must_have:{mh[:30]}", 0.90, turn, evidence)
        for db_item in analysis.get("deal_breakers_mentioned", []):
            if db_item and db_item not in profile.indecision.deal_breakers:
                profile.indecision.deal_breakers.append(db_item)
                profile.record_provenance(f"deal_breaker:{db_item[:30]}", 0.90, turn, evidence)

        # Interests — mention = orta-yüksek güven (tekrar mention provenance'ı otomatik artırır)
        for interest in analysis.get("interests_mentioned", []):
            key = interest.lower().strip()
            if key in profile.interests:
                profile.interests[key] = min(1.0, profile.interests[key] + 0.25)
                profile.record_provenance(f"interest:{key}", 0.75, turn, evidence)

        # Experience
        exp = analysis.get("experience_hints")
        if exp and exp != "unknown":
            profile.experience_level = exp

        # Concerns — kanonik kategorilere normalize + dedup (analyzer serbest metin sızdırırsa savunma)
        for c in analysis.get("concerns_mentioned", []):
            norm = self._normalize_concern(c)
            if norm and norm not in profile.concerns:
                if norm in profile.resolved_concerns:
                    profile.resolved_concerns.remove(norm)
                profile.concerns.append(norm)
                profile.record_provenance(f"concern:{norm}", 0.85, turn, evidence)

        # Explicitly retracted alternatives become inactive. They remain in the
        # event history but stop influencing routing and bandit eligibility.
        retractions = analysis.get("retractions", {}) or {}
        for raw in retractions.get("field_alternatives", []):
            canon = normalize_field(raw)
            if canon:
                profile.retire_alternative("field", canon, turn)
        for raw in retractions.get("university_alternatives", []):
            canon = normalize_university(raw)
            if canon:
                profile.retire_alternative("university", canon, turn)
        for raw in retractions.get("department_alternatives", []):
            canon = normalize_department(raw)
            if canon:
                profile.retire_alternative("department", canon, turn)

        # Defensive fallback for older analyzers/fakes: detect explicit Turkish
        # retraction wording against currently active alternatives.
        self._apply_text_retractions(profile, user_text, turn)

        for raw in analysis.get("concerns_resolved", []):
            norm = self._normalize_concern(raw)
            if not norm:
                continue
            if norm in profile.concerns:
                profile.concerns.remove(norm)
            if norm not in profile.resolved_concerns:
                profile.resolved_concerns.append(norm)
            profile.record_preference_event(turn, "resolved", "concern", norm)

        decision_status = analysis.get("decision_status", "none")
        if decision_status in ("still_deciding", "itu_compe_committed", "other_committed"):
            profile.decision_status = decision_status
            profile.decision_confidence = 0.95 if decision_status.endswith("committed") else 0.65
            profile.record_preference_event(turn, "decision", "status", decision_status)

        # Keep the active shortlist deterministic and current.
        active_alternatives = [
            *profile.indecision.university_alternatives,
            *profile.indecision.department_alternatives,
            *profile.indecision.field_alternatives,
        ]
        profile.indecision.top_alternatives = list(dict.fromkeys(active_alternatives))[:3]

    _CANONICAL_CONCERNS = {
        "math", "difficulty", "family", "cost", "employment",
        "english", "discrimination", "self_efficacy", "uncertainty",
    }
    _CONCERN_SYNONYMS = {
        "matematik": "math", "mathematics": "math",
        "zor": "difficulty", "zorluk": "difficulty", "kalanlar": "difficulty",
        "kalmak": "difficulty", "kaybederim": "difficulty",
        "aile": "family", "ailem": "family", "baba": "family", "anne": "family",
        "aile baskısı": "family", "ailem de üzülür": "family",
        "maddi": "cost", "para": "cost", "burs": "cost", "money": "cost",
        "işsizlik": "employment", "issizlik": "employment", "job_security": "employment",
        "iş bulamama": "employment",
        "ingilizce": "english", "dil": "english",
        "ayrımcılık": "discrimination",
        "özgüven": "self_efficacy", "korku": "self_efficacy", "korkularım": "self_efficacy",
        "kararsızlık": "uncertainty", "belirsizlik": "uncertainty",
    }

    def _normalize_concern(self, raw: str) -> str | None:
        if not raw:
            return None
        c = raw.strip().lower()
        if c in self._CANONICAL_CONCERNS:
            return c
        if c in self._CONCERN_SYNONYMS:
            return self._CONCERN_SYNONYMS[c]
        # Substring eşleme — "matematiğim kötü" gibi serbest metin sızıntıları
        for key, canon in self._CONCERN_SYNONYMS.items():
            if key in c:
                return canon
        # Hiçbir kategoriye oturmuyorsa profili kirletme
        return None

    def _apply_text_retractions(self, profile: CandidateProfile, text: str, turn: int):
        if not text:
            return
        folded = text.lower().translate(str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu"))
        markers = (
            "vazgectim", "dusunmuyorum", "istemiyorum", "eledim",
            "listemden cikardim", "artik secenek degil",
        )
        if not any(marker in folded for marker in markers):
            return

        aliases = {
            "tip": ("tip", "doktorluk"),
            "hukuk": ("hukuk",),
            "koc": ("koc",),
            "odtu": ("odtu",),
            "bogazici": ("bogazici",),
            "bilkent": ("bilkent",),
            "sabanci": ("sabanci",),
            "ytu": ("ytu", "yildiz"),
            "yapay_zeka_veri": ("yapay zeka", "veri muhendisligi"),
            "elektronik_haberlesme": ("elektronik", "haberlesme"),
            "kontrol_otomasyon": ("kontrol", "otomasyon"),
            "yazilim": ("yazilim",),
        }
        active_map = {
            "field": list(profile.indecision.field_alternatives),
            "university": list(profile.indecision.university_alternatives),
            "department": list(profile.indecision.department_alternatives),
        }
        for category, values in active_map.items():
            for value in values:
                if any(alias in folded for alias in aliases.get(value, (value.replace("_", " "),))):
                    profile.retire_alternative(category, value, turn)

    def _compute_engagement(self, analysis: dict, prev: float) -> float:
        intent = analysis.get("intent", "neutral")
        delta = 0.0
        if intent in ("engaged", "seek_info"):
            delta += 0.15
        elif intent == "concern":
            delta += 0.05
        elif intent == "disengaged":
            delta -= 0.20
        elif intent == "reject":
            delta -= 0.05

        length = analysis.get("response_length", 0)
        if length >= 20:
            delta += 0.05
        elif length <= 3:
            delta -= 0.05

        return max(0.0, min(1.0, prev * 0.7 + (0.5 + delta) * 0.3))

    def _compute_trust(self, analysis: dict, prev: float) -> float:
        """Slow-moving trust proxy based on voluntary disclosure and response relevance."""
        target = 0.5
        if analysis.get("new_profile_info"):
            target += 0.12
        if analysis.get("asked_followup"):
            target += 0.08
        relevance = float(analysis.get("response_relevance", 0.5))
        target += (relevance - 0.5) * 0.20
        if analysis.get("intent") == "disengaged":
            target -= 0.15
        return max(0.0, min(1.0, prev * 0.85 + target * 0.15))

    def _build_fsm_context(self, conv: Conversation, profile: CandidateProfile, analysis: dict) -> dict:
        interests_known = sum(1 for v in profile.interests.values() if v > 0.15)
        ind = profile.indecision
        return {
            "turn_count": conv.turn_count,
            "yks_rank": profile.yks_rank,
            "interests_known": interests_known,
            "greeting_done": (conv.turn_count or 0) >= 1,
            "intent": analysis.get("intent", "neutral"),
            "sentiment": analysis.get("sentiment", 0.0),
            "reception_signal": analysis.get("reception_signal", 0.5),
            "wants_detail": analysis.get("wants_detail", False),
            "new_profile_info": analysis.get("new_profile_info", False),
            "has_objection": analysis.get("intent") == "concern" or len(analysis.get("concerns_mentioned", [])) > 0,
            "has_field_alternatives": len(ind.field_alternatives) > 0,
            "has_univ_alternatives": len(ind.university_alternatives) > 0,
            "has_dept_alternatives": len(ind.department_alternatives) > 0,
            "has_dominant_motivation": ind.dominant_motivation() != "unknown",
            # FSM'e YALNIZCA bu turnki karar sinyali gider — profildeki yapışkan decision_status
            # her turnu S8'e çekip ping-pong yaratıyordu (sess_1329). Aday "İTÜ birinci tercihim"
            # dediği turn özeti alır; sonraki soruları normal akıştan cevaplanır.
            "decision_status": analysis.get("decision_status", "none"),
            "asked_followup": analysis.get("asked_followup", False),
            "fallback_needed": False,
        }

    def _decision_stage(self, state: FSMState) -> str:
        """FSM state → karar aşaması (tek doğruluk kaynağı FSM'dir)."""
        if state in (FSMState.S0_FALLBACK, FSMState.S1_GREETING,
                     FSMState.S2_INDECISION_PROBE, FSMState.S2R_PROFILE_UPDATE):
            return "kesif"
        if state == FSMState.S7_CONCERN_HANDLING:
            return "itiraz"
        if state in (FSMState.S8_IDEAL_MATCH_SUMMARY, FSMState.S9_CLOSING):
            return "kapanis"
        return "kiyaslama"

    _CONSTRAINT_TR = {
        "city_istanbul": "İstanbul isteği",
        "public_university": "devlet üniv. tercihi",
        "cost_sensitivity": "maliyet hassasiyeti",
        "housing_needed": "yurt ihtiyacı",
        "family_influence": "aile etkisi",
        "english_medium": "İngilizce eğitim isteği",
        "abroad_goal": "yurt dışı hedefi",
        "campus_social": "sosyal kampüs beklentisi",
    }

    def _profile_summary(self, profile: CandidateProfile) -> str:
        from .profile.academic import academic_fit_summary
        lines = []
        if profile.display_name:
            lines.append(f"İsim: {profile.display_name} (hitap ederken adını kullan, ama her cümlede değil)")

        # Akademik uygunluk — deterministik hesap (risk bandı + erişilebilir bölümler)
        lines.append(f"AKADEMİK DURUM: {academic_fit_summary(profile.yks_rank, profile.yks_rank_type)}")
        if profile.yks_rank is None:
            lines.append("YKS sıralaması: HENÜZ BİLİNMİYOR (öncelikle nazikçe sor).")
        else:
            # Adayın masasındaki bölümler için AYRI bandlar — "bilgisayar hard" diye
            # adayın gerçek hedefini karartma; elektronik güvenliyse onu söyle
            from .profile.academic import risk_bands_for
            table = ["bilgisayar"]
            if profile.indecision.target_department:
                table.append(profile.indecision.target_department)
            table.extend(profile.indecision.department_alternatives)
            bands = risk_bands_for(profile.yks_rank, table)
            if len(bands) > 1:
                band_tr = {"safe": "güvenli", "borderline": "sınırda", "hard": "geride", "unknown": "taban bilinmiyor"}
                parts = [f"{b['department']}={band_tr[b['band']]}" for b in bands]
                lines.append(f"MASADAKİ BÖLÜMLERİN DURUMU: {', '.join(parts)}")
        if profile.indecision.target_department:
            lines.append(f"ADAYIN HEDEF BÖLÜMÜ: {profile.indecision.target_department}")

        ind = profile.indecision
        # Okunur ana-kararsızlık cümlesi — LLM'in bunu tek bakışta anlaması için
        main_axis = ind.main_indecision_axis()
        axis_tr = {"field": "ALAN (mühendislik mi, başka alan mı)",
                   "university": "ÜNİVERSİTE (İTÜ mü, başka üniversite mi)",
                   "department": "BÖLÜM (Bilgisayar mı, başka bölüm mü)"}[main_axis]
        alts = {"field": ind.field_alternatives,
                "university": ind.university_alternatives,
                "department": ind.department_alternatives}[main_axis]
        alt_str = f" — masadaki alternatif: {', '.join(alts)}" if alts else ""
        lines.append(f"ANA KARARSIZLIK: {axis_tr}{alt_str}")
        lines.append(f"GENEL KARARSIZLIK SKORU: {ind.overall_indecision():.2f}")
        if ind.top_alternatives:
            lines.append(f"AKTİF KISA LİSTE: {', '.join(ind.top_alternatives)}")

        if ind.field_alternatives:
            lines.append(f"Alan alternatifleri: {', '.join(ind.field_alternatives)}")
        if ind.university_alternatives:
            lines.append(f"Üniversite alternatifleri: {', '.join(ind.university_alternatives)}")
        if ind.department_alternatives:
            lines.append(f"Bölüm alternatifleri: {', '.join(ind.department_alternatives)}")

        dom = ind.dominant_motivation()
        if dom != "unknown":
            lines.append(f"Dominant motivasyon: {dom}")

        lines.append(f"Karar aşaması: {ind.decision_stage}")

        # Kısıtlar — sadece bilinenler
        known = profile.constraints.known_items()
        if known:
            parts = []
            for k, v in known.items():
                label = self._CONSTRAINT_TR.get(k, k)
                if isinstance(v, bool):
                    parts.append(f"{label}: {'evet' if v else 'hayır'}")
                else:
                    parts.append(f"{label}: {v:.1f}")
            lines.append(f"Tercih kısıtları: {', '.join(parts)}")

        if ind.must_have:
            lines.append(f"OLMAZSA OLMAZLAR: {', '.join(ind.must_have)}")
        if ind.deal_breakers:
            lines.append(f"İSTEMEDİKLERİ: {', '.join(ind.deal_breakers)} (bunlara karşı argüman üretme, saygı göster)")

        top_interests = sorted(profile.interests.items(), key=lambda kv: kv[1], reverse=True)[:3]
        top_interests = [f"{k}({v:.2f})" for k, v in top_interests if v > 0.15]
        if top_interests:
            lines.append(f"İlgi alanları: {', '.join(top_interests)}")

        if profile.concerns:
            lines.append(f"Kaygılar: {', '.join(profile.concerns)}")
        if profile.resolved_concerns:
            lines.append(f"ÇÖZÜLMÜŞ KAYGILAR: {', '.join(profile.resolved_concerns)} (yeniden sorunmuş gibi açma)")
        if profile.covered_topics:
            lines.append(f"KONUŞULAN KONULAR: {', '.join(profile.covered_topics[-8:])}")
        if profile.decision_status != "none":
            lines.append(f"KARAR DURUMU: {profile.decision_status} ({profile.decision_confidence:.2f})")

        # KESİN vs TAHMİN ayrımı — LLM'in tahminleri gerçek gibi kullanmaması için
        facts = profile.confident_facts()
        guesses = profile.uncertain_guesses()
        if facts:
            lines.append(f"KESİN BİLİNENLER (aday söyledi): {', '.join(facts[:10])}")
        if guesses:
            lines.append(f"TAHMİNLER (çıkarım — temkinli kullan, gerekirse teyit et): {', '.join(guesses[:6])}")

        lines.append(f"Engagement: {profile.engagement_level:.2f}, Trust: {profile.trust_level:.2f}")

        return "\n".join(lines)

    def _forced_selection(self, argument_id: str, reasoning: str = "forced selection", score: float = 1.0):
        from .strategy.bandit import SelectionResult
        return SelectionResult(
            argument_id=argument_id,
            score=score,
            exploration_bonus=0.0,
            reasoning=reasoning,
            alternatives=[],
        )
