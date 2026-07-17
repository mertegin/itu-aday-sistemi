"""Non-destructive response review for the evidence-grounded writer pipeline."""
from dataclasses import dataclass, field
import re

from .evidence_gate import enforce_evidence_contract
from .fact_gate import (
    check_fact_gate,
    enforce_admission_reality,
    enforce_answer_relevance,
    enforce_non_repetition,
    enforce_scholarship_eligibility,
)
from .retriever import RagResult


@dataclass
class ResponseReview:
    clean: bool
    corrections: list[str] = field(default_factory=list)
    checks: dict = field(default_factory=dict)
    fallbacks: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "clean": self.clean,
            "corrections": self.corrections,
            "checks": self.checks,
        }


def review_response(
    text: str,
    *,
    question: str,
    rag: RagResult,
    argument_id: str,
    rank: int | None,
    history: list[dict],
) -> ResponseReview:
    """Inspect a draft and return rewrite notes without changing its wording."""
    corrections: list[str] = []
    fallbacks: dict = {}

    fact = check_fact_gate(text, rag).to_dict()
    if not fact["clean"]:
        claims = ", ".join(
            f"{item['category']}: {item['claim']}" for item in fact["violations"][:5]
        )
        corrections.append(f"Kanıt paketinde desteklenmeyen iddiaları çıkar veya düzelt: {claims}.")

    relevance_text, relevance = enforce_answer_relevance(text, rag, question)
    if relevance.get("repaired"):
        corrections.append(
            f"Adayın güncel sorusuna doğrudan odaklan; öncelikli kanıt {relevance.get('card_id')} kartındadır."
        )
        fallbacks["relevance"] = relevance_text

    evidence_text, evidence = enforce_evidence_contract(text, rag, argument_id)
    evidence_issue = bool(evidence.get("repaired") or not evidence.get("clean", True))
    if evidence_issue:
        missing = ", ".join(evidence.get("missing") or ["somut kanıt"])
        examples = ", ".join((evidence.get("available_examples") or [])[:5])
        note = f"Cevapta eksik kanıt türleri: {missing}."
        if examples:
            note += f" Kullanılabilecek somut örnekler: {examples}."
        corrections.append(note)
        if evidence.get("repaired"):
            fallbacks["evidence"] = evidence_text

    scholarship_text, scholarship = enforce_scholarship_eligibility(text, rag, question)
    if scholarship.get("repaired"):
        corrections.append(
            "Adayın sıralamasına uyan burs tutarını, ödeme dönemini ve ilk tercih/devam koşulunu eksiksiz ver. "
            f"Doğruluk özeti: {_as_claims(scholarship_text)}"
        )
        fallbacks["scholarship"] = scholarship_text

    admission_expected, admission_raw = enforce_admission_reality(
        text, rag, question, rank,
    )
    admission = _inspect_admission(text, admission_expected, admission_raw)
    if not admission["clean"]:
        corrections.append(
            "Sıralama değerlendirmesinde küçük sayının daha iyi olduğunu koru ve şu doğruluk özetindeki "
            f"sayı/yön/garanti koşullarını eksiksiz kullan: {_as_claims(admission_expected)}"
        )
        fallbacks["admission"] = admission_expected

    repetition_text, repetition = enforce_non_repetition(text, rag, question, history)
    repetition_issue = bool(
        repetition.get("repaired")
        or repetition.get("reason") == "no_distinct_relevant_card"
    )
    if repetition_issue:
        corrections.append(
            "Önceki cevabın cümle yapısını tekrarlama; aynı kanıtı gerekiyorsa farklı bağlam ve faydayla anlat."
        )
        if repetition.get("repaired"):
            fallbacks["repetition"] = repetition_text

    checks = {
        "fact_gate": fact,
        "answer_relevance": relevance,
        "evidence": evidence,
        "scholarship": scholarship,
        "admission": admission,
        "repetition": repetition,
    }
    return ResponseReview(
        clean=not corrections,
        corrections=list(dict.fromkeys(corrections)),
        checks=checks,
        fallbacks=fallbacks,
    )


def choose_last_resort(review: ResponseReview) -> tuple[str | None, str | None]:
    """Choose a deterministic answer only after the single rewrite also fails."""
    for reason in ("admission", "scholarship", "relevance", "evidence", "repetition"):
        if review.fallbacks.get(reason):
            return review.fallbacks[reason], reason
    return None, None


def _inspect_admission(text: str, expected: str, meta: dict) -> dict:
    inactive_reasons = {
        "rank_unknown",
        "financial_question_not_admission",
        "not_an_admission_turn",
        "comparison_without_admission_question",
    }
    if meta.get("reason") in inactive_reasons:
        return {**meta, "clean": True, "missing_numbers": [], "missing_concepts": []}

    expected_numbers = list(dict.fromkeys(re.findall(r"\d+(?:[.,]\d+)*", expected)))
    missing_numbers = [number for number in expected_numbers if number not in text]
    folded = _fold(text)
    expected_folded = _fold(expected)
    concepts = [
        concept
        for concept in ("onunde", "gerisinde", "garanti", "ucretsiz", "ilk tercih")
        if concept in expected_folded
    ]
    missing_concepts = [concept for concept in concepts if concept not in folded]
    return {
        **meta,
        "clean": not missing_numbers and not missing_concepts,
        "missing_numbers": missing_numbers,
        "missing_concepts": missing_concepts,
    }


def _as_claims(text: str) -> str:
    return " | ".join(
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+", text.strip())
        if part.strip()
    )


_TR_FOLD = str.maketrans("çğıöşüâîûÇĞİÖŞÜÂÎÛ", "cgiosuaiucgiosuaiu")


def _fold(text: str) -> str:
    return text.translate(_TR_FOLD).casefold()
