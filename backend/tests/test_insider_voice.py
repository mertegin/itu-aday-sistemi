import pytest

from app.guardrails.ethics import enforce_conversation_voice
from app.kb.fact_gate import enforce_answer_relevance, enforce_non_repetition
from app.kb.retriever import retrieve_facts
from app.llm.client import LLMClient
from app.llm.prompts import RESPONSE_SYSTEM_TEMPLATE
from app.profile.schema import CandidateProfile
from app.strategy.router import route_current_turn


def test_response_prompt_uses_insider_itu_identity_and_direct_answers():
    assert "İTÜ'lüsün" in RESPONSE_SYSTEM_TEMPLATE
    assert "bizim bölümümüzde" in RESPONSE_SYSTEM_TEMPLATE
    assert "Sahte kişisel anı uydurma" in RESPONSE_SYSTEM_TEMPLATE
    assert "takip sorusu" in RESPONSE_SYSTEM_TEMPLATE
    assert "kelimesi kelimesine tekrar etme" in RESPONSE_SYSTEM_TEMPLATE
    assert "güvenli bölgedesin" in RESPONSE_SYSTEM_TEMPLATE


def test_direct_answer_drops_automatic_closing_question():
    text, meta = enforce_conversation_voice(
        "Fakültemizde 18 araştırma laboratuvarı var. Bunu düşünür müsün?",
        "itu_technical_resources",
        user_asked_question=True,
        wants_detail=True,
    )
    assert text == "Fakültemizde 18 araştırma laboratuvarı var."
    assert meta["question_removed"] is True


def test_discovery_argument_keeps_one_useful_question():
    text = "Yapay zekâ mı, robotik mi seni daha çok heyecanlandırıyor?"
    output, meta = enforce_conversation_voice(text, "socratic_probe")
    assert output == text
    assert meta["reason"] == "discovery_argument"


@pytest.mark.parametrize(
    ("question", "argument_id", "card_id"),
    [
        ("Hocaların İngilizcesi ve ders anlatımı nasıl?", "itu_faculty_research", "insider_teaching_english_card"),
        ("Laboratuvara hocadan izin alıp girebilir miyim?", "itu_technical_resources", "insider_lab_access_card"),
        ("Yurtta mutfak ve internet var mı?", "itu_housing_details", "insider_dorm_life_card"),
        ("Sınavlar aynı hafta mı, çan sistemi var mı?", "itu_academic_workload", "insider_exam_curve_card"),
        ("Dersten kalma oranı nasıl, çan güzel mi?", "itu_academic_workload", "insider_course_failure_curve_card"),
        ("Bilgisayar öğrencileri dört yılda mezun oluyor mu?", "itu_graduation_requirements", "insider_four_year_graduation_estimate_card"),
        ("İHA takımı, uydu takımı ve TEKNOFEST var mı?", "itu_clubs_teams", "insider_current_tech_teams_card"),
        ("Mezuniyet sonrası iş bulma oranı nedir?", "itu_career_evidence", "insider_employment_outcome_card"),
        ("Bölüm hocaları öğrencilere karşı ilgili mi?", "itu_faculty_research", "insider_faculty_interest_card"),
        ("Hocalara ulaşmak kolay mı?", "itu_faculty_research", "differentiator_faculty_access_and_advising_2026"),
        ("Sınavlarda kod yazmamız isteniyor mu?", "itu_academic_workload", "curriculum_exam_coding_card"),
        ("Algoritma dersleri çok zor mu?", "concern_math_difficulty", "curriculum_algorithms_difficulty_card"),
    ],
)
def test_insider_questions_retrieve_the_matching_answer_card(question, argument_id, card_id):
    rag = retrieve_facts(question, CandidateProfile(), argument_id)
    assert rag.facts[0].id == card_id
    assert rag.facts[0].answer_card is True


def test_unofficial_graduation_estimate_is_explicitly_marked_as_community_data():
    rag = retrieve_facts(
        "Bilgisayar öğrencileri dört yılda mezun oluyor mu?",
        CandidateProfile(),
        "itu_graduation_requirements",
    )
    assert rag.facts[0].confidence == "low"
    assert "resmî bir oran değildir" in rag.facts[0].text
    assert "yaklaşık/topluluk verisi" in rag.prompt_block()


@pytest.mark.parametrize(
    ("question", "argument_id"),
    [
        ("Laboratuvarlara ders dışında girebilir miyim?", "itu_technical_resources"),
        ("Yurtlarda mutfak ve internet var mı?", "itu_housing_details"),
        ("İHA, uydu veya TEKNOFEST takımlarınız var mı?", "itu_clubs_teams"),
        ("Sınavlar aynı haftaya mı yığılıyor, çan sistemi var mı?", "itu_academic_workload"),
        ("Bilgisayar öğrencileri dört yılda mezun oluyor mu?", "itu_graduation_requirements"),
    ],
)
def test_insider_questions_route_to_the_specific_argument(question, argument_id):
    route = route_current_turn(
        question,
        {"asked_followup": True, "wants_detail": True, "concerns_mentioned": []},
        CandidateProfile(),
    )
    assert route.forced_argument_id == argument_id


def test_off_topic_generated_answer_is_repaired_with_top_team_card():
    question = "İHA, uydu veya TEKNOFEST takımlarınız var mı?"
    rag = retrieve_facts(question, CandidateProfile(), "itu_clubs_teams")
    output, meta = enforce_answer_relevance(
        "Ayazağa Kampüsümüzde metro, olimpik havuz ve kütüphane var.",
        rag,
        question,
    )
    assert meta["repaired"] is True
    assert meta["card_id"] == "insider_current_tech_teams_card"
    assert "İTÜNOM" in output
    assert "UZAYTEK" in output


def test_yks_rank_before_oldum_is_extracted():
    assert LLMClient._extract_rank("selam ben Nil yksde 347. oldum") == 347


def test_duplicate_answer_advances_to_another_relevant_card():
    question = "Hocalara ulaşmak kolay mı?"
    rag = retrieve_facts(question, CandidateProfile(), "itu_faculty_research")
    repeated = rag.facts[0].text
    output, meta = enforce_non_repetition(
        repeated,
        rag,
        question,
        [{"role": "assistant", "text": repeated}],
    )
    assert meta["repaired"] is True
    assert output != repeated
