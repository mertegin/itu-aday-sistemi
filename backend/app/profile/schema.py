from dataclasses import dataclass, field
from enum import Enum


class MotivationType(str, Enum):
    UNKNOWN = "unknown"
    MONEY = "money"
    SCIENCE = "science"
    PRESTIGE = "prestige"
    INTEREST = "interest"
    FAMILY = "family"
    SOCIAL_IMPACT = "social_impact"
    ENTREPRENEURSHIP = "entrepreneurship"
    ABROAD = "abroad"
    JOB_SECURITY = "job_security"
    UNCERTAIN = "uncertain"


MOTIVATION_KEYS = [
    "money", "science", "prestige", "interest", "family",
    "social_impact", "entrepreneurship", "abroad", "job_security",
]


def _default_motivation() -> dict[str, float]:
    return {k: 0.0 for k in MOTIVATION_KEYS}


def _default_inactive_alternatives() -> dict[str, list[str]]:
    return {"field": [], "university": [], "department": []}


@dataclass
class PreferenceConstraints:
    """Tercih kısıtları — aday sadece 'ilgi' ile karar vermiyor.

    None = henüz bilinmiyor (0.5 'kararsız'dan farklı; UI'da '?' gösterilir).
    float alanlar 0-1: 0 = istemiyor/önemsiz, 1 = kesin istiyor/çok önemli.
    """
    city_istanbul: float | None = None        # İstanbul'da okumak istiyor mu
    public_university: float | None = None    # devlet üniversitesi tercihi
    cost_sensitivity: float | None = None     # burs/maliyet hassasiyeti
    housing_needed: bool | None = None        # yurt/barınma ihtiyacı
    family_influence: float | None = None     # aile etkisinin gücü
    english_medium: float | None = None       # İngilizce eğitim isteği
    abroad_goal: float | None = None          # yurt dışı hedefi (okuma/çalışma)
    campus_social: float | None = None        # kampüs/sosyal ortam beklentisi

    def to_dict(self) -> dict:
        return {
            "city_istanbul": self.city_istanbul,
            "public_university": self.public_university,
            "cost_sensitivity": self.cost_sensitivity,
            "housing_needed": self.housing_needed,
            "family_influence": self.family_influence,
            "english_medium": self.english_medium,
            "abroad_goal": self.abroad_goal,
            "campus_social": self.campus_social,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PreferenceConstraints":
        c = cls()
        if not d:
            return c
        for k in c.to_dict():
            if k in d:
                setattr(c, k, d[k])
        return c

    def known_items(self) -> dict:
        """Sadece bilinen (None olmayan) kısıtlar."""
        return {k: v for k, v in self.to_dict().items() if v is not None}


@dataclass
class IndecisionMatrix:
    """Kararsızlık — 3 eksende netlik + motivasyon dağılımı + karar bağlamı."""
    field_certainty: float = 0.5           # 0 = başka alan / 1 = mühendislik kesin
    university_certainty: float = 0.5      # 0 = başka üniv / 1 = İTÜ kesin
    department_certainty: float = 0.5      # 0 = başka bölüm / 1 = Bilg. kesin

    field_alternatives: list[str] = field(default_factory=list)
    university_alternatives: list[str] = field(default_factory=list)
    department_alternatives: list[str] = field(default_factory=list)

    motivation: dict[str, float] = field(default_factory=_default_motivation)

    # Karar bağlamı
    decision_stage: str = "kesif"          # kesif | kiyaslama | itiraz | kapanis (FSM'den türetilir)
    target_department: str | None = None   # adayın AÇIKÇA hedeflediği bölüm (canonical slug; null = belirsiz)
    top_alternatives: list[str] = field(default_factory=list)   # adayın GERÇEKTEN masasındaki 2-3 seçenek
    must_have: list[str] = field(default_factory=list)          # olmazsa olmazlar
    deal_breakers: list[str] = field(default_factory=list)      # kesinlikle istemedikleri

    def overall_indecision(self) -> float:
        return 1.0 - min(self.field_certainty, self.university_certainty, self.department_certainty)

    def dominant_motivation(self) -> str:
        if not self.motivation or max(self.motivation.values(), default=0.0) < 0.15:
            return "unknown"
        return max(self.motivation.items(), key=lambda kv: kv[1])[0]

    def main_indecision_axis(self) -> str:
        active_axes: list[tuple[str, float]] = []
        if self.university_alternatives:
            active_axes.append(("university", self.university_certainty))
        if self.department_alternatives:
            active_axes.append(("department", self.department_certainty))
        if self.field_alternatives:
            active_axes.append(("field", self.field_certainty))
        if active_axes:
            return min(active_axes, key=lambda item: item[1])[0]
        axes = {
            "field": self.field_certainty,
            "university": self.university_certainty,
            "department": self.department_certainty,
        }
        return min(axes.items(), key=lambda kv: kv[1])[0]

    def top_alternative(self) -> str | None:
        if self.top_alternatives:
            return self.top_alternatives[0]
        for lst in (self.university_alternatives, self.department_alternatives, self.field_alternatives):
            if lst:
                return lst[0]
        return None


@dataclass
class CandidateProfile:
    """Aday'ın konuşma boyunca birikmiş profili.

    Provenance katmanı: her önemli alan için `provenance[alan]` =
    {confidence, source_turn, updated_turn, evidence}. confidence >= 0.75 → "kesin"
    (aday açıkça söyledi), altı → "tahmin" (LLM çıkarımı). Prompt özetinde ayrılır.
    """
    display_name: str | None = None

    # Akademik uygunluk
    yks_rank: int | None = None
    yks_rank_type: str = "unknown"    # "actual" | "practice" | "target" | "unknown"

    # Kararsızlık + kısıtlar
    indecision: IndecisionMatrix = field(default_factory=IndecisionMatrix)
    constraints: PreferenceConstraints = field(default_factory=PreferenceConstraints)

    # İlgi alanları — 0-1 skorlar
    interests: dict[str, float] = field(default_factory=lambda: {
        "ai": 0.0, "software": 0.0, "hardware": 0.0,
        "cybersec": 0.0, "gamedev": 0.0, "robotics": 0.0,
        "aerospace": 0.0, "entrepreneurship": 0.0,
        "research": 0.0, "abroad": 0.0,
    })

    experience_level: str = "unknown"
    concerns: list[str] = field(default_factory=list)

    # Meta-signaller
    engagement_level: float = 0.5
    trust_level: float = 0.5
    reception_signal: float = 0.5

    # Session state
    covered_topics: list[str] = field(default_factory=list)
    revealed_arguments: list[str] = field(default_factory=list)

    # Dynamic preference memory: removed items are remembered but no longer
    # influence routing/argument eligibility.
    inactive_alternatives: dict[str, list[str]] = field(default_factory=_default_inactive_alternatives)
    resolved_concerns: list[str] = field(default_factory=list)
    decision_status: str = "none"
    decision_confidence: float = 0.0
    preference_events: list[dict] = field(default_factory=list)

    # Provenance: alan adı -> {confidence, source_turn, updated_turn, evidence}
    provenance: dict[str, dict] = field(default_factory=dict)

    # ---- Provenance yardımcıları ----

    def record_provenance(self, key: str, confidence: float, turn: int, evidence: str = ""):
        entry = self.provenance.get(key)
        if entry is None:
            self.provenance[key] = {
                "confidence": round(confidence, 2),
                "source_turn": turn,
                "updated_turn": turn,
                "evidence": evidence[:120],
            }
        else:
            # Tekrarlanan sinyal güveni artırır (tavan 0.98)
            entry["confidence"] = round(min(0.98, max(entry["confidence"], confidence) + 0.05), 2)
            entry["updated_turn"] = turn
            if evidence:
                entry["evidence"] = evidence[:120]

    def confident_facts(self, threshold: float = 0.75) -> list[str]:
        return [k for k, v in self.provenance.items() if v.get("confidence", 0) >= threshold]

    def uncertain_guesses(self, threshold: float = 0.75) -> list[str]:
        return [k for k, v in self.provenance.items() if v.get("confidence", 0) < threshold]

    def record_preference_event(self, turn: int, event: str, category: str, value: str):
        self.preference_events.append({
            "turn": turn,
            "event": event,
            "category": category,
            "value": value,
        })
        if len(self.preference_events) > 30:
            self.preference_events = self.preference_events[-30:]

    def retire_alternative(self, category: str, value: str, turn: int):
        active_map = {
            "field": self.indecision.field_alternatives,
            "university": self.indecision.university_alternatives,
            "department": self.indecision.department_alternatives,
        }
        active = active_map.get(category)
        if active is None:
            return
        if value in active:
            active.remove(value)
        inactive = self.inactive_alternatives.setdefault(category, [])
        if value not in inactive:
            inactive.append(value)
        self.record_preference_event(turn, "retracted", category, value)

    def activate_alternative(self, category: str, value: str, turn: int):
        inactive = self.inactive_alternatives.setdefault(category, [])
        if value in inactive:
            inactive.remove(value)
            self.record_preference_event(turn, "reactivated", category, value)

    # ---- Akademik uygunluk (deterministik, profile/academic.py kullanır) ----

    def rank_confidence(self) -> float:
        return {"actual": 0.95, "practice": 0.70, "target": 0.50}.get(self.yks_rank_type, 0.0)

    def to_dict(self) -> dict:
        return {
            "display_name": self.display_name,
            "yks_rank": self.yks_rank,
            "yks_rank_type": self.yks_rank_type,
            "indecision": {
                "field_certainty": self.indecision.field_certainty,
                "university_certainty": self.indecision.university_certainty,
                "department_certainty": self.indecision.department_certainty,
                "field_alternatives": self.indecision.field_alternatives,
                "university_alternatives": self.indecision.university_alternatives,
                "department_alternatives": self.indecision.department_alternatives,
                "motivation": self.indecision.motivation,
                "decision_stage": self.indecision.decision_stage,
                "target_department": self.indecision.target_department,
                "top_alternatives": self.indecision.top_alternatives,
                "must_have": self.indecision.must_have,
                "deal_breakers": self.indecision.deal_breakers,
            },
            "constraints": self.constraints.to_dict(),
            "interests": self.interests,
            "experience_level": self.experience_level,
            "concerns": self.concerns,
            "engagement_level": self.engagement_level,
            "trust_level": self.trust_level,
            "reception_signal": self.reception_signal,
            "covered_topics": self.covered_topics,
            "revealed_arguments": self.revealed_arguments,
            "inactive_alternatives": self.inactive_alternatives,
            "resolved_concerns": self.resolved_concerns,
            "decision_status": self.decision_status,
            "decision_confidence": self.decision_confidence,
            "preference_events": self.preference_events,
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CandidateProfile":
        p = cls()
        if not d:
            return p
        p.display_name = d.get("display_name")
        p.yks_rank = d.get("yks_rank")
        p.yks_rank_type = d.get("yks_rank_type", "unknown")
        ind = d.get("indecision", {})
        if ind:
            motivation = _default_motivation()
            motivation.update(ind.get("motivation", {}))
            p.indecision = IndecisionMatrix(
                field_certainty=ind.get("field_certainty", 0.5),
                university_certainty=ind.get("university_certainty", 0.5),
                department_certainty=ind.get("department_certainty", 0.5),
                field_alternatives=ind.get("field_alternatives", []),
                university_alternatives=ind.get("university_alternatives", []),
                department_alternatives=ind.get("department_alternatives", []),
                motivation=motivation,
                decision_stage=ind.get("decision_stage", "kesif"),
                target_department=ind.get("target_department"),
                top_alternatives=ind.get("top_alternatives", []),
                must_have=ind.get("must_have", []),
                deal_breakers=ind.get("deal_breakers", []),
            )
        p.constraints = PreferenceConstraints.from_dict(d.get("constraints", {}))
        p.interests = d.get("interests", p.interests)
        p.experience_level = d.get("experience_level", "unknown")
        p.concerns = d.get("concerns", [])
        p.engagement_level = d.get("engagement_level", 0.5)
        p.trust_level = d.get("trust_level", 0.5)
        p.reception_signal = d.get("reception_signal", 0.5)
        p.covered_topics = d.get("covered_topics", [])
        p.revealed_arguments = d.get("revealed_arguments", [])
        inactive = _default_inactive_alternatives()
        inactive.update(d.get("inactive_alternatives", {}))
        p.inactive_alternatives = inactive
        p.resolved_concerns = d.get("resolved_concerns", [])
        p.decision_status = d.get("decision_status", "none")
        p.decision_confidence = float(d.get("decision_confidence", 0.0))
        p.preference_events = d.get("preference_events", [])
        p.provenance = d.get("provenance", {})
        return p
