"""Ensure evidence-heavy answers contain a sourced number and concrete example.

The LLM receives the same requirement in its prompt, but this deterministic
gate protects the negotiation flow when the generated answer is still generic.
It may only repair an answer by copying a short, retrieved answer card.
"""
from dataclasses import dataclass, field
import re

from .retriever import RagResult, RetrievedFact


@dataclass(frozen=True)
class EvidenceRequirement:
    number: bool = False
    example: bool = False
    card_ids: tuple[str, ...] = ()


@dataclass
class EvidenceGateResult:
    required: bool
    clean: bool
    missing: list[str] = field(default_factory=list)
    repaired: bool = False
    card_id: str | None = None
    available_examples: list[str] = field(default_factory=list)
    original_text: str | None = None

    def to_dict(self) -> dict:
        return {
            "required": self.required,
            "clean": self.clean,
            "missing": self.missing,
            "repaired": self.repaired,
            "card_id": self.card_id,
            "available_examples": self.available_examples,
            "original_text": self.original_text,
        }


REQUIREMENTS: dict[str, EvidenceRequirement] = {
    "itu_financial_support": EvidenceRequirement(number=True),
    "itu_entrepreneurship_ecosystem": EvidenceRequirement(number=True, example=True),
    "itu_campus_life": EvidenceRequirement(number=True, example=True),
    "itu_dining": EvidenceRequirement(number=True, example=True),
    "itu_career_evidence": EvidenceRequirement(number=True, example=True),
    "itu_english_prep": EvidenceRequirement(number=True, example=True),
    "itu_compe_differentiators": EvidenceRequirement(number=True, example=True),
    "university_comparison_general": EvidenceRequirement(number=True, example=True),
    "itu_faculty_research": EvidenceRequirement(example=True),
    "itu_first_year_curriculum": EvidenceRequirement(
        number=True,
        example=True,
        card_ids=("curriculum_year1_card",),
    ),
    "itu_curriculum_beginner": EvidenceRequirement(
        number=True,
        example=True,
        card_ids=("curriculum_beginner_programming_card",),
    ),
    "itu_curriculum_overview": EvidenceRequirement(
        example=True,
        card_ids=("curriculum_overview_card",),
    ),
    "itu_curriculum_details": EvidenceRequirement(number=True, example=True),
    "itu_academic_workload": EvidenceRequirement(number=True, example=True),
    "itu_technical_resources": EvidenceRequirement(number=True, example=True),
    "itu_internship_pathways": EvidenceRequirement(number=True, example=True),
    "itu_research_projects": EvidenceRequirement(number=True, example=True),
    "itu_specialization": EvidenceRequirement(number=True, example=True),
    "itu_double_major_transfer": EvidenceRequirement(number=True, example=True),
    "itu_erasmus_mobility": EvidenceRequirement(number=True, example=True),
    "itu_clubs_teams": EvidenceRequirement(number=True, example=True),
    "itu_clubs_projects": EvidenceRequirement(number=True, example=True),
    "itu_social_venues": EvidenceRequirement(example=True),
    "itu_housing_details": EvidenceRequirement(number=True, example=True),
    "itu_istanbul_life": EvidenceRequirement(example=True),
    "itu_student_wellbeing": EvidenceRequirement(number=True, example=True),
    "itu_graduation_requirements": EvidenceRequirement(number=True, example=True),
}

_TR_FOLD = str.maketrans("çğıöşüâîûÇĞİÖŞÜÂÎÛ", "cgiosuaiucgiosuaiu")


def enforce_evidence_contract(
    text: str,
    rag: RagResult,
    argument_id: str,
) -> tuple[str, dict]:
    requirement = REQUIREMENTS.get(argument_id)
    if requirement is None:
        return text, EvidenceGateResult(required=False, clean=True).to_dict()
    if (
        argument_id == "itu_housing_details"
        and rag.facts
        and rag.facts[0].id == "housing_application_path_card"
    ):
        requirement = EvidenceRequirement(example=True, card_ids=("housing_application_path_card",))

    eligible_facts = [
        fact for fact in rag.facts
        if fact.answer_card
        and fact.applicable
        and (not requirement.card_ids or fact.id in requirement.card_ids)
    ]
    # A broad argument can contain several valid subtopic cards (for example
    # Erasmus selection, internship and course recognition). Evidence must
    # match the query-ranked first card, not merely any card in that argument.
    if not requirement.card_ids and eligible_facts:
        eligible_facts = eligible_facts[:1]
    examples = list(dict.fromkeys(
        example.strip()
        for fact in eligible_facts
        for example in fact.examples
        if example and example.strip()
    ))
    missing = _missing_evidence(text, requirement, examples)
    if not missing:
        return text, EvidenceGateResult(
            required=True,
            clean=True,
            available_examples=examples,
        ).to_dict()

    card = _choose_answer_card(rag.facts, requirement)
    if card is None:
        return text, EvidenceGateResult(
            required=True,
            clean=False,
            missing=missing,
            available_examples=examples,
        ).to_dict()

    repaired_missing = _missing_evidence(card.text, requirement, card.examples)
    return card.text, EvidenceGateResult(
        required=True,
        clean=not repaired_missing,
        missing=repaired_missing,
        repaired=True,
        card_id=card.id,
        available_examples=examples,
        original_text=text,
    ).to_dict()


def _missing_evidence(
    text: str,
    requirement: EvidenceRequirement,
    examples: list[str],
) -> list[str]:
    missing: list[str] = []
    if requirement.number and not re.search(r"%?\d+(?:[.,]\d+)?", text):
        missing.append("number")
    if requirement.example and examples:
        folded_text = _fold(text)
        if not any(_fold(example) in folded_text for example in examples):
            missing.append("example")
    return missing


def _choose_answer_card(
    facts: list[RetrievedFact],
    requirement: EvidenceRequirement,
) -> RetrievedFact | None:
    for fact in facts:
        if not fact.answer_card or not fact.applicable:
            continue
        if requirement.card_ids and fact.id not in requirement.card_ids:
            continue
        if not _missing_evidence(fact.text, requirement, fact.examples):
            return fact
    return None


def _fold(text: str) -> str:
    return " ".join(text.translate(_TR_FOLD).lower().split())
