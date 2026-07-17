"""LLM analyzer çıktısı için Pydantic şeması.

Bozuk JSON, eksik alan, yanlış tip → ValidationError → client güvenli fallback'e düşer.
Tüm sayısal alanlar validator'larla [0,1] (sentiment [-1,1]) aralığına sıkıştırılır.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Literal


def _clamp01(v: float | None) -> float | None:
    if v is None:
        return None
    return max(0.0, min(1.0, float(v)))


class FieldSignals(BaseModel):
    engineering_certain: float | None = None
    field_alternatives_mentioned: list[str] = Field(default_factory=list)

    @field_validator("engineering_certain")
    @classmethod
    def clamp(cls, v):
        return _clamp01(v)


class UniversitySignals(BaseModel):
    itu_certain: float | None = None
    university_alternatives_mentioned: list[str] = Field(default_factory=list)

    @field_validator("itu_certain")
    @classmethod
    def clamp(cls, v):
        return _clamp01(v)


class DepartmentSignals(BaseModel):
    compe_certain: float | None = None
    target_department_mentioned: str | None = None  # adayın AÇIKÇA hedeflediğini söylediği bölüm
    department_alternatives_mentioned: list[str] = Field(default_factory=list)

    @field_validator("compe_certain")
    @classmethod
    def clamp(cls, v):
        return _clamp01(v)


class MotivationSignals(BaseModel):
    money: float = 0.0
    science: float = 0.0
    prestige: float = 0.0
    interest: float = 0.0
    family: float = 0.0
    social_impact: float = 0.0
    entrepreneurship: float = 0.0
    abroad: float = 0.0
    job_security: float = 0.0

    @field_validator("money", "science", "prestige", "interest", "family",
                     "social_impact", "entrepreneurship", "abroad", "job_security")
    @classmethod
    def clamp(cls, v):
        return _clamp01(v) or 0.0


class ConstraintSignals(BaseModel):
    """Tercih kısıtı sinyalleri — None = bu mesajda sinyal yok."""
    city_istanbul: float | None = None
    public_university: float | None = None
    cost_sensitivity: float | None = None
    housing_needed: bool | None = None
    family_influence: float | None = None
    english_medium: float | None = None
    abroad_goal: float | None = None
    campus_social: float | None = None

    @field_validator("city_istanbul", "public_university", "cost_sensitivity",
                     "family_influence", "english_medium", "abroad_goal", "campus_social")
    @classmethod
    def clamp(cls, v):
        return _clamp01(v)


class RetractionSignals(BaseModel):
    """Adayın artık değerlendirmediğini açıkça söylediği seçenekler."""
    field_alternatives: list[str] = Field(default_factory=list)
    university_alternatives: list[str] = Field(default_factory=list)
    department_alternatives: list[str] = Field(default_factory=list)


class MessageAnalysis(BaseModel):
    """Analyzer LLM'inin döndürmesi gereken tam şema."""
    intent: Literal[
        "greeting", "engaged", "seek_info", "concern",
        "reject", "close", "disengaged", "neutral",
    ] = "neutral"
    sentiment: float = 0.0
    asked_followup: bool = False
    response_length: int = 0

    yks_rank_mentioned: int | None = None
    yks_rank_type: Literal["actual", "target", "practice"] | None = None
    display_name_mentioned: str | None = None

    field_signals: FieldSignals = Field(default_factory=FieldSignals)
    university_signals: UniversitySignals = Field(default_factory=UniversitySignals)
    department_signals: DepartmentSignals = Field(default_factory=DepartmentSignals)
    motivation_signals: MotivationSignals = Field(default_factory=MotivationSignals)
    constraint_signals: ConstraintSignals = Field(default_factory=ConstraintSignals)

    interests_mentioned: list[str] = Field(default_factory=list)
    experience_hints: Literal["none", "hobby", "competition", "project", "unknown"] = "unknown"
    concerns_mentioned: list[str] = Field(default_factory=list)
    must_have_mentioned: list[str] = Field(default_factory=list)
    deal_breakers_mentioned: list[str] = Field(default_factory=list)
    retractions: RetractionSignals = Field(default_factory=RetractionSignals)
    concerns_resolved: list[str] = Field(default_factory=list)
    decision_status: Literal[
        "none", "still_deciding", "itu_compe_committed", "other_committed",
    ] = "none"

    new_profile_info: bool = False
    wants_detail: bool = False
    reception_signal: float = 0.5
    response_relevance: float = 0.5
    argument_reaction: Literal[
        "accepted", "curious", "neutral", "objection",
        "rejected", "topic_shift", "not_applicable",
    ] = "not_applicable"
    conversation_language: Literal["tr", "en"] = "tr"

    @field_validator("sentiment")
    @classmethod
    def clamp_sentiment(cls, v):
        return max(-1.0, min(1.0, float(v)))

    @field_validator("reception_signal", "response_relevance")
    @classmethod
    def clamp_reception(cls, v):
        return max(0.0, min(1.0, float(v)))

    @field_validator("response_length")
    @classmethod
    def non_negative(cls, v):
        return max(0, int(v))

    @field_validator("yks_rank_mentioned")
    @classmethod
    def sane_rank(cls, v):
        if v is None:
            return None
        v = int(v)
        # YKS SAY sıralaması 1 - 3.000.000 aralığında anlamlı
        if v < 1 or v > 3_000_000:
            return None
        return v

    @field_validator("display_name_mentioned")
    @classmethod
    def clean_name(cls, v):
        if not v:
            return None
        v = str(v).strip()
        # Aşırı uzun / cümle gibi şeyleri reddet
        if len(v) > 40 or len(v.split()) > 3:
            return None
        return v.title()

    def to_orchestrator_dict(self) -> dict:
        """Orchestrator'ın beklediği düz dict format."""
        return {
            "intent": self.intent,
            "sentiment": self.sentiment,
            "asked_followup": self.asked_followup,
            "response_length": self.response_length,
            "yks_rank_mentioned": self.yks_rank_mentioned,
            "yks_rank_type": self.yks_rank_type,
            "display_name_mentioned": self.display_name_mentioned,
            "field_signals": self.field_signals.model_dump(),
            "university_signals": self.university_signals.model_dump(),
            "department_signals": self.department_signals.model_dump(),
            "motivation_signals": self.motivation_signals.model_dump(),
            "constraint_signals": self.constraint_signals.model_dump(),
            "interests_mentioned": self.interests_mentioned,
            "experience_hints": self.experience_hints,
            "concerns_mentioned": self.concerns_mentioned,
            "must_have_mentioned": self.must_have_mentioned,
            "deal_breakers_mentioned": self.deal_breakers_mentioned,
            "retractions": self.retractions.model_dump(),
            "concerns_resolved": self.concerns_resolved,
            "decision_status": self.decision_status,
            "new_profile_info": self.new_profile_info,
            "wants_detail": self.wants_detail,
            "reception_signal": self.reception_signal,
            "response_relevance": self.response_relevance,
            "argument_reaction": self.argument_reaction,
            "conversation_language": self.conversation_language,
        }
