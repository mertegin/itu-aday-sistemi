"""Topic-aware RAG + fact gate testleri."""
from app.kb.fact_gate import enforce_fact_gate
from app.kb.retriever import retrieve_facts
from app.profile.schema import CandidateProfile


def test_retriever_faculty_lab_question():
    p = CandidateProfile(yks_rank=900)
    rag = retrieve_facts("İTÜ'de yapay zeka çalışan hocalar ve laboratuvarlar var mı?", p, "science_motivated_labs")
    assert "faculty" in rag.query_topics or "labs" in rag.query_topics
    joined = " ".join(f.text.lower() for f in rag.facts)
    assert "öğretim" in joined or "laboratuvar" in joined or "araştırma" in joined


def test_retriever_uses_structured_faculty_data_for_nlp_question():
    p = CandidateProfile(yks_rank=900)
    rag = retrieve_facts("NLP ve doğal dil işleme çalışan hoca var mı?", p, "science_motivated_labs")
    joined = " ".join(f.text.lower() for f in rag.facts)
    assert "dilara torunoğlu-selamet" in joined
    assert "natural language processing" in joined


def test_retriever_surfaces_faculty_examples_for_ai_question():
    p = CandidateProfile(yks_rank=900)
    rag = retrieve_facts("Yapay zeka alanında çalışan hocalar var mı?", p, "science_motivated_labs")
    ids = [f.id for f in rag.facts]
    joined = " ".join(f.text.lower() for f in rag.facts)
    assert "faculty_area_ai_data" in ids
    assert any(
        faculty_id in ids
        for faculty_id in (
            "faculty_yusuf_yaslan",
            "faculty_hazim_kemal_ekenel",
            "faculty_burak_berk_ustundag",
            "faculty_gokhan_ince",
        )
    )
    assert "machine learning" in joined or "artificial intelligence" in joined


def test_retriever_department_summary_can_include_faculty_context():
    p = CandidateProfile(yks_rank=900)
    rag = retrieve_facts("Bana İTÜ bilgisayar bölümünden bahset.", p, "ideal_match_summary")
    joined = " ".join(f.text.lower() for f in rag.facts)
    assert "öğretim üyesi" in joined or "resmi öğretim üyesi sayfası" in joined or "araştırma alanları" in joined


def test_retriever_game_question_gets_grad_program_caution():
    p = CandidateProfile(yks_rank=1900)
    p.interests["gamedev"] = 0.5
    rag = retrieve_facts("Oyun yapan bölüm var mı burada?", p, "ai_vs_compe_foundation")
    joined = " ".join(f.text.lower() for f in rag.facts)
    assert "lisans programı/bölümü olarak değil" in joined


def test_fact_gate_blocks_unsupported_game_department_claim():
    p = CandidateProfile(yks_rank=1900)
    rag = retrieve_facts("Oyun yapan bölüm var mı burada?", p, "ai_vs_compe_foundation")
    text = "Evet, İTÜ'de Oyun Teknolojileri adı altında bir lisans bölümü var."
    final, meta = enforce_fact_gate(text, rag)
    assert meta["clean"] is False
    assert meta["replaced"] is True
    assert "lisans bölümü var" not in final.lower()


def test_fact_gate_allows_supported_rank_number():
    p = CandidateProfile(yks_rank=1600)
    rag = retrieve_facts("1600 ile bilgisayara girer miyim?", p, "compe_borderline_1000_1500")
    text = "2025 tabanı yaklaşık 1.435; 1600 için Bilgisayar geçen yılın biraz gerisinde kalıyor."
    final, meta = enforce_fact_gate(text, rag)
    assert meta["clean"] is True
    assert final == text


def test_rank_800_gets_matching_scholarship_amount_and_conditions():
    p = CandidateProfile(yks_rank=800)
    p.constraints.cost_sensitivity = 0.9
    rag = retrieve_facts(
        "Maddi durumum kısıtlı, 800 sıralamayla ne kadar burs alabilirim?",
        p,
        "itu_financial_support",
    )
    ids = [f.id for f in rag.facts]
    assert ids[0] == "scholarship_rank_501_1000"
    assert "scholarship_need_based" in ids
    fact = rag.facts[0]
    assert "6.750 TL" in fact.text
    assert "1. tercihiyle" in fact.text
    assert "2,50" in fact.text
    assert fact.source_url == "https://yurtburs.itu.edu.tr/burs/basari-bursu"


def test_rank_350_gets_101_500_scholarship_tier():
    p = CandidateProfile(yks_rank=350)
    rag = retrieve_facts("Başarı bursu ne kadar?", p, "itu_financial_support")
    assert rag.facts[0].id == "scholarship_rank_101_500"
    assert "8.500 TL" in rag.facts[0].text


def test_unknown_rank_financial_hardship_surfaces_need_and_meal_support():
    p = CandidateProfile()
    p.constraints.cost_sensitivity = 0.9
    rag = retrieve_facts(
        "Ailem masrafları karşılayamaz, geçinmekten endişeliyim.",
        p,
        "itu_financial_support",
    )
    ids = [f.id for f in rag.facts]
    assert "scholarship_need_based" in ids[:3]
    assert "scholarship_meal" in ids[:4]


def test_entrepreneurship_question_gets_current_official_figures():
    p = CandidateProfile(yks_rank=800)
    p.indecision.motivation["entrepreneurship"] = 0.9
    p.constraints.cost_sensitivity = 0.9
    rag = retrieve_facts(
        "İTÜ Çekirdek girişim ve yatırım konusunda ne kadar güçlü?",
        p,
        "itu_entrepreneurship_ecosystem",
    )
    ids = [f.id for f in rag.facts]
    assert ids[0].startswith("itu_cekirdek_")
    assert "itu_cekirdek_impact_2025" in ids
    assert "itu_cekirdek_investment_2025" in ids
    joined = " ".join(f.text for f in rag.facts)
    assert "5.000'den fazla" in joined
    assert "325 milyon doları" in joined
    assert all(
        f.source_url.startswith("https://itucekirdek.com/")
        for f in rag.facts
        if f.id.startswith("itu_cekirdek_")
    )


def test_fact_gate_allows_supported_scholarship_amount_but_blocks_invented_amount():
    p = CandidateProfile(yks_rank=800)
    rag = retrieve_facts("800 sıralamayla burs ne kadar?", p, "itu_financial_support")

    supported = "2025 koşullarında, ilk tercihle yerleşirsen yılda 9 ay aylık 6.750 TL burs var; devamı için GNO en az 2,50 olmalı."
    final, meta = enforce_fact_gate(supported, rag)
    assert meta["clean"] is True
    assert final == supported

    _, invented_meta = enforce_fact_gate("Aylık 12.500 TL burs alırsın.", rag)
    assert invented_meta["clean"] is False
    assert any(v["category"] == "unsupported_number" for v in invented_meta["violations"])


def test_fact_gate_blocks_unsupported_student_satisfaction_claim():
    from app.kb.retriever import RagResult

    rag = RagResult(query_topics=["curriculum"], facts=[])
    final, meta = enforce_fact_gate("İTÜ'de öğrenci memnuniyeti çok yüksek.", rag)
    assert meta["clean"] is False
    assert meta["replaced"] is True
    assert "memnuniyeti çok yüksek" not in final.lower()


def test_fact_gate_blocks_unsupported_women_representation_trend():
    from app.kb.retriever import RagResult

    rag = RagResult(query_topics=["faculty"], facts=[])
    _, meta = enforce_fact_gate("Bilgisayar bölümünde kadınların sayısı giderek artıyor.", rag)
    assert any(v["category"] == "women_representation" for v in meta["violations"])


def test_safe_response_does_not_leak_bot_instructions():
    """REGRESYON: 'küçümseme, kabul et' gibi bota yazılmış yönerge fact'leri
    güvenli cevaba kopyalanıp ADAYA SIZMAMALI (canlı testte yakalandı)."""
    from app.kb.fact_gate import build_safe_response, _is_instructional
    from app.kb.retriever import RagResult, RetrievedFact

    instructional = RetrievedFact(
        id="taviz_koc", confidence="medium",
        text="Koç tam burslu paketi çok güçlü bir teklif — adayın elinde varsa bunu küçümseme, ciddi bir alternatif olarak kabul et.",
    )
    speakable = RetrievedFact(
        id="cekirdek", confidence="high",
        text="İTÜ Çekirdek: UBI Global'e göre dünyanın 1 numaralı üniversite kuluçkası.",
    )
    assert _is_instructional(instructional.text)
    assert not _is_instructional(speakable.text)

    rag = RagResult(query_topics=["scholarship"], facts=[instructional, speakable])
    safe = build_safe_response(rag)
    assert "küçümseme" not in safe
    assert "kabul et" not in safe
    assert "Çekirdek" in safe  # konuşulabilir fact kullanılabilir

    # Sadece yönerge fact'i varsa → kaynak-yok metnine düş
    rag_only_instr = RagResult(query_topics=["scholarship"], facts=[instructional])
    safe2 = build_safe_response(rag_only_instr)
    assert "küçümseme" not in safe2
    assert "net kaynaklı bilgi" in safe2


def test_new_coverage_topics_and_arguments():
    """Kapsam genişletme: yazılım-vs-compe, üniv karşılaştırma, AI-gelecek."""
    from app.arguments.catalog import ARGUMENTS
    from app.kb.retriever import infer_query_topics
    from app.profile.normalize import normalize_department
    from app.strategy.bandit import ArgumentSelector
    from app.fsm.states import FSMState

    # Katalogda yeni argümanlar var
    for arg_id in (
        "software_vs_compe", "university_comparison_general", "future_of_compe",
        "itu_faculty_research", "itu_curriculum_flexibility",
        "itu_student_life_support", "itu_global_opportunities",
        "itu_clubs_projects", "itu_admission_reality", "itu_financial_support",
        "itu_entrepreneurship_ecosystem",
    ):
        assert arg_id in ARGUMENTS

    # Normalize: yazılım ailesi
    assert normalize_department("yazılım mühendisliği") == "yazilim"
    assert normalize_department("Software Engineering") == "yazilim"

    # Topic çıkarımı
    p = CandidateProfile(yks_rank=1000)
    t1 = infer_query_topics("Bilgisayar ile yazılım mühendisliği arasındaki fark ne?", p)
    assert "software_vs_compe" in t1
    t2 = infer_query_topics("Yapay zeka gelişti, bilgisayar mühendisliğinin geleceği ne olacak?", p)
    assert "future_of_field" in t2
    t3 = infer_query_topics("Boğaziçi ile aranızdaki fark ne, bir de Yıldız Teknik?", p)
    assert "comparison" in t3

    # RAG yeni fact'leri buluyor
    rag1 = retrieve_facts("yazılım mühendisliği ile bilgisayar farkı nedir", p, "software_vs_compe")
    joined1 = " ".join(f.text.lower() for f in rag1.facts)
    assert "yazılım" in joined1
    rag2 = retrieve_facts("yapay zeka işimizi alacak mı, bölümün geleceği var mı", p, "future_of_compe")
    joined2 = " ".join(f.text.lower() for f in rag2.facts)
    assert "yapay zek" in joined2 or "otomasyon" in joined2 or "17,9" in joined2

    # Bandit eligibility
    sel = ArgumentSelector()
    p2 = CandidateProfile(yks_rank=1000)
    p2.indecision.university_alternatives = ["bogazici"]
    elig = sel._eligible_for_state(FSMState.S3_ARGUMENT_SELECTION, p2, {})
    assert "university_comparison_general" in elig

    p3 = CandidateProfile(yks_rank=1000)
    p3.indecision.department_alternatives = ["yazilim"]
    elig3 = sel._eligible_for_state(FSMState.S3_ARGUMENT_SELECTION, p3, {})
    assert "software_vs_compe" in elig3

    p4 = CandidateProfile(yks_rank=1000)
    p4.concerns = ["employment"]
    elig4 = sel._eligible_for_state(FSMState.S7_CONCERN_HANDLING, p4, {})
    assert "future_of_compe" in elig4


def test_safe_response_picks_question_relevant_fact():
    """REGRESYON: 'kaçıncı sıraya yazayım' sorusuna 'araştırma alanları' fact'i dönmemeli."""
    from app.kb.fact_gate import build_safe_response
    from app.kb.retriever import RagResult, RetrievedFact

    irrelevant = RetrievedFact(
        id="labs", confidence="high",
        text="Bölümün araştırma alanları arasında bilgisayarlı görü ve doğal dil işleme yer alır.",
    )
    relevant = RetrievedFact(
        id="tercih", confidence="high",
        text="YKS yerleştirme sisteminde en çok istediğin bölümü üst sıraya yazmak kaybettirmez; tercih listesi sıralamana göre yerleşirsin.",
    )
    rag = RagResult(query_topics=["ranking"], facts=[irrelevant, relevant])

    out = build_safe_response(rag, question="Tercih listemde İTÜ'yü kaçıncı sıraya yazmalıyım?")
    assert "üst sıraya yazmak kaybettirmez" in out
    assert "bilgisayarlı görü" not in out

    # Hiç alakalı fact yoksa → alakasız fact okumak yerine kaynak-yok metni
    rag2 = RagResult(query_topics=["ranking"], facts=[irrelevant])
    out2 = build_safe_response(rag2, question="Yemekhane fiyatları ne kadar?")
    assert "net kaynaklı bilgi yok" in out2


def test_instructional_markers_extended():
    """Kullanıcının hoca fact'indeki 'doğrulanmalı/uydurma' yönergeleri de sızmamalı."""
    from app.kb.fact_gate import _is_instructional
    assert _is_instructional("Kesin isim bilgisi resmi sayfadan doğrulanmalı; RAG'de isim yoksa hoca adı uydurma.")
    assert not _is_instructional("İTÜ Bilgisayar 2025 taban sırası yaklaşık 1.435'tir.")


def test_gate_salvages_clean_sentences_instead_of_dropping_all():
    """sess_051a T6: tek ihlalli cümle yüzünden tüm cevap atılmamalı."""
    from app.kb.fact_gate import enforce_fact_gate
    from app.kb.retriever import RagResult, RetrievedFact

    fact = RetrievedFact(id="quality", confidence="high",
                         text="İTÜ Bilgisayar ABET akreditelidir ve QS Mühendislik & Teknoloji dünya 91. sıradadır.")
    rag = RagResult(query_topics=["comparison"], facts=[fact])
    text = ("İTÜ Bilgisayar ABET akreditelidir. "
            "Mezunların yüzde 99'u ilk hafta işe girer garanti ederim. "
            "QS Mühendislik & Teknoloji sıralamasında dünya 91. sıradadır.")
    final, meta = enforce_fact_gate(text, rag, question="itü bilgisayar kaliteli mi")
    assert meta["replaced"] is True
    assert meta.get("salvaged") is True
    assert "garanti ederim" not in final
    assert "ABET" in final and "91" in final  # temiz cümleler korunur


def test_relevance_ignores_domain_stopwords():
    """sess_051a T7: 'itü bilgisayar kaliteli mi' sorusuna hoca-eposta fact'i seçilmemeli."""
    from app.kb.fact_gate import build_safe_response
    from app.kb.retriever import RagResult, RetrievedFact

    faculty = RetrievedFact(id="hoca", confidence="high",
                            text="Yusuf Yaslan, İTÜ Bilgisayar Mühendisliği kadrosunda Doç. Dr. olarak yer alır.")
    quality = RetrievedFact(id="kalite", confidence="high",
                            text="İTÜ Bilgisayar'ın eğitim kalitesi kanıtları: QS 91, ABET, kontenjan her yıl doluyor.")
    rag = RagResult(query_topics=["comparison"], facts=[faculty, quality])
    out = build_safe_response(rag, question="neymiş itü bilgisayar kaliteli mi")
    assert "kalite" in out.lower()
    assert "Yaslan" not in out


def test_router_social_life_beats_difficulty():
    """sess_051a T9: 'bölüm yoğun, sosyal hayata zaman kalır mı' difficulty'ye gitmemeli."""
    from app.strategy.router import route_current_turn
    from app.profile.schema import CandidateProfile
    route = route_current_turn(
        "Bölüm çok yoğun olduğu için sosyal hayata zaman kalıyor mu?",
        {"asked_followup": True, "wants_detail": True, "concerns_mentioned": []},
        CandidateProfile(),
    )
    assert route.primary_topic == "social_life"
    assert route.forced_argument_id == "itu_clubs_projects"


def test_router_quality_and_dept_info():
    from app.strategy.router import route_current_turn
    from app.profile.schema import CandidateProfile
    r1 = route_current_turn("devlet okulu neticede kaliteli mi",
                            {"asked_followup": True, "wants_detail": True, "concerns_mentioned": []},
                            CandidateProfile())
    assert r1.primary_topic == "quality"
    r2 = route_current_turn("bilgisayar mühendisliği hakkında bilgi almak istiyorum",
                            {"asked_followup": False, "wants_detail": True, "concerns_mentioned": []},
                            CandidateProfile())
    assert r2.primary_topic == "dept_info"


def test_ordinal_dot_does_not_split_sentence():
    """sess_1329: 'QS'de 91. sırada' ifadesi cümle ortasından kesiliyordu."""
    from app.kb.fact_gate import split_sentences_tr
    parts = split_sentences_tr("İTÜ, QS sıralamasında 91. sırada yer alıyor. Ayrıca ABET akreditelidir.")
    assert len(parts) == 2
    assert "91. sırada yer alıyor" in parts[0]

    from app.guardrails.ethics import enforce_spoken_length
    text, meta = enforce_spoken_length(
        "İTÜ QS Mühendislik sıralamasında 91. sırada yer alıyor ve bu alandaki tek Türk üniversitesidir. "
        + " ".join(["dolgu"] * 45), max_words=20)
    assert "91. sırada" in text  # sayı kesilmedi


def test_active_question_never_closes_fsm():
    """sess_1329 ping-pong: aday soru sorarken FSM S8'e gitmemeli."""
    from app.fsm.machine import _wants_close
    assert not _wants_close({"intent": "close", "asked_followup": True})
    assert not _wants_close({"decision_status": "itu_compe_committed", "wants_detail": True})
    assert _wants_close({"intent": "close", "asked_followup": False, "wants_detail": False})


def test_router_comparison_covers_fark_and_kazanim():
    from app.strategy.router import route_current_turn
    from app.profile.schema import CandidateProfile
    a = {"asked_followup": True, "wants_detail": True, "concerns_mentioned": []}
    for q in ["İTÜ'nün diğer üniversitelerden farkı nedir?",
              "İTÜ'yü seçersem diğer üniversitelere göre ne kazanırım?",
              "itüyü eşsiz yapan detay ne"]:
        r = route_current_turn(q, a, CandidateProfile())
        assert r.forced_argument_id == "itu_compe_differentiators", q
