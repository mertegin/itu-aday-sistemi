from datetime import datetime
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    fsm_state: Mapped[str] = mapped_column(String(32), default="S1_GREETING")
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    profile: Mapped[dict] = mapped_column(JSON, default=dict)
    turn_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    strategy_logs: Mapped[list["StrategyLog"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str] = mapped_column(String(16))  # "user" | "assistant"
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class StrategyLog(Base):
    __tablename__ = "strategy_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    turn: Mapped[int] = mapped_column(Integer)
    fsm_from: Mapped[str] = mapped_column(String(32))
    fsm_to: Mapped[str] = mapped_column(String(32))
    fsm_trigger: Mapped[str] = mapped_column(String(64))
    argument_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reward: Mapped[float | None] = mapped_column(nullable=True)
    xai_reason: Mapped[str] = mapped_column(Text, default="")
    decision_factors: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="strategy_logs")
