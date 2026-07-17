import pytest

from app.kb.retriever import retrieve_facts
from app.kb.evidence_gate import enforce_evidence_contract
from app.profile.schema import CandidateProfile
from app.strategy.router import route_current_turn


ANALYSIS = {
    "asked_followup": True,
    "wants_detail": True,
    "concerns_mentioned": [],
}


@pytest.mark.parametrize(
    ("question", "topic", "argument_id", "card_id"),
    [
        ("İlk sınıfta hangi dersler var?", "curriculum_year1", "itu_first_year_curriculum", "curriculum_year1_card"),
        ("Hangi programlama dilleri öğretiliyor?", "curriculum_details", "itu_curriculum_details", "curriculum_language_card"),
        ("Ders yükü ve sınav sistemi nasıl?", "academic_workload", "itu_academic_workload", "curriculum_workload_honesty_card"),
        ("İngilizce hazırlık zorunlu mu?", "english_prep", "itu_english_prep", "prep_flow_card"),
        ("Bilgisayar laboratuvarlarını ders dışında kullanabilir miyim?", "technical_resources", "itu_technical_resources", "lab_access_honesty_card"),
        ("Staj zorunlu mu, kaç gün?", "internship", "itu_internship_pathways", "internship_requirements_card"),
        ("İTÜ adı tek başına iş buldurur mu?", "career", "money_motivated_data", "career_name_not_enough_card"),
        ("Lisans öğrencisi hocayla araştırma yapabilir mi?", "research_projects", "itu_research_projects", "undergraduate_research_card"),
        ("Siber güvenlikte uzmanlaşabilir miyim?", "specialization", "itu_specialization", "curriculum_ai_security_electives_card"),
        ("ÇAP ve yandal şartları neler?", "double_major_transfer", "itu_double_major_transfer", "double_major_minor_card"),
        ("Erasmus dersleri İTÜ'de sayılır mı?", "erasmus", "itu_erasmus_mobility", "erasmus_course_recognition_card"),
        ("Hangi öğrenci kulüpleri ve takımları var?", "clubs_teams", "itu_clubs_teams", "department_clubs_teams_card"),
        ("Yurt ücretleri ve kapasitesi ne?", "housing_details", "itu_housing_details", "housing_capacity_fees_card"),
        ("İstanbul'da kampüsten metroya erişim nasıl?", "istanbul_life", "itu_istanbul_life", "istanbul_transport_card"),
        ("Öğrenci profili rekabetçi mi?", "student_social", "itu_clubs_teams", "student_profile_honesty_card"),
        ("Yalnız hissedersem psikolojik destek var mı?", "student_wellbeing", "itu_student_wellbeing", "psychological_support_card"),
        ("İTÜ Bilgisayar kaç binle alıyor?", "ranking", "itu_admission_reality", "admission_compe_cutoff_card"),
        ("Mezuniyet için kaç AKTS ve ortalama gerekir?", "graduation", "itu_graduation_requirements", "graduation_requirements_card"),
        ("Bir dersten kalırsam dünyanın sonu mu?", "difficulty", "concern_math_difficulty", "academic_recovery_honesty_card"),
        ("Bölümde yazılım mı donanım mı ağırlıklı?", "electronics", "electronics_vs_compe_overlap", "curriculum_balance_card"),
    ],
)
def test_representative_question_routes_to_specific_evidence_card(
    question, topic, argument_id, card_id,
):
    profile = CandidateProfile()
    route = route_current_turn(question, ANALYSIS, profile)
    assert route.primary_topic == topic
    assert route.forced_argument_id == argument_id

    rag = retrieve_facts(question, profile, argument_id)
    assert rag.facts[0].id == card_id
    assert rag.facts[0].answer_card is True
    assert len(rag.facts[0].text.split()) <= 40


def test_full_attached_question_bank_is_routed_and_has_evidence_cards():
    from audit_question_coverage import audit, read_questions
    from pathlib import Path

    path = Path(
        r"C:\Users\90553\.codex\attachments\60467227-a741-4ddf-a1ef-472ded37c738\pasted-text.txt"
    )
    if not path.exists():
        pytest.skip("Conversation attachment is not available outside this workspace.")

    rows = audit(read_questions(path))
    candidate_rows = [row for row in rows if row["topic"] != "profile_probe"]
    assert len(candidate_rows) == 451
    assert all(row["topic"] != "general" for row in candidate_rows)
    assert all(row["covered"] for row in candidate_rows)


@pytest.mark.parametrize(
    ("question", "argument_id", "wrong_answer", "expected_card", "expected_text"),
    [
        (
            "Erasmus dersleri İTÜ'de sayılır mı?",
            "itu_erasmus_mobility",
            "Erasmus stajı en az 60 gün sürer ve B1/65 gerekir.",
            "erasmus_course_recognition_card",
            "OLA",
        ),
        (
            "Yalnız hissedersem psikolojik destek var mı?",
            "itu_student_wellbeing",
            "Bölümde 5 kulüp, 3 takım ve 18 laboratuvar vardır.",
            "psychological_support_card",
            "934",
        ),
    ],
)
def test_same_topic_but_wrong_subtopic_is_repaired_from_top_card(
    question, argument_id, wrong_answer, expected_card, expected_text,
):
    rag = retrieve_facts(question, CandidateProfile(), argument_id)
    output, meta = enforce_evidence_contract(wrong_answer, rag, argument_id)
    assert meta["repaired"] is True
    assert meta["card_id"] == expected_card
    assert expected_text in output
