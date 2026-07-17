"""Current-turn topic router for negotiation argument selection.

The long-term profile tells us what may persuade the candidate. The current
message tells us what must be answered now. Explicit questions therefore get
priority over bandit exploration; softer signals become bandit preferences.
"""
from dataclasses import dataclass, field

from ..profile.schema import CandidateProfile


_TR_FOLD = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")


def _fold(text: str) -> str:
    return " ".join(text.translate(_TR_FOLD).lower().split())


@dataclass
class RouteDecision:
    primary_topic: str = "general"
    topics: list[str] = field(default_factory=list)
    forced_argument_id: str | None = None
    preferred_arguments: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reason: str = "Belirgin bir güncel konu bulunamadı; profil tabanlı seçim kullanılacak."

    def to_dict(self) -> dict:
        return {
            "primary_topic": self.primary_topic,
            "topics": self.topics,
            "forced_argument_id": self.forced_argument_id,
            "preferred_arguments": self.preferred_arguments,
            "confidence": round(self.confidence, 2),
            "reason": self.reason,
        }


_TOPIC_RULES: list[tuple[str, tuple[str, ...], str, float]] = [
    (
        "comparison_financial_offer",
        ("para teklif", "maddi teklif", "burs teklif", "aylik odeme teklif", "nakit teklif"),
        "koc_vs_itu_value",
        0.99,
    ),
    (
        "curriculum_year1",
        (
            "ilk sinif", "birinci sinif", "1. sinif", "1 sinif", "ilk yil", "birinci yil",
            "1. yariyil", "1 yariyil", "2. yariyil", "2 yariyil",
        ),
        "itu_first_year_curriculum",
        0.99,
    ),
    (
        "curriculum_beginner",
        (
            "sadece kod", "yalnizca kod", "kod yazmaktan", "hic programlama",
            "daha once programlama", "programlama yapmadim", "kodlama bilmiyorum",
            "programlama bilmiyorum", "zorlanir miyim",
        ),
        "itu_curriculum_beginner",
        0.99,
    ),
    (
        "double_major_transfer",
        ("cift anadal", "cap yap", "cap sart", "yandal", "yatay gecis", "bolum degistir", "ikinci diploma"),
        "itu_double_major_transfer",
        0.99,
    ),
    (
        "erasmus",
        ("erasmus", "degisim program", "yurt disinda donem", "yurt disinda staj", "hangi ulke", "hangi universiteyle anlasma"),
        "itu_erasmus_mobility",
        0.99,
    ),
    (
        "graduation",
        ("mezuniyet sart", "mezun olmak icin", "dort yilda mezun", "4 yilda mezun", "mezuniyet orani", "kac kredi", "kac akts", "erken mezun", "okulu uzat", "azami sure", "yaz okulu", "butunleme", "bitirmek zor"),
        "itu_graduation_requirements",
        0.98,
    ),
    (
        "internship",
        ("staj zorunlu", "zorunlu staj", "staj kac gun", "staj suresi", "stajda ne", "staj sistemi", "staj raporu", "online staj", "uzaktan staj"),
        "itu_internship_pathways",
        0.99,
    ),
    (
        "research_projects",
        ("arastirma projes", "hocayla proje", "hocayla arastirma", "lisans arastirma", "lisans ogrencisi", "tubitak", "yayin yap", "laboratuvara katil", "projelere katil", "proje gelistir"),
        "itu_research_projects",
        0.97,
    ),
    (
        "specialization",
        ("uzmanlas", "secmeli ders", "hangi alana yonel", "alan sec", "yapay zekaya yonel", "siber guvenlige yonel", "oyun gelistirmeye yonel"),
        "itu_specialization",
        0.97,
    ),
    (
        "curriculum_details",
        ("hangi programlama dili", "programlama dilleri", "python ogretil", "java ogretil", "c++ ogretil", "isletim sistemi dersi", "bitirme projesi", "ders projeleri", "uygulamali mi", "teorik mi"),
        "itu_curriculum_details",
        0.97,
    ),
    (
        "academic_workload",
        ("ders yuku", "haftada kac saat", "kac saat calis", "sinav sistemi", "sinavlar ayni hafta", "sinav haft", "can sistemi", "can egrisi", "can guzel", "dersten kalma orani", "notlandirma", "kalma orani", "odev yogun", "ezber", "vize final", "dersleri duzenli takip", "dersi duzenli takip", "takip etmek yeterli", "derse gitmek yeterli"),
        "itu_academic_workload",
        0.97,
    ),
    (
        "technical_resources",
        ("bilgisayar laboratuvar", "laboratuvara ders disinda", "laboratuvarlara ders disinda", "lab eris", "hoca izni", "teknik imkan", "sunucu", "gpu", "ekipman", "laboratuvar eris", "kutuphane kac", "calisma alani"),
        "itu_technical_resources",
        0.96,
    ),
    (
        "clubs_teams",
        ("hangi kulup", "ogrenci kulup", "ogrenci takimi", "proje takimi", "iha takimi", "uydu takimi", "teknofest", "uzaytek", "spor takimi", "hackathon", "acm", "gdg", "datathon"),
        "itu_clubs_teams",
        0.97,
    ),
    (
        "gamedev",
        ("bilgisayar oyunu", "oyun oyna", "oyun oynamayi", "oyun gelistir", "oyun tasarla"),
        "itu_clubs_projects",
        0.96,
    ),
    (
        "housing_details",
        ("yurt fiy", "yurt ucret", "yurt kapas", "yurtlarda mutfak", "yurtta mutfak", "yurt internet", "yurtlarda internet", "yurtta internet", "oda secenek", "kac kisilik oda", "yurt cikar", "yurt cikma", "yurt basvuru", "ozel yurt", "eve cik"),
        "itu_housing_details",
        0.98,
    ),
    (
        "istanbul_life",
        ("istanbul'da", "istanbulda", "ulasim nasil", "metro var", "trafik", "sehir pahali", "taksim", "levent"),
        "itu_istanbul_life",
        0.96,
    ),
    (
        "student_social",
        ("ogrenci profili", "arkadas ortami", "rekabetci", "dayanisma", "sosyal cevre", "arkadas edin", "inek ogrenci"),
        "itu_clubs_teams",
        0.95,
    ),
    (
        "student_wellbeing",
        ("yalniz kal", "yalniz hiss", "uyum sagla", "psikolojik", "kaygi", "stres", "bunal", "pisman olur", "destek al", "danismanlik"),
        "itu_student_wellbeing",
        0.97,
    ),
    (
        "future_of_field",
        ("isimizi al", "issiz kal", "meslek olur mu", "meslek biter", "gelecegi var", "ai gelis", "otomasyon"),
        "future_of_compe",
        0.96,
    ),
    (
        "family",
        ("ailem", "babam", "annem", "aile bask", "aileme nasil", "ikna ederim", "aile sirket", "hazir sirket"),
        "concern_family_pressure",
        0.94,
    ),
    (
        "difficulty",
        ("matematik", "derslerden kal", "kalirsam", "cok zor", "zorlanirsam", "okul yogun", "ders yuku"),
        "concern_math_difficulty",
        0.93,
    ),
    (
        "faculty_research",
        (
            "hoca", "ogretim uyes", "akademik kadro", "kim calisiyor", "laboratuvar", "lab ",
            "arastirma imkani", "danisman hoca", "akademik danisman", "mail at", "iletisim kur",
            "hocalara ulas", "ulasilabilir mi", "ders destegi", "hocadan destek",
        ),
        "itu_faculty_research",
        0.95,
    ),
    (
        "dining",
        (
            "yemekhane", "yemek ucreti", "yemek fiyati", "yemek secenek", "ne yenir",
            "ogle yemegi", "aksam yemegi", "menu", "vejetaryen yemek",
        ),
        "itu_dining",
        0.98,
    ),
    (
        "financial_support",
        (
            "burs", "maddi", "para sikint", "gecinem", "karsilayam", "odeyem",
            "butce", "ekonomik durum", "masraf", "ucret", "maliyet",
        ),
        "itu_financial_support",
        0.97,
    ),
    (
        "campus_life",
        (
            "hangi kampus", "kampusu nerede", "kampuste ne var", "kampus hakkinda",
            "ayazaga", "maslak kampusu", "sosyal alan", "spor tesisi", "kutuphane",
            "yuzme havuzu", "stadyum", "golet", "kampus secenek", "kampuste ogrenciler",
            "kampusunde ogrenciler", "nerede sosyalles", "nerede yemek yen", "kampuste yemek",
        ),
        "itu_campus_life",
        0.97,
    ),
    (
        "english_prep",
        (
            "hazirlik zorunlu", "hazirlik okum", "hazirlik atla", "yeterlik sinavi",
            "proficiency", "muafiyet", "toefl", "pte", "ingilizce hazirlik",
        ),
        "itu_english_prep",
        0.98,
    ),
    (
        "career_evidence",
        (
            "mezun olmadan", "mezuniyetten once", "is bulabiliyor", "ise basla",
            "kariyer zirvesi", "hangi sirket", "hangi firma", "firma geliyor",
            "staj bul", "isveren ilgisi",
        ),
        "itu_career_evidence",
        0.97,
    ),
    (
        "differentiators",
        (
            "diger universitelerden fark", "universitelerden farki", "farki nedir",
            "ne kazanirim", "essiz yapan", "en buyuk avantaj", "neden itu",
            "neden tercih", "tum okullar", "her okul", "her universite",
        ),
        "itu_compe_differentiators",
        0.97,
    ),
    (
        "social_life",
        ("sosyal hayat", "sosyal hayata", "sosyal yasam", "eglence", "arkadas edin", "kulup var mi"),
        "itu_clubs_projects",
        0.93,
    ),
    (
        "quality",
        ("kaliteli mi", "kalitesi", "egitim kalite", "gercekten iyi mi", "deger mi", "memnun mu"),
        "university_comparison_general",
        0.93,
    ),
    (
        "dept_info",
        ("hakkinda bilgi", "tanitir misin", "ne ogretiliyor", "neler yapar", "neler ogren",
         "anlatir misin", "bolumde ne var", "tam olarak ne"),
        "itu_curriculum_overview",
        0.92,
    ),
    (
        "student_support",
        ("yurt", "barinma", "kampus nasil"),
        "itu_student_life_support",
        0.94,
    ),
    (
        "global",
        ("yurt dis", "yurtdis", "erasmus", "cift diploma", "uluslararasi", "almanya", "abd'de", "abd de"),
        "itu_global_opportunities",
        0.93,
    ),
    (
        "software_vs_compe",
        ("yazilim muhendisligi", "software engineering", "yazilim bolumu", "yazilim mi bilgisayar"),
        "software_vs_compe",
        0.96,
    ),
    (
        "ai_vs_compe",
        ("yapay zeka mi", "ai mi", "yapay zeka ve veri", "machine learning engineer", "yz mi"),
        "ai_vs_compe_foundation",
        0.96,
    ),
    (
        "electronics",
        ("elektronik", "gomulu", "donanim", "arduino", "raspberry", "mikroislemci", "robotik"),
        "electronics_vs_compe_overlap",
        0.91,
    ),
    (
        "curriculum",
        ("mufredat", "hangi ders", "ders var", "kacinci sinif", "cift anadal", "cap ", "yandal", "yuksek lisans"),
        "itu_curriculum_flexibility",
        0.92,
    ),
    (
        "entrepreneurship",
        ("girisim", "startup", "sirket kur", "cekirdek", "yatirimci", "demo day"),
        "itu_entrepreneurship_ecosystem",
        0.95,
    ),
    (
        "career",
        ("maas", "kariyer", "is bul", "istihdam", "mezun olunca", "ne kadar kazan"),
        "money_motivated_data",
        0.90,
    ),
    (
        "comparison",
        ("odtu", "bogazici", "bilkent", "sabanci", "ytu", "yildiz", "koc", "daha iyi", "kiyasla", "karsilastir"),
        "university_comparison_general",
        0.92,
    ),
    (
        "ranking",
        ("siralama", "taban", "puan", "kac bin", "yeter mi", "girer miyim", "gelir mi", "kacla kapat"),
        "itu_admission_reality",
        0.94,
    ),
    (
        "healthtech",
        ("tip mi", "doktor", "saglik teknoloj", "biyomedikal", "tibbi goruntu"),
        "med_vs_eng_health_tech",
        0.90,
    ),
    (
        "clubs_projects",
        ("kulup", "takim", "anthro", "proje takimi", "oyun yap", "unity", "hackathon"),
        "itu_clubs_projects",
        0.89,
    ),
]


_FALLBACK_TOPIC_ARGUMENTS: list[tuple[str, str]] = [
    ("curriculum_year1", "itu_first_year_curriculum"),
    ("curriculum_beginner", "itu_curriculum_beginner"),
    ("programming_languages", "itu_curriculum_details"),
    ("curriculum_systems", "itu_curriculum_details"),
    ("curriculum_ai", "itu_specialization"),
    ("curriculum_security", "itu_specialization"),
    ("curriculum_projects", "itu_curriculum_details"),
    ("academic_workload", "itu_academic_workload"),
    ("teaching_quality", "itu_faculty_research"),
    ("technical_resources", "itu_technical_resources"),
    ("internship", "itu_internship_pathways"),
    ("research_projects", "itu_research_projects"),
    ("specialization", "itu_specialization"),
    ("double_major_transfer", "itu_double_major_transfer"),
    ("erasmus", "itu_erasmus_mobility"),
    ("clubs_teams", "itu_clubs_teams"),
    ("housing_details", "itu_housing_details"),
    ("istanbul_life", "itu_istanbul_life"),
    ("student_social", "itu_clubs_teams"),
    ("student_wellbeing", "itu_student_wellbeing"),
    ("graduation", "itu_graduation_requirements"),
    ("english_prep", "itu_english_prep"),
    ("dining", "itu_dining"),
    ("financial_concern", "itu_financial_support"),
    ("financial_support", "itu_financial_support"),
    ("housing", "itu_student_life_support"),
    ("campus_life", "itu_campus_life"),
    ("faculty", "itu_faculty_research"),
    ("labs", "itu_faculty_research"),
    ("career_evidence", "itu_career_evidence"),
    ("future_of_field", "future_of_compe"),
    ("career", "money_motivated_data"),
    ("entrepreneurship", "itu_entrepreneurship_ecosystem"),
    ("software_vs_compe", "software_vs_compe"),
    ("comparison", "university_comparison_general"),
    ("differentiators", "itu_compe_differentiators"),
    ("ranking", "itu_admission_reality"),
    ("admission", "itu_admission_reality"),
    ("abroad", "itu_global_opportunities"),
    ("gamedev", "itu_clubs_projects"),
    ("healthtech", "med_vs_eng_health_tech"),
    ("candidate_fit", "ideal_match_summary"),
    ("curriculum_overview", "itu_curriculum_overview"),
    ("curriculum", "itu_curriculum_flexibility"),
]

_FALLBACK_ARGUMENT_BY_TOPIC = dict(_FALLBACK_TOPIC_ARGUMENTS)


def _is_contextual_followup(text: str, analysis: dict) -> bool:
    low = _fold(text).strip(" ?!.,")
    if low in {"ornek verir misin", "ornek verir misin nelerdir", "nelerdir", "biraz daha anlatir misin"}:
        return True
    return bool(analysis.get("wants_detail")) and len(low.split()) <= 5


def route_current_turn(
    text: str,
    analysis: dict,
    profile: CandidateProfile,
    previous_route: dict | None = None,
) -> RouteDecision:
    low = f" {_fold(text)} "
    matches: list[tuple[str, str, float]] = []
    for topic, needles, argument_id, confidence in _TOPIC_RULES:
        if any(needle in low for needle in needles):
            matches.append((topic, argument_id, confidence))

    # Analyzer concerns are useful when the wording is indirect.
    concerns = set(analysis.get("concerns_mentioned", []))
    if "employment" in concerns and not any(topic == "career_evidence" for topic, _, _ in matches):
        matches.insert(0, ("future_of_field", "future_of_compe", 0.95))
    if "family" in concerns:
        matches.insert(0, ("family", "concern_family_pressure", 0.93))
    if concerns & {"math", "difficulty", "self_efficacy"}:
        matches.insert(0, ("difficulty", "concern_math_difficulty", 0.92))
    if "cost" in concerns:
        matches.insert(0, ("financial_support", "itu_financial_support", 0.96))

    if not matches and previous_route and _is_contextual_followup(text, analysis):
        previous_topic = str(previous_route.get("primary_topic") or "general")
        previous_argument = previous_route.get("forced_argument_id")
        if not previous_argument:
            preferred = previous_route.get("preferred_arguments") or []
            previous_argument = preferred[0] if preferred else None
        if previous_argument and previous_topic != "general":
            return RouteDecision(
                primary_topic=previous_topic,
                topics=[previous_topic],
                forced_argument_id=str(previous_argument),
                preferred_arguments=[str(previous_argument)],
                confidence=0.96,
                reason=f"Kısa devam sorusu önceki '{previous_topic}' konusuna bağlandı.",
            )

    # "Yurt ve yemekhane" iki ayrı öğrenci yaşamı ihtiyacıdır; yalnızca yemek
    # kartına daraltma. Doğrudan burs veya yurt dışı sorusu varsa onların daha
    # özel yolları aşağıdaki öncelik sırasıyla yine kazanır.
    matched_topics = {topic for topic, _, _ in matches}
    if {"dining", "student_support"} <= matched_topics and not matched_topics & {
        "financial_support", "global",
    }:
        matches = [match for match in matches if match[0] != "dining"]

    if not matches:
        from ..kb.retriever import infer_query_topics

        # Fallback force yalnızca METİN sinyalinden gelir — profil-türevi topic'ler
        # (housing_needed gibi kalıcı bayraklar) güncel soruyu ele geçiremez (sess_f450).
        inferred_topics = infer_query_topics(text, profile, include_profile=False)
        for topic in inferred_topics:
            argument_id = _FALLBACK_ARGUMENT_BY_TOPIC.get(topic)
            if not argument_id:
                continue
            explicit_question = bool(
                analysis.get("asked_followup")
                or analysis.get("wants_detail")
                or "?" in text
            )
            return RouteDecision(
                primary_topic=topic,
                topics=inferred_topics,
                forced_argument_id=argument_id if explicit_question else None,
                preferred_arguments=[argument_id],
                confidence=0.91,
                reason=f"Son mesaj geniş konu eşleşmesiyle '{topic}' başlığına yönlendirildi.",
            )
        preferred = _profile_preferences(profile)
        return RouteDecision(preferred_arguments=preferred)

    # Operation-like questions outrank their subject branch: "elektronik ile
    # çift anadal" is primarily a curriculum question; "yurt dışı" is global,
    # not housing merely because it contains the token "yurt".
    topic_priority = {
        "comparison_financial_offer": 0,
        "curriculum_year1": 0,
        "curriculum_beginner": 0,
        "double_major_transfer": 0,
        "erasmus": 0,
        "graduation": 0,
        "internship": 0,
        "research_projects": 0,
        "specialization": 0,
        "curriculum_details": 0,
        "academic_workload": 0,
        "technical_resources": 0,
        "clubs_teams": 0,
        "housing_details": 0,
        "istanbul_life": 0,
        "student_social": 0,
        "student_wellbeing": 0,
        "gamedev": 0,
        "future_of_field": 0,
        "dining": 1,
        "financial_support": 2,
        "career_evidence": 2,
        "differentiators": 2,
        "campus_life": 2,
        "english_prep": 2,
        "family": 3,
        # social_life, difficulty'den ÖNCE: "bölüm yoğun, sosyal hayata zaman kalır mı?"
        # sorusu 'yoğun' kelimesiyle difficulty'ye kaçıyordu (sess_051a T9)
        "social_life": 3,
        "difficulty": 4,
        "faculty_research": 5,
        "dept_info": 5,
        "quality": 6,
        "curriculum": 6,
        "global": 7,
        "student_support": 8,
        "software_vs_compe": 8,
        "ai_vs_compe": 8,
        "electronics": 8,
        "entrepreneurship": 9,
        "career": 10,
        "comparison": 11,
        "ranking": 12,
        "healthtech": 13,
        "clubs_projects": 14,
    }
    matches.sort(key=lambda item: (topic_priority.get(item[0], 99), -item[2]))

    # Preserve rule priority while deduplicating.
    topics = list(dict.fromkeys(topic for topic, _, _ in matches))
    arguments = list(dict.fromkeys(arg for _, arg, _ in matches))
    primary_topic, primary_argument, confidence = matches[0]
    explicit_question = bool(
        analysis.get("asked_followup")
        or analysis.get("wants_detail")
        or "?" in text
        or any(q in low for q in (" nasil", " nedir", " hangisi", " var mi", " kim", " kac", " yeter mi"))
    )
    forced = primary_argument if explicit_question and confidence >= 0.90 else None
    return RouteDecision(
        primary_topic=primary_topic,
        topics=topics,
        forced_argument_id=forced,
        preferred_arguments=arguments,
        confidence=confidence,
        reason=(
            f"Son mesaj '{primary_topic}' konusuna doğrudan odaklanıyor; güncel soru profil geçmişinden öncelikli."
            if forced
            else f"Son mesaj '{primary_topic}' sinyali taşıyor; ilgili argümanlar banditte önceliklendirilecek."
        ),
    )


def _profile_preferences(profile: CandidateProfile) -> list[str]:
    ind = profile.indecision
    preferred: list[str] = []
    if "tip" in ind.field_alternatives:
        preferred.append("med_vs_eng_health_tech")
    if "koc" in ind.university_alternatives:
        preferred.append("koc_vs_itu_value")
    if ind.university_alternatives:
        preferred.append("university_comparison_general")
    if "yapay_zeka_veri" in ind.department_alternatives:
        preferred.append("ai_vs_compe_foundation")
    if any(d in ind.department_alternatives for d in ("elektronik_haberlesme", "elektrik", "kontrol_otomasyon")):
        preferred.append("electronics_vs_compe_overlap")
    dom = ind.dominant_motivation()
    if profile.constraints.cost_sensitivity is not None and profile.constraints.cost_sensitivity >= 0.5:
        preferred.append("itu_financial_support")
    if dom == "entrepreneurship":
        preferred.append("itu_entrepreneurship_ecosystem")
    elif dom in ("money", "job_security"):
        preferred.append("money_motivated_data")
    elif dom in ("science", "abroad"):
        preferred.append("itu_faculty_research")
    return list(dict.fromkeys(preferred))
