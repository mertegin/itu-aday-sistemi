import pytest

from app.kb.evidence_gate import enforce_evidence_contract
from app.kb.fact_gate import enforce_fact_gate
from app.kb.retriever import retrieve_facts
from app.llm.client import LLMClient
from app.orchestrator import Orchestrator
from app.profile.schema import CandidateProfile
from app.strategy.router import route_current_turn


ANALYSIS = {
    "asked_followup": True,
    "wants_detail": True,
    "concerns_mentioned": [],
}


@pytest.mark.parametrize(
    ("question", "argument_id"),
    [
        ("Bilgisayar Mühendisliği hangi kampüste?", "itu_campus_life"),
        ("Yemek seçenekleri ve yemekhane ücreti ne?", "itu_dining"),
        ("Öğrenciler mezun olmadan iş bulabiliyor mu?", "itu_career_evidence"),
        ("İngilizce hazırlık zorunlu mu?", "itu_english_prep"),
        ("Tüm okullar böyle değil mi, İTÜ'yü eşsiz yapan ne?", "itu_compe_differentiators"),
        ("Bilgisayar kampüsünde öğrenciler nerede sosyalleşiyor?", "itu_campus_life"),
    ],
)
def test_priority_questions_route_to_dedicated_evidence_arguments(question, argument_id):
    route = route_current_turn(question, ANALYSIS, CandidateProfile())
    assert route.forced_argument_id == argument_id


@pytest.mark.parametrize(
    ("question", "argument_id", "card_id", "number", "example"),
    [
        ("Bilgisayar Mühendisliği hangi kampüste?", "itu_campus_life", "campus_compe_ayazaga_card", "1.600.000", "Mustafa İnan"),
        ("Yemekhane ücreti ve yemek seçenekleri ne?", "itu_dining", "dining_price_menu_card", "47,50", "tantuni"),
        ("Mezun olmadan iş bulabilir miyim, hangi şirketler geliyor?", "itu_career_evidence", "career_employment_companies_card", "%54", "ASELSAN"),
        ("İngilizce hazırlık zorunlu mu?", "itu_english_prep", "prep_flow_card", "1", "TOEFL"),
        ("İTÜ Bilgisayar'ı eşsiz yapan ne?", "itu_compe_differentiators", "differentiator_qs_abet_faculty_card", "91", "Burak Berk Üstündağ"),
    ],
)
def test_evidence_rag_surfaces_short_answer_cards(question, argument_id, card_id, number, example):
    rag = retrieve_facts(question, CandidateProfile(), argument_id)
    assert rag.facts[0].id == card_id
    assert rag.facts[0].answer_card is True
    assert number in rag.facts[0].text
    assert example in rag.facts[0].text
    assert len(rag.facts[0].text.split()) <= 40


def test_student_provided_campus_and_food_examples_are_retrievable():
    campus = retrieve_facts(
        "Kampüste öğrenciler nerede sosyalleşiyor ve nerede yemek yiyor?",
        CandidateProfile(),
        "itu_campus_life",
    )
    campus_text = " ".join(f.text for f in campus.facts)
    assert "Selfish" in campus_text
    assert "Med Çim" in campus_text
    assert "Unkapanı Pilavcısı" in campus_text
    assert "Migros, A101 ve ŞOK" in campus_text

    dining = retrieve_facts(
        "Yemekhanede hangi güzel ve doyurucu yemekler çıkıyor?",
        CandidateProfile(),
        "itu_dining",
    )
    dining_text = " ".join(f.text for f in dining.facts)
    assert "tantuni" in dining_text
    assert "Adana dürüm" in dining_text
    assert "et döner" in dining_text
    assert "limonata" in dining_text


def test_student_feedback_on_faculty_access_and_advising_is_attributed():
    rag = retrieve_facts(
        "Hocalara maille ulaşabilir miyim, danışman hoca atanıyor mu?",
        CandidateProfile(),
        "itu_faculty_research",
    )
    fact = next(f for f in rag.facts if f.id == "differentiator_faculty_access_and_advising_2026")
    assert fact.confidence == "medium"
    assert "Öğrenci geri bildirimi" in fact.source
    assert "danışman hoca" in fact.text


def test_generic_differentiator_answer_is_repaired_with_number_and_faculty_example():
    argument_id = "itu_compe_differentiators"
    rag = retrieve_facts("İTÜ'yü eşsiz yapan ne?", CandidateProfile(), argument_id)
    output, meta = enforce_evidence_contract(
        "İTÜ güçlü akademik kadrosu ve geniş imkanlarıyla iyi bir seçenektir.",
        rag,
        argument_id,
    )
    assert meta["repaired"] is True
    assert meta["card_id"] == "differentiator_qs_abet_faculty_card"
    assert "91" in output
    assert "Burak Berk Üstündağ" in output


def test_rank_3_scholarship_generic_answer_is_repaired_with_exact_tier():
    profile = CandidateProfile(yks_rank=3)
    rag = retrieve_facts("Burs imkanları var mı?", profile, "itu_financial_support")
    assert rag.facts[0].id == "scholarship_rank_1_10"

    output, meta = enforce_evidence_contract(
        "İTÜ'de başarı ve ihtiyaç bursları bulunuyor.",
        rag,
        "itu_financial_support",
    )
    assert meta["repaired"] is True
    assert "100.000 TL" in output
    assert "10.000 TL + 10.000 TL" in output


def test_single_digit_yks_rank_is_extracted_deterministically():
    assert LLMClient._extract_rank("Merhaba, YKS sıralamam Türkiye 3.") == 3
    assert LLMClient._extract_rank("Sıralamam 850") == 850
    assert LLMClient._extract_rank("selam ben mert ve ben 700. oldum yksde") == 700
    assert LLMClient._extract_rank("2026 Kariyer Zirvesi") is None


def test_lowercase_name_is_extracted_without_mistaking_an_ordinary_phrase_for_a_name():
    assert LLMClient._extract_display_name("selam ben mert ve ben 700. oldum yksde") == "Mert"
    assert LLMClient._extract_display_name("ben çok kararsızım") is None


def test_legacy_session_identity_is_backfilled_from_history():
    profile = CandidateProfile()
    Orchestrator._backfill_identity_from_history(profile, [
        {"role": "user", "text": "selam ben mert ve ben 700. oldum yksde"},
        {"role": "assistant", "text": "Eski yanıt"},
    ])
    assert profile.display_name == "Mert"
    assert profile.yks_rank == 700
    assert profile.yks_rank_type == "actual"


@pytest.mark.parametrize(
    ("question", "argument_id", "card_id"),
    [
        ("İlk sınıfta hangi dersler var?", "itu_first_year_curriculum", "curriculum_year1_card"),
        (
            "Bölüm sadece kod yazmaktan mı oluşuyor? Daha önce hiç programlama yapmadım, zorlanır mıyım?",
            "itu_curriculum_beginner",
            "curriculum_beginner_programming_card",
        ),
        (
            "Bilgisayar Mühendisliği bölümünde tam olarak ne öğretiliyor?",
            "itu_curriculum_overview",
            "curriculum_overview_card",
        ),
    ],
)
def test_curriculum_questions_route_to_exact_answer_cards(question, argument_id, card_id):
    route = route_current_turn(question, ANALYSIS, CandidateProfile())
    assert route.forced_argument_id == argument_id

    rag = retrieve_facts(question, CandidateProfile(), argument_id)
    assert rag.facts[0].id == card_id
    assert rag.facts[0].answer_card is True
    assert len(rag.facts[0].text.split()) <= 40


def test_first_year_answer_never_contains_advanced_ai_courses():
    argument_id = "itu_first_year_curriculum"
    rag = retrieve_facts("İlk sınıfta hangi dersler var?", CandidateProfile(), argument_id)
    output, meta = enforce_evidence_contract("İlk yıl temel dersler var.", rag, argument_id)

    assert meta["repaired"] is True
    assert meta["card_id"] == "curriculum_year1_card"
    assert "Bilgi Sistemlerine Giriş" in output
    assert "Bilgisayar Mühendisliğine Giriş ve Etik" in output
    assert "C ile Programlamaya Giriş" in output
    assert "BLG 417E" not in output
    assert "BBF 304E" not in output


def test_unknown_rank_never_uses_a_degree_specific_scholarship_card():
    rag = retrieve_facts("Burs imkanları var mı, ne kadar?", CandidateProfile(), "itu_financial_support")
    output, meta = enforce_evidence_contract(
        "İTÜ'de farklı burs imkanları bulunuyor.",
        rag,
        "itu_financial_support",
    )
    assert meta["card_id"] == "scholarship_first_choice"
    assert "ilk sıraya" in output
    assert "Türkiye 1-10" not in output


def test_fact_gate_rejects_unconditional_prep_not_required_claim():
    rag = retrieve_facts("İngilizce hazırlık zorunlu mu?", CandidateProfile(), "itu_english_prep")
    output, meta = enforce_fact_gate("Hazırlık zorunlu değil; isteyen okuyabilir.", rag)
    assert meta["clean"] is False
    assert any(v["category"] == "prep_not_required" for v in meta["violations"])
    assert "zorunlu değil" not in output.lower()
