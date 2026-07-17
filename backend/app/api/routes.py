import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.db import Conversation, Message, StrategyLog
from ..orchestrator import Orchestrator

router = APIRouter()

_orchestrator = Orchestrator()


class ChatRequest(BaseModel):
    session_id: str | None = Field(default=None, description="Session ID; if omitted, a new one is created")
    text: str


class ChatResponse(BaseModel):
    session_id: str
    response_text: str
    xai_meta: dict
    profile: dict
    academic: dict = {}
    fsm_state: str
    turn_count: int
    reward_previous_turn: float | None
    reward_breakdown_previous_turn: dict | None = None
    ethics_check: dict
    voice_check: dict = {}
    fact_gate: dict = {}
    admission_check: dict = {}
    answer_relevance: dict = {}
    repetition_check: dict = {}
    followup_check: dict = {}
    evidence_check: dict = {}
    generation_fallback: dict = {}
    response_pipeline: dict = {}
    speech_check: dict = {}
    rag: dict = {}
    analysis: dict


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text.")
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:12]}"
    result = await _orchestrator.handle_turn(session_id, req.text.strip(), db)
    return result


@router.post("/session/new")
async def new_session():
    return {"session_id": f"sess_{uuid.uuid4().hex[:12]}"}


@router.get("/sessions")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    """Tüm konuşmaların listesi — geçmiş sohbetler sayfası için."""
    result = await db.execute(select(Conversation).order_by(Conversation.id.desc()))
    convs = result.scalars().all()

    out = []
    for c in convs:
        # Son kullanıcı mesajını önizleme olarak al
        msg_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == c.id, Message.role == "user")
            .order_by(Message.id.desc())
            .limit(1)
        )
        last_msg = msg_result.scalar_one_or_none()
        profile = c.profile or {}
        out.append({
            "session_id": c.session_id,
            "display_name": c.display_name or profile.get("display_name"),
            "yks_rank": profile.get("yks_rank"),
            "fsm_state": c.fsm_state,
            "turn_count": c.turn_count,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "last_user_message": (last_msg.text[:80] + "…") if last_msg and len(last_msg.text) > 80 else (last_msg.text if last_msg else ""),
        })
    return {"sessions": out, "total": len(out)}


@router.get("/session/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.session_id == session_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Session not found")

    msgs_result = await db.execute(
        select(Message).where(Message.conversation_id == conv.id).order_by(Message.id.asc())
    )
    messages = [
        {"role": m.role, "text": m.text, "created_at": m.created_at.isoformat()}
        for m in msgs_result.scalars().all()
    ]

    logs_result = await db.execute(
        select(StrategyLog).where(StrategyLog.conversation_id == conv.id).order_by(StrategyLog.turn.asc())
    )
    logs = [
        {
            "turn": s.turn,
            "fsm_from": s.fsm_from,
            "fsm_to": s.fsm_to,
            "fsm_trigger": s.fsm_trigger,
            "argument_id": s.argument_id,
            "reward": s.reward,
            "xai_reason": s.xai_reason,
            "decision_factors": s.decision_factors,
        }
        for s in logs_result.scalars().all()
    ]

    return {
        "session_id": conv.session_id,
        "display_name": conv.display_name,
        "fsm_state": conv.fsm_state,
        "turn_count": conv.turn_count,
        "profile": conv.profile,
        "context": {k: v for k, v in (conv.context or {}).items() if k != "bandit_stats"},
        "bandit_stats": (conv.context or {}).get("bandit_stats", {}),
        "messages": messages,
        "strategy_logs": logs,
    }


@router.delete("/session/{session_id}")
async def reset_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Conversation).where(Conversation.session_id == session_id))
    conv = result.scalar_one_or_none()
    if conv:
        await db.delete(conv)
        await db.commit()
    return {"deleted": True, "session_id": session_id}


@router.get("/health")
async def health():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}


@router.get("/bandit/stats")
async def bandit_stats(db: AsyncSession = Depends(get_db)):
    """Argüman bazında seçim sayısı, ortalama reward ve user_type kırılımı.

    Kaynak: strategy_logs (tüm session'lar). Reward, argümanın SEÇİLDİĞİ turnda değil,
    bir SONRAKİ turnda hesaplandığı için log'daki reward alanı 'önceki argümanın ödülü'dür —
    burada argümanın kendi ödülüne geri eşliyoruz.
    """
    result = await db.execute(select(StrategyLog).order_by(StrategyLog.conversation_id, StrategyLog.turn))
    logs = list(result.scalars().all())

    stats: dict[str, dict] = {}
    prev_by_conv: dict[int, StrategyLog] = {}
    for log in logs:
        entry = stats.setdefault(log.argument_id or "unknown", {
            "selected_count": 0,
            "reward_sum": 0.0,
            "reward_count": 0,
            "by_user_type": {},
        })
        entry["selected_count"] += 1
        ut = (log.decision_factors or {}).get("user_type", "unknown")
        ut_entry = entry["by_user_type"].setdefault(ut, {"count": 0, "reward_sum": 0.0, "reward_count": 0})
        ut_entry["count"] += 1

        # Bu logdaki reward → aynı conversation'daki BİR ÖNCEKİ turnun argümanına ait
        prev = prev_by_conv.get(log.conversation_id)
        if prev is not None and log.reward is not None and prev.argument_id:
            prev_entry = stats.setdefault(prev.argument_id, {
                "selected_count": 0, "reward_sum": 0.0, "reward_count": 0, "by_user_type": {},
            })
            prev_entry["reward_sum"] += log.reward
            prev_entry["reward_count"] += 1
            prev_ut = (prev.decision_factors or {}).get("user_type", "unknown")
            prev_ut_entry = prev_entry["by_user_type"].setdefault(prev_ut, {"count": 0, "reward_sum": 0.0, "reward_count": 0})
            prev_ut_entry["reward_sum"] += log.reward
            prev_ut_entry["reward_count"] += 1
        prev_by_conv[log.conversation_id] = log

    # Ortalama hesapla, çıktıyı düzleştir
    out = []
    for arg_id, e in stats.items():
        by_ut = {
            ut: {
                "count": v["count"],
                "avg_reward": round(v["reward_sum"] / v["reward_count"], 3) if v["reward_count"] else None,
            }
            for ut, v in e["by_user_type"].items()
        }
        out.append({
            "argument_id": arg_id,
            "selected_count": e["selected_count"],
            "avg_reward": round(e["reward_sum"] / e["reward_count"], 3) if e["reward_count"] else None,
            "reward_samples": e["reward_count"],
            "by_user_type": by_ut,
        })
    out.sort(key=lambda x: x["selected_count"], reverse=True)
    return {"arguments": out, "total_turns": len(logs)}


@router.get("/fsm")
async def fsm_definition():
    """FSM state'leri + transition table'ı diagram için JSON olarak döner."""
    from ..fsm.states import FSMState
    from ..fsm.machine import TRANSITION_TABLE

    states = [s.value for s in FSMState]

    transitions = []
    for from_state, rows in TRANSITION_TABLE.items():
        for pred, to_state, trigger, weight in rows:
            transitions.append({
                "from": from_state.value,
                "to": to_state.value,
                "trigger": trigger,
                "weight": weight,
                "predicate": pred.__name__.lstrip("_"),
            })

    return {"states": states, "transitions": transitions}


@router.get("/fsm/session/{session_id}")
async def fsm_session_path(session_id: str, db: AsyncSession = Depends(get_db)):
    """Bir session'ın FSM geçiş geçmişini döner (diyagramda highlight için)."""
    result = await db.execute(select(Conversation).where(Conversation.session_id == session_id))
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Session not found")

    logs_result = await db.execute(
        select(StrategyLog).where(StrategyLog.conversation_id == conv.id).order_by(StrategyLog.turn.asc())
    )
    path = [
        {"turn": s.turn, "from": s.fsm_from, "to": s.fsm_to, "trigger": s.fsm_trigger, "argument": s.argument_id}
        for s in logs_result.scalars().all()
    ]
    return {"session_id": session_id, "current_state": conv.fsm_state, "path": path}
