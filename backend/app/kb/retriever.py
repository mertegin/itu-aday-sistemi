"""Topic-aware, embedding'siz RAG v1.

Bu sürüm bilinçli olarak basit: kullanıcı mesajı + profil + seçilen argümandan topic
çıkarır, facts.yaml içinden en alakalı kısa fact listesini döndürür. İleride aynı
arayüzün altına embedding/Chroma eklenebilir.
"""
from dataclasses import dataclass, field
import re

from .loader import flatten_facts
from ..profile.schema import CandidateProfile


TOPIC_KEYWORDS: dict[str, list[str]] = {
    "database_course": ["veritabanı", "veri tabanı", "database", "sql"],
    "cloud_technologies": ["bulut teknoloji", "bulut bilişim", "cloud computing", "aws", "azure", "google cloud"],
    "curriculum_year1": ["ilk sınıf", "birinci sınıf", "1. sınıf", "ilk yıl", "birinci yıl", "1. yarıyıl", "2. yarıyıl"],
    "curriculum_beginner": ["sadece kod", "yalnızca kod", "kod yazmaktan", "hiç programlama", "hiç kod", "daha önce programlama", "programlama yapmadım", "kodlama bilmiyorum", "programlama bilmiyorum", "sıfırdan", "lisede yazılım", "yetenek işi", "çalışarak öğren", "diğer öğrenciler", "bilgisayarlarla", "bilgisayar başında olmak", "kodlama sınav", "üniversiteye gelmeden", "problem çözme", "zorlanır mıyım"],
    "curriculum_overview": ["ne öğretiliyor", "neler öğren", "tam olarak ne", "bölümde ne var", "hakkında bilgi", "tanıt"],
    "programming_languages": ["hangi dil", "programlama dili", "python", "java", "c++", "c dili", "kodlama dili"],
    "curriculum_systems": ["işletim sistemi", "bilgisayar mimarisi", "mikroişlemci", "devre tasarım", "sistem programlama", "veri yapıları", "algoritma"],
    "curriculum_ai": ["yapay zeka dersi", "makine öğrenmesi", "veriden öğrenme", "deep learning", "llm", "üretken yapay zeka"],
    "curriculum_security": ["siber güvenlik", "bilgisayar güvenliği", "ağ güvenliği", "güvenli programlama", "kriptografi"],
    "curriculum_projects": ["bitirme projesi", "tasarım projesi", "grup projesi", "ders projesi", "uygulamalı proje", "ödevler proje"],
    "academic_workload": ["ders yükü", "haftada kaç saat", "kaç saat çalış", "sınav sistemi", "sınav hafta", "sınavlarda kod", "aynı haftada", "vize", "final", "çan eğrisi", "not ortalama", "geçmiş sınav", "ofis saat", "üst sınıflar", "öğrenciler birbirine", "en zor sınıf", "ödevler", "notlandırma", "kalma oranı", "çok teorik", "ezber", "ödev yoğun", "uyumaya vakit", "yorucu taraf"],
    "teaching_quality": ["eğitim kalitesi", "hocalar iyi", "ders anlat", "hocaların ingilizcesi", "hocalar ingilizce", "ingilizce ders anlat", "dersleri anlayabilir", "dersi anlam", "ders içerikleri güncel", "müfredat güncel", "müfredat ne sıklıkla", "müfredatı ne sıklıkla", "güncel teknoloji", "eski teknoloji", "öğrenci geri bildirim", "sektör deneyimi", "sektörel deneyim", "sınıflar kalabalık", "dersler slayttan", "slayttan işlen", "slayttan mı işlen", "çoğunlukla slayt", "slayt ağırlıklı"],
    "technical_resources": ["bilgisayar laboratuvar", "robotik laboratuvar", "robotik lab", "laboratuvarlardaki bilgisayar", "bilgisayarlar güncel", "teknik imkan", "sunucu", "gpu", "ekipman", "ekipman ödünç", "cihaz ödünç", "proje ekipmanı", "laboratuvar eriş", "kütüphane", "çalışma alanı", "sessiz alan", "uygun alan", "kendi bilgisayar", "güçlü bilgisayar", "bilgisayara ihtiyac", "bilgisayar başında çalış", "macbook", "linux", "github student", "ücretsiz yazılım lisans", "yazılım lisansı", "office 365", "matlab", "internet hızlı"],
    "internship": ["staj zorunlu", "staj kaç gün", "staj süresi", "stajda ne", "staj nasıl", "staj raporu", "online staj", "uzaktan staj"],
    "research_projects": ["araştırma projesi", "hocayla proje", "hocayla araştırma", "lisans araştırma", "lisans öğrencisi", "tübitak", "yayın yap", "laboratuvara katıl", "proje geliştirmek", "proje yarışma", "projeler yarışma", "yarışmalara gönder", "akademisyen olmak", "akademik kariyer", "araştırmacı olmak"],
    "specialization": ["uzmanlaş", "seçmeli ders", "hangi alan", "alan seç", "robotik alan", "gömülü sistem", "bilgisayarlı görü", "görüntü işleme", "web geliştirme", "bulut teknoloji", "kuantum bilişim", "oyun geliştirme"],
    "double_major_transfer": ["çift anadal", "çap ", "çap yap", "yandal", "yatay geçiş", "bölüm değiştir", "başka bölüme geç", "ikinci diploma"],
    "erasmus": ["erasmus", "değişim program", "erasmus staj", "erasmus bursu", "erasmus hibesi", "hibe yeterli", "hangi ülke", "hangi üniversite", "hangi üniversitelere gid", "erasmus dil sınavı", "dil sınavı zor", "yurt dışında dönem"],
    "global_exchange": ["global exchange", "amerika'da değişim", "amerikada değişim", "amerika değişim", "abd'de değişim", "abd de değişim", "abd değişim", "amerika çift diploma", "abd çift diploma"],
    "clubs_teams": ["kulüp", "kulübü", "öğrenci kulüb", "öğrenci takımı", "proje takımı", "yarışmalara katıl", "spor takımı", "teknik gezi", "konser", "festival", "bahar şenlik", "hackathon", "acm", "gdg", "datathon"],
    "worship_facilities": ["cami", "mescit", "namaz", "ibadet", "ibadethane"],
    "housing_details": ["yurt fiyat", "yurt ücreti", "yurt kapasite", "kaç kişilik oda", "yurt internet", "yurtta internet", "yurtta mutfak", "yurt çıkar", "yurt çıkma", "yemek yapma", "ev kirala", "hangi semt", "ev arkadaşı", "özel yurt", "eve çık", "yurt başvuru"],
    "istanbul_life": ["istanbul'da", "istanbulda", "ankara'da", "ankarada", "ulaşım", "metro", "trafik", "şehir pahalı", "öğrenci olmak çok pahalı", "aylık ortalama", "şehir merkez", "hafta sonu", "hafta sonları", "deprem", "güvenli mi", "aileden uzakta", "başka şehirden", "taksim", "levent"],
    "student_social": ["öğrenci profili", "arkadaş ortamı", "rekabetçi", "aşırı rekabet", "dayanışma", "sosyal çevre", "arkadaş edin", "bölüm öğrencilerine", "herkes çok çalışkan", "notlarını paylaş", "kız ve erkek", "öğrencileri sosyal", "öğrenciler mutlu", "inek öğrenci", "sinema kulüb", "maç izle", "dünya kupası", "bestra", "pizza", "genel olarak ortam", "bölüm ortamı", "fakülte ortamı", "öğrenci ortamı", "ortam nasıl"],
    "student_wellbeing": ["yalnız", "uyum sağlay", "psikolojik", "kaygı", "stres", "tükenmiş", "başarısız olduğumda", "toparlayabilir", "zorbalık", "dışlanma", "sunum yapmaktan", "grup çalışmalarında", "hem başarılı hem mutlu", "dâhi", "dahi olmak", "daha zeki", "bunal", "pişman", "psikolojik destek", "danışmanlık"],
    "graduation": ["mezuniyet şart", "mezun olmak", "kaç kredi", "kaç akts", "erken mezun", "dört yılda", "4 yılda", "okulu uzat", "okulun uzaması", "üç buçuk yılda", "azami süre", "yaz okulu", "bütünleme"],
    "admission": ["kabul şart", "tercih süreci", "kontenjan", "yatay geçiş"],
    "ranking": ["sıra", "sıralama", "taban", "puan", "kaç gelir", "kaç bin", "girer", "risk",
                "kaçıncı sıra", "tercih listesi", "tercih listem", "ihtimal", "şans", "yazmalı"],
    "curriculum": ["ders", "müfredat", "kaçıncı sınıf", "program", "çap", "çift anadal", "yandal",
                   "hakkında bilgi", "tanıt", "ne öğretiliyor", "neler yapar", "neler öğren", "anlat",
                   "hazırlık", "yeterlik", "atlama", "ingilizce"],
    "faculty": ["hoca", "hocala", "öğretim üyesi", "akademik kadro", "akademisyen", "kim çalışıyor", "bölümde kim", "profesör", "danışman", "e-posta", "mail", "iletişim", "ulaşılabilir"],
    "student_experience": ["öğrenci deneyimi", "öğrenciler nerede", "nerede sosyalleş", "güzel yemek", "doyurucu", "danışman hoca", "akademik danışman", "mail", "e-posta", "iletişim", "ulaşılabilir"],
    "labs": ["lab", "laboratuvar", "araştırma", "çalışan hoca", "sağlık bilişimi", "biyoinformatik", "nlp", "doğal dil", "yapay zeka", "veri bilimi", "computer vision", "robotik"],
    "career": ["iş", "kariyer", "maaş", "mezun", "istihdam", "işsiz", "sektör", "part-time", "freelance", "para kazanmaya", "teknokentte öğrenci", "savunma sanayi", "işverenler"],
    "career_evidence": ["mezun olmadan", "mezuniyetten önce", "işe başla", "kariyer zirvesi", "şirket", "firma", "staj", "işveren ilgisi"],
    "entrepreneurship": ["çekirdek", "girişim", "startup", "yatırımcı", "demo day", "şirket", "kuluçka", "şirketleş", "fonlama"],
    "campus": ["kampüs", "kulüp", "takım", "sosyal", "sosyal hayat", "sosyal yaşam", "yemekhane", "maslak"],
    "campus_life": ["hangi kampüs", "ayazağa", "maslak", "kampüste ne var", "kampüste kaybol", "kampüs 24", "kampüste kafe", "spor salon", "kampüsü gez", "sosyal alan", "spor tesisi", "kütüphane", "stadyum", "yüzme havuzu", "gölet", "metro"],
    "dining": ["yemekhane", "yemek ücreti", "yemek fiyatı", "yemek fiyatları", "yemek seçenek", "menü", "öğle yemeği", "akşam yemeği", "vejetaryen", "ne yenir"],
    "english_prep": ["hazırlık", "hazırlığı bir dönemde", "yeterlik", "proficiency", "muafiyet", "atlama", "toefl", "pte"],
    "differentiators": ["diğer üniversitelerden fark", "farkı", "ne kazanırım", "eşsiz", "neden itü", "neden başka", "en güçlü yön", "en büyük eksik", "kötü taraf", "dışarıdan görünmeyen", "en keyifli", "gerçekten mantıklı", "tekrar tercih", "avantaj", "her okul", "tüm okullar", "diğer güçlü okul", "güçlü okullardan", "ayıran şey"],
    "candidate_fit": ["sevdiğimi nasıl", "sevip sevmediğimi", "nasıl biri olmak", "yaratıcı birine", "burada başarılı", "iyi bir yazılımcı olabilir", "gelmek gerçekten mantıklı", "kendimi okul dışında", "öğrenciler gerçekten mutlu", "sadece matematiği", "gelmeden önce bilmem", "gelir gelmez ne yap"],
    "housing": ["yurt", "barınma", "konaklama", "garanti"],
    "scholarship": ["burs", "ücret", "ücretsiz", "tam burs", "aylık", "maliyet", "para desteği", "başarı ödülü", "ilk tercih bursu"],
    "financial_support": ["burs", "maddi", "para sıkınt", "geçinem", "karşılayam", "ödeyem", "bütçe", "ekonomik", "masraf", "destek var mı"],
    "financial_concern": ["para sıkınt", "maddi durum", "maddi kayg", "geçinem", "karşılayam", "ödeyem", "bütçem", "ekonomik durum", "ailem karşılayamaz"],
    "comparison": ["odtü", "koç", "boğaziçi", "bilkent", "sabancı", "yıldız", "ytü", "karşılaştır", "diğer üniversitelere göre", "qs", "daha iyi", "fark",
                   "kalite", "kaliteli", "gerçekten iyi", "değer mi", "memnun"],
    "gamedev": ["oyun", "unity", "game", "harita", "oyun teknolojileri", "otg"],
    "healthtech": ["tıp", "doktor", "sağlık", "biyomedikal", "tıbbi"],
    "abroad": ["yurt dışı", "yurtdışı", "erasmus", "cern", "abd", "almanya", "çift diploma"],
    "software_vs_compe": ["yazılım mühendisliği", "yazılım müh", "software engineering", "yazılım bölümü", "yazılımcılık bölümü"],
    "future_of_field": ["gelecek", "geleceği", "işimizi alacak", "işini elinden", "beş yıl sonra", "işsiz kalır", "işleri alacak", "yapay zeka gelişti", "otomasyonla", "meslek ölür", "bitecek mi", "maaşlar gelecekte", "gelecekte düşer"],
}

ARGUMENT_TOPICS: dict[str, list[str]] = {
    "rank_probe": ["ranking"],
    "compe_priority_top1000": ["ranking", "curriculum", "career", "faculty", "labs"],
    "compe_borderline_1000_1500": ["ranking"],
    "med_vs_eng_health_tech": ["healthtech", "labs", "career"],
    "koc_vs_itu_value": ["comparison", "scholarship", "housing", "campus"],
    "ai_vs_compe_foundation": ["curriculum", "labs", "ranking"],
    "electronics_vs_compe_overlap": ["curriculum", "curriculum_systems", "curriculum_overview", "specialization", "labs", "campus"],
    "money_motivated_data": ["career", "career_evidence", "future_of_field"],
    "itu_financial_support": ["financial_support", "financial_concern", "scholarship", "housing", "campus"],
    "itu_entrepreneurship_ecosystem": ["entrepreneurship", "career"],
    "science_motivated_labs": ["labs", "faculty", "research_projects", "abroad"],
    "itu_faculty_research": ["labs", "faculty", "teaching_quality", "technical_resources"],
    "itu_curriculum_flexibility": ["curriculum", "double_major_transfer", "graduation", "specialization"],
    "itu_first_year_curriculum": ["curriculum_year1", "curriculum"],
    "itu_curriculum_beginner": ["curriculum_beginner", "curriculum_year1", "curriculum"],
    "itu_curriculum_overview": ["curriculum_overview", "curriculum"],
    "itu_curriculum_details": ["database_course", "programming_languages", "curriculum_systems", "curriculum_ai", "curriculum_security", "curriculum_projects", "curriculum"],
    "itu_academic_workload": ["academic_workload", "curriculum", "student_wellbeing"],
    "itu_technical_resources": ["technical_resources", "labs", "campus_life"],
    "itu_internship_pathways": ["internship", "career_evidence", "curriculum_projects"],
    "itu_research_projects": ["research_projects", "labs", "faculty"],
    "itu_specialization": ["cloud_technologies", "specialization", "curriculum_ai", "curriculum_security", "labs"],
    "itu_double_major_transfer": ["double_major_transfer", "curriculum", "admission"],
    "itu_erasmus_mobility": ["erasmus", "abroad", "internship"],
    "itu_clubs_teams": ["clubs_teams", "student_social", "research_projects"],
    "itu_social_venues": ["student_social", "campus_life", "dining", "clubs_teams"],
    "itu_worship_facilities": ["worship_facilities"],
    "itu_housing_details": ["housing_details", "housing", "financial_concern"],
    "itu_istanbul_life": ["istanbul_life", "campus_life", "career"],
    "itu_student_wellbeing": ["student_wellbeing", "student_social", "campus_life"],
    "itu_graduation_requirements": ["graduation", "curriculum_projects", "curriculum"],
    "itu_student_life_support": ["scholarship", "housing", "campus"],
    "itu_campus_life": ["campus_life", "campus"],
    "itu_dining": ["dining", "financial_concern", "scholarship"],
    "itu_career_evidence": ["career_evidence", "career"],
    "itu_english_prep": ["english_prep", "curriculum"],
    "itu_compe_differentiators": ["differentiators", "comparison", "faculty", "career_evidence"],
    "itu_global_opportunities": ["abroad", "global_exchange", "erasmus", "research_projects", "curriculum", "career", "career_evidence"],
    "itu_clubs_projects": ["clubs_teams", "student_social", "research_projects", "campus_life", "campus", "gamedev", "labs"],
    "itu_admission_reality": ["ranking", "admission"],
    "concern_math_difficulty": ["academic_workload", "student_wellbeing", "curriculum"],
    "concern_family_pressure": ["career", "comparison"],
    "balanced_perspective": ["comparison", "ranking"],
    "ideal_match_summary": ["candidate_fit", "curriculum", "career", "career_evidence", "faculty", "labs"],
    "software_vs_compe": ["software_vs_compe", "curriculum_projects", "curriculum_overview", "curriculum"],
    "university_comparison_general": ["comparison", "differentiators", "ranking", "scholarship"],
    "future_of_compe": ["future_of_field", "career", "career_evidence"],
}


EVIDENCE_TOPICS = {
    "campus_life", "dining", "career_evidence", "english_prep", "differentiators",
    "database_course", "cloud_technologies",
    "curriculum_year1", "curriculum_beginner", "curriculum_overview", "programming_languages",
    "curriculum_systems", "curriculum_ai", "curriculum_security", "curriculum_projects",
    "academic_workload", "teaching_quality", "technical_resources", "internship", "research_projects",
    "specialization", "double_major_transfer", "erasmus", "clubs_teams", "housing_details",
    "istanbul_life", "student_social", "student_wellbeing", "graduation", "ranking", "admission",
    "abroad", "global_exchange", "comparison", "career", "candidate_fit", "worship_facilities",
}


@dataclass
class RetrievedFact:
    id: str
    text: str
    label: str = ""
    source: str = ""
    source_url: str = ""
    source_urls: list[str] = field(default_factory=list)
    profile_url: str = ""
    email: str = ""
    year: str | int = ""
    confidence: str = "medium"
    topics: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    answer_card: bool = False
    applicable: bool = True
    score: float = 0.0

    def prompt_line(self) -> str:
        source = f"{self.source} {self.year}".strip() or "kaynak belirtilmemiş"
        note = "yaklaşık/topluluk verisi" if self.confidence == "low" else self.confidence
        claims = self.claims()
        lines = [f"KANIT {self.id} | güven={note} | kaynak={source}"]
        lines.extend(f"  - iddia: {claim}" for claim in claims)
        if self.examples:
            lines.append(f"  - kullanılabilir örnekler: {', '.join(self.examples[:6])}")
        return "\n".join(lines)

    def claims(self) -> list[str]:
        """Expose answer cards as evidence claims instead of ready-made replies."""
        parts = [
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", self.text.strip())
            if part.strip()
        ]
        return parts or [self.text.strip()]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "text": self.text,
            "source": self.source,
            "source_url": self.source_url,
            "source_urls": self.source_urls,
            "profile_url": self.profile_url,
            "email": self.email,
            "year": self.year,
            "confidence": self.confidence,
            "topics": self.topics,
            "examples": self.examples,
            "answer_card": self.answer_card,
            "applicable": self.applicable,
            "score": round(self.score, 3),
        }


@dataclass
class RagResult:
    query_topics: list[str]
    facts: list[RetrievedFact]
    allowed_numbers: list[str] = field(default_factory=list)

    def prompt_block(self) -> str:
        if not self.facts:
            return (
                "Bu tur için kaynaklı fact bulunamadı. Sayı, garanti, bölüm adı veya kesin iddia verme; "
                "karar çerçevesi sun ve gerekirse resmi kaynaktan doğrulamayı öner."
            )
        lines = [
            "Aşağıdaki içerik bir KANIT PAKETİDİR; hazır cevap metni değildir.",
            "Kartın tamamını veya art arda iki cümlesini aynen kopyalama. İlgili iddiaları seçip doğal bir cevap kur.",
            "Sayı/kontenjan/sıralama/program/garanti iddialarında SADECE bu maddeleri kullan.",
            "Bu maddelerde olmayan kesin bilgiyi uydurma; 'net kaynaklı bilgi yok' diye çerçevele.",
            "",
        ]
        if "financial_support" in self.query_topics or "financial_concern" in self.query_topics:
            lines.append(
                "Burs yanıtında kaynak yılını ve varsa sıralama, ilk tercih, GNO/hazırlık koşullarını söyle; "
                "ihtiyaç bursunda kaynakta olmayan bir tutar veya herkese garanti verme."
            )
        if "entrepreneurship" in self.query_topics:
            lines.append(
                "Ekosistem toplamlarını kişisel yatırım garantisi gibi sunma; başvuru, kabul, şirketleşme ve yatırımın ayrı aşamalar olduğunu koru."
            )
        if set(self.query_topics) & EVIDENCE_TOPICS:
            lines.append(
                "Bu soru için genel sıfatlarla yetinme: kanıt paketindeki en az bir sayıyı ve adlandırılmış bir somut örneği kısa cevapta kullan."
            )
        if any("öğrenci geri bildirimi" in f.source.lower() for f in self.facts):
            lines.append(
                "'Öğrenci geri bildirimi' kaynaklı maddeleri resmi kurum verisi gibi sunma; öğrenci deneyimine göre olduğunu açıkça belirt."
            )
        lines.extend(f.prompt_line() for f in self.facts)
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "topics": self.query_topics,
            "allowed_numbers": self.allowed_numbers,
            "facts": [f.to_dict() for f in self.facts],
            "evidence_packet": [
                {
                    "id": fact.id,
                    "claims": fact.claims(),
                    "examples": fact.examples,
                    "source": fact.source,
                    "year": fact.year,
                    "confidence": fact.confidence,
                }
                for fact in self.facts
                if fact.applicable
            ],
        }


def retrieve_facts(
    user_text: str,
    profile: CandidateProfile,
    argument_id: str,
    max_facts: int = 6,
) -> RagResult:
    topics = infer_query_topics(user_text, profile, argument_id)
    folded_query = _fold(user_text)
    direct_topics = {
        topic for topic, words in TOPIC_KEYWORDS.items()
        if any(_keyword_matches(word, folded_query) for word in words)
    }
    query_terms = _tokens(user_text)
    # Kalıcı AI/robotik ilgisi yalnız hoca-lab sorusunda kişiselleştirme sinyali
    # olsun. Aksi halde önceki "AI ilgim var" bilgisi girişimcilik, kıyaslama ve
    # kampüs sorularında faculty kartlarını haksız biçimde üste taşıyor.
    explicit_focus_terms = _focus_terms(user_text, profile, include_profile=False)
    focus_terms = explicit_focus_terms or _focus_terms(
        user_text,
        profile,
        include_profile=bool(direct_topics & {"faculty", "labs"}),
    )
    scored: list[RetrievedFact] = []

    for raw in flatten_facts():
        fact_topics = raw.get("topics", [])
        text = raw.get("text", "")
        tags = raw.get("tags", [])
        score = 0.0

        overlap_topics = set(topics) & set(fact_topics)
        score += 5.0 * len(overlap_topics)
        if raw.get("answer_card") and overlap_topics and set(topics) & EVIDENCE_TOPICS:
            score += 9.0

        hay_tokens = set(_tokens(" ".join([text, " ".join(tags), " ".join(fact_topics)])))
        score += 0.8 * len(set(query_terms) & hay_tokens)
        folded_text = _fold(text)
        raw_id = raw.get("id", "")
        if raw_id.startswith("admission_") and not direct_topics & {"ranking", "admission"}:
            score -= 100.0

        support_type = raw.get("support_type")
        financial_query = bool(set(topics) & {"financial_support", "financial_concern", "scholarship"})
        if financial_query and support_type:
            score += 5.0
            asks_amount = any(
                phrase in _fold(user_text)
                for phrase in ("ne kadar", "kac tl", "aylik", "tutar", "miktar")
            )
            if asks_amount and support_type == "merit_cash":
                score += 7.0
            if "financial_concern" in topics and support_type in ("need_based", "meal"):
                score += 9.0
            elif profile.yks_rank is None and support_type in ("need_based", "first_choice"):
                score += 4.0

        rank_min = raw.get("rank_min")
        rank_max = raw.get("rank_max")
        rank_restricted = rank_min is not None and rank_max is not None
        rank_applicable = not rank_restricted or (
            profile.yks_rank is not None
            and int(rank_min) <= profile.yks_rank <= int(rank_max)
        )
        if profile.yks_rank is not None and rank_min is not None and rank_max is not None:
            rank_matches = int(rank_min) <= profile.yks_rank <= int(rank_max)
            if financial_query:
                score += 14.0 if rank_matches else -6.0
            elif "entrepreneurship" in topics and rank_matches:
                score += 6.0
        if financial_query and rank_restricted and not rank_applicable:
            score -= 10.0

        # Sıralama biliniyorsa burs sorusunun ilk cevabı yan imkanlar değil,
        # doğrudan o dilime ait nakit tutarı olmalı (sess_1329 regresyonu).
        if profile.yks_rank is not None and financial_query and support_type == "merit_cash":
            score += 6.0

        if raw.get("requires_first_choice") and any(
            phrase in _fold(user_text) for phrase in ("ilk tercih", "birinci tercih", "1 tercih")
        ):
            score += 5.0

        focus_overlap = set(focus_terms) & hay_tokens
        if focus_overlap:
            score += 2.5 * len(focus_overlap)
            if raw_id.startswith("faculty_area_"):
                score += 4.0
            elif raw_id.startswith("faculty_") and raw.get("profile_url"):
                score += 5.0

        if "ranking" in topics and any(w in folded_text for w in ("taban", "sira", "siralam", "yks", "say", "puan")):
            score += 6.0
        if "bilgisayar" in _fold(user_text) and "bilgisayar" in folded_text:
            score += 1.0

        # Hoca/lab sorularında resmi akademik kadro/lab maddeleri öne çıksın.
        if "faculty" in topics and ("öğretim" in text.lower() or "akademik" in text.lower()):
            score += 4.0
        if "labs" in topics and ("laboratuvar" in text.lower() or "araştırma" in text.lower()):
            score += 3.0
        # Karşılaştırma sorusunda İTÜ'nün ana kartları (QS + karşılaştırma önceliği yönergesi) öne çıksın.
        if "comparison" in topics and ("qs" in text.lower() or "karşılaştırma önceliği" in text.lower()):
            score += 4.0
        if "entrepreneurship" in topics and raw_id.startswith("itu_cekirdek_"):
            score += 7.0
        if "campus_life" in topics and raw_id.startswith("campus_"):
            score += 6.0
        if "worship_facilities" in direct_topics and raw_id == "campus_worship_facilities_card":
            score += 90.0
        if "worship_facilities" not in direct_topics and raw_id == "campus_worship_facilities_card":
            score -= 100.0
        if raw_id == "campus_cinema_match_viewing_card" and any(
            _keyword_matches(phrase, folded_query) for phrase in ("sinema", "mac izle", "dunya kupasi", "bestra", "televizyon")
        ):
            score += 70.0
        if raw_id == "campus_food_shopping_official_card" and any(
            _keyword_matches(phrase, folded_query) for phrase in ("pizza", "market", "migros", "a101", "sok", "kampuste yemek")
        ):
            score += 70.0
        if raw_id == "campus_official_daily_life_card" and any(
            _keyword_matches(phrase, folded_query) for phrase in ("stadyum", "golet", "havuz", "metro", "kampuste ne var")
        ):
            score += 65.0
        if "dining" in topics and raw_id.startswith("dining_"):
            score += 6.0
        if "career_evidence" in topics and raw_id.startswith("career_"):
            score += 6.0
        if "career_evidence" in topics and raw_id == "career_employment_companies_card":
            score += 8.0
        if "english_prep" in topics and raw_id.startswith("prep_"):
            score += 6.0
        if "differentiators" in topics and raw_id.startswith("differentiator_"):
            score += 6.0
        if "gamedev" in direct_topics and raw_id == "game_tech_grad_program":
            score += 14.0
        if "gamedev" in direct_topics and raw_id == "department_clubs_teams_card":
            score += 32.0
        if "gamedev" in direct_topics and raw_id == "game_interest_fit_card":
            score += 70.0
        if raw_id == "campus_student_social_food_spots_2026" and any(
            phrase in folded_query for phrase in ("sosyal alan", "takilacak yer", "arkadas edin", "nerede sosyalles", "ornek verir")
        ):
            score += 36.0
        if raw_id == "differentiator_faculty_access_and_advising_2026" and any(
            phrase in folded_query for phrase in ("mail", "e-posta", "danisman", "ulas", "iletisim")
        ):
            score += 45.0
        if raw_id == "insider_faculty_interest_card" and "hoca" in folded_query and "ilgili" in folded_query:
            score += 55.0
        if raw_id == "ai_faculty_lab_answer_card" and any(
            phrase in folded_query for phrase in ("yapay zeka", "ai ", "makine ogren")
        ) and any(term in folded_query for term in ("hoca", "laboratuvar", "lab")):
            score += 95.0
        if raw_id == "comparison_bilkent_honesty_card" and "bilkent" in folded_query:
            score += 90.0
        if raw_id == "comparison_difficulty_honesty_card" and any(
            phrase in folded_query for phrase in ("diger universitelere gore", "egitimi daha mi zor", "itu cok zor")
        ):
            score += 95.0
        direct_priority_cards = {
            "curriculum_database_practice_card": ("veritabani", "veri tabani", "database", "sql"),
            "cloud_technologies_honesty_card": ("bulut teknoloji", "bulut bilisim", "cloud computing", "aws", "azure", "google cloud"),
            "faculty_industry_experience_honesty_card": ("sektorel deneyim", "sektor deneyimi", "hocalar sektorden"),
            "curriculum_modernity_answer_card": ("ders icerikleri guncel", "mufredat guncel", "guncel teknoloji", "eski teknoloji"),
            "student_software_licenses_answer_card": ("ucretsiz yazilim lisans", "yazilim lisansi", "github student", "office 365", "matlab lisans"),
            "robotics_lab_access_answer_card": ("robotik laboratuvar", "robotik lab"),
            "erasmus_grant_sufficiency_answer_card": ("erasmus bursu yeterli", "erasmus hibesi yeterli", "hibe yeterli", "erasmus bursu ne kadar"),
            "global_exchange_america_honesty_card": ("amerika'da degisim", "amerikada degisim", "amerika degisim", "abd'de degisim", "abd de degisim", "abd degisim", "amerika cift diploma", "abd cift diploma"),
            "worship_exam_policy_honesty_card": ("ramazanda sinav", "sinavda namaz", "namaz izni", "oruc sinav"),
            "lab_computer_currency_honesty_card": ("laboratuvarlardaki bilgisayar", "bilgisayarlar guncel", "son model bilgisayar"),
            "ai_gpu_access_honesty_card": ("gpu destegi", "gpu erisimi", "yapay zeka gpu", "gpu sunucu"),
            "erasmus_compe_partner_examples_card": ("hangi universitelere gid", "bilgisayar muhendisligi erasmus", "erasmus universiteleri"),
            "erasmus_language_requirement_card": ("erasmus dil sinavi", "dil sinavi zor", "erasmus ingilizce"),
            "curriculum_update_frequency_honesty_card": ("mufredat ne siklikla", "mufredati ne siklikla", "mufredat ne zaman guncellen", "mufredati ne zaman guncellen", "her yil yenilen"),
            "equipment_loan_honesty_card": ("ekipman odunc", "cihaz odunc", "proje ekipmani"),
            "academic_career_support_card": ("akademisyen olmak", "akademik kariyer", "arastirmaci olmak"),
            "teaching_materials_honesty_card": ("dersler slayttan", "slayttan islen", "slayttan mi islen", "cogunlukla slayt", "slayt agirlikli"),
            "differentiator_qs_abet_faculty_card": ("diger guclu okul", "guclu okullardan", "ayiran sey"),
        }
        if raw_id in direct_priority_cards and any(
            _keyword_matches(phrase, folded_query) for phrase in direct_priority_cards[raw_id]
        ):
            score += 95.0
        competitor_cards = {
            "admission_koc_compe_full_2025_direct": ("koc", "tam burs", "%100 burs"),
            "admission_ytu_compe_2025_direct": ("ytu", "yildiz teknik"),
            "admission_itu_ai_data_2025_direct": ("yapay zeka ve veri", "veri muhendis", "yzv"),
            "admission_itu_compe_2025_direct": ("itu bilgisayar", "bilgisayar gelir", "bilgisayara gir"),
        }
        if raw_id in competitor_cards and any(
            _keyword_matches(phrase, folded_query) for phrase in competitor_cards[raw_id]
        ):
            score += 75.0
        exact_cards = {
            "curriculum_database_practice_card": ("veritabani", "veri tabani", "database", "sql"),
            "cloud_technologies_honesty_card": ("bulut teknoloji", "bulut bilisim", "cloud computing", "aws", "azure", "google cloud"),
            "insider_faculty_interest_card": ("hocalar ilgili", "hocalari ilgili", "ogrencilere karsi ilgili", "ogrencilerle ilgilen", "hoca destegi"),
            "insider_teaching_english_card": ("hocalarin ingilizcesi", "hocalar ingilizce", "ingilizce ders anlat", "dersleri anlayabilir", "dersi anlam", "hocalar dersleri anlasilir", "dersleri anlasilir anlat", "anlasilir anlatiyor"),
            "insider_lab_access_card": ("laboratuvara gire", "laboratuvarlara ders disinda", "laboratuvara ders disinda", "laboratuvara hoca", "lab erisim", "hoca izni", "hocadan izin", "hocayla calis"),
            "insider_dorm_life_card": ("yurt internet", "yurtlarda internet", "yurtta internet", "yurtlarda mutfak", "yurtta mutfak", "oda secenek", "kac kisilik oda", "oda yasami"),
            "insider_dorm_probability_card": ("yurt cikar", "yurt cikma", "yurt garanti"),
            "insider_exam_curve_card": ("sinavlar ayni hafta", "sinav hafta", "iki gun ara", "can sistemi", "can egrisi", "vize final"),
            "insider_course_failure_curve_card": ("dersten kalma orani", "can guzel", "kalma dusuk", "can dagilimi"),
            "insider_four_year_graduation_estimate_card": ("dort yilda mezun", "4 yilda mezun", "mezuniyet orani", "kac kisi uzat"),
            "insider_employment_outcome_card": ("yuzde 70 is", "is bulma orani", "mezuniyet sonrasi is"),
            "insider_current_tech_teams_card": ("iha takimi", "uydu takimi", "teknofest", "uzay takimi"),
            "curriculum_exam_coding_card": ("sinavlarda kod", "sinavda kod", "kod yazmamiz isten", "kagitta kod", "programlama sinavi"),
            "curriculum_algorithms_difficulty_card": ("algoritma dersleri cok zor", "algoritma dersi cok zor", "algoritma dersi zor", "algoritma analizi zor", "algoritmadan kal"),
            "curriculum_language_card": ("python", "java", "c++", "c dili", "programlama dili"),
            "curriculum_study_habits_card": ("dersleri duzenli takip", "dersi duzenli takip", "takip etmek yeterli", "derse gitmek yeterli"),
            "curriculum_capstone_process_card": ("bitirme projesi nasil", "bitirme projesi sec", "proje danismani", "tasarim projesi nasil"),
            "insider_faculty_course_support_card": ("ders destegi", "hocadan destek", "konuyu anlamadim", "ders icin hocaya"),
            "housing_application_path_card": ("kalacak yerim yok", "nasil ayarlarim", "yurt basvuru", "yurda nasil"),
            "game_interest_fit_card": ("bilgisayar oyunu", "oyun oynamayi sevmek", "oyun sevmek", "bolum icin yeterli"),
            "internship_requirements_card": ("zorunlu staj", "staj zorunlu", "kac gun", "staj suresi"),
            "double_major_minor_card": ("cift anadal", "cap ", "cap ve", "yandal"),
            "erasmus_course_recognition_card": ("dersler sayil", "ders saydir", "ola", "taninma"),
            "undergraduate_research_card": ("lisans arastirma", "lisans ogrencisi", "hocayla arastirma", "hocayla proje"),
            "student_profile_honesty_card": (
                "ogrenci profili", "rekabetci", "dayanisma", "arkadas ortami",
                "genel olarak ortam", "bolum ortami", "fakulte ortami", "ogrenci ortami", "ortam nasil",
            ),
            "psychological_support_card": ("psikolojik", "yalniz", "kaygi", "bunal", "stres"),
            "graduation_requirements_card": ("mezuniyet", "mezun olmak", "kac akts", "kac kredi", "azami sure"),
            "academic_recovery_honesty_card": ("dersten kal", "notlarim dusuk", "dunyanin sonu"),
            "career_guidance_card": ("kime danis", "kariyer konusunda kararsiz", "kariyer gunleri"),
            "project_competition_honesty_card": ("projeler yarism", "yarismalara gonder", "proje yarismasi"),
            "future_salary_ai_honesty_card": ("maaslar gelecekte", "gelecekte duser", "maas duser", "yapay zeka isimizi"),
            "faculty_industry_experience_honesty_card": ("sektorel deneyim", "sektor deneyimi", "hocalar sektorden"),
            "curriculum_modernity_answer_card": ("ders icerikleri guncel", "mufredat guncel", "guncel teknoloji", "eski teknoloji"),
            "student_software_licenses_answer_card": ("ucretsiz yazilim lisans", "yazilim lisansi", "github student", "office 365", "matlab lisans"),
            "robotics_lab_access_answer_card": ("robotik laboratuvar", "robotik lab"),
            "erasmus_grant_sufficiency_answer_card": ("erasmus bursu yeterli", "erasmus hibesi yeterli", "hibe yeterli"),
            "global_exchange_america_honesty_card": ("amerika'da degisim", "amerikada degisim", "amerika degisim", "abd'de degisim", "abd de degisim", "abd degisim", "amerika cift diploma", "abd cift diploma"),
            "worship_exam_policy_honesty_card": ("ramazanda sinav", "sinavda namaz", "namaz izni", "oruc sinav"),
            "lab_computer_currency_honesty_card": ("laboratuvarlardaki bilgisayar", "bilgisayarlar guncel", "son model bilgisayar"),
            "ai_gpu_access_honesty_card": ("gpu destegi", "gpu erisimi", "yapay zeka gpu", "gpu sunucu"),
            "erasmus_compe_partner_examples_card": ("hangi universitelere gid", "bilgisayar muhendisligi erasmus", "erasmus universiteleri"),
            "erasmus_language_requirement_card": ("erasmus dil sinavi", "dil sinavi zor", "erasmus ingilizce"),
            "curriculum_update_frequency_honesty_card": ("mufredat ne siklikla", "mufredati ne siklikla", "mufredat ne zaman guncellen", "mufredati ne zaman guncellen", "her yil yenilen"),
            "equipment_loan_honesty_card": ("ekipman odunc", "cihaz odunc", "proje ekipmani"),
            "academic_career_support_card": ("akademisyen olmak", "akademik kariyer", "arastirmaci olmak"),
            "teaching_materials_honesty_card": ("dersler slayttan", "slayttan islen", "slayttan mi islen", "cogunlukla slayt", "slayt agirlikli"),
            "differentiator_qs_abet_faculty_card": ("diger guclu okul", "guclu okullardan", "ayiran sey"),
        }
        if raw_id in exact_cards and any(_keyword_matches(phrase, folded_query) for phrase in exact_cards[raw_id]):
            is_direct_answer = raw_id.startswith("insider_") or raw_id in {
                "curriculum_exam_coding_card",
                "curriculum_algorithms_difficulty_card",
                "curriculum_language_card",
                "curriculum_study_habits_card",
                "curriculum_capstone_process_card",
                "project_competition_honesty_card",
                "future_salary_ai_honesty_card",
                "ai_faculty_lab_answer_card",
                "comparison_bilkent_honesty_card",
                "comparison_difficulty_honesty_card",
                "faculty_industry_experience_honesty_card",
                "curriculum_modernity_answer_card",
                "student_software_licenses_answer_card",
                "robotics_lab_access_answer_card",
                "erasmus_grant_sufficiency_answer_card",
                "global_exchange_america_honesty_card",
                "worship_exam_policy_honesty_card",
                "lab_computer_currency_honesty_card",
                "ai_gpu_access_honesty_card",
                "erasmus_compe_partner_examples_card",
                "erasmus_language_requirement_card",
                "curriculum_update_frequency_honesty_card",
                "equipment_loan_honesty_card",
                "academic_career_support_card",
                "teaching_materials_honesty_card",
                "differentiator_qs_abet_faculty_card",
                "curriculum_database_practice_card",
                "cloud_technologies_honesty_card",
                "insider_faculty_course_support_card",
                "housing_application_path_card",
                "game_interest_fit_card",
            }
            score += 40.0 if is_direct_answer else 25.0
        if (
            raw_id == "erasmus_course_recognition_card"
            and "erasmus" in folded_query
            and "ders" in folded_query
            and "sayil" in folded_query
        ):
            score += 25.0
        if "curriculum_year1" in topics and raw_id == "curriculum_year1_card":
            score += 8.0
        if "curriculum_beginner" in topics and raw_id == "curriculum_beginner_programming_card":
            score += 8.0
        if "curriculum_overview" in topics and raw_id == "curriculum_overview_card":
            score += 8.0
        focused_prefixes = {
            "database_course": ("curriculum_database_",),
            "cloud_technologies": ("cloud_technologies_", "department_lab_"),
            "programming_languages": ("curriculum_",),
            "curriculum_systems": ("curriculum_",),
            "curriculum_ai": ("curriculum_", "department_"),
            "curriculum_security": ("curriculum_", "department_"),
            "curriculum_projects": ("curriculum_", "internship_", "undergraduate_"),
            "academic_workload": ("curriculum_", "summer_", "academic_"),
            "teaching_quality": ("teaching_quality_", "department_"),
            "technical_resources": ("department_", "library_", "curriculum_", "lab_access_", "student_software_", "robotics_lab_"),
            "internship": ("internship_", "erasmus_internship"),
            "research_projects": ("undergraduate_", "robotics_", "department_", "department_clubs", "lab_access_"),
            "specialization": ("curriculum_", "department_", "robotics_"),
            "double_major_transfer": ("double_major_", "transfer_"),
            "erasmus": ("erasmus_", "global_exchange_"),
            "global_exchange": ("global_exchange_",),
            "clubs_teams": ("department_clubs_", "clubs_"),
            "worship_facilities": ("campus_worship_",),
            "housing_details": ("housing_", "student_support_"),
            "istanbul_life": ("istanbul_",),
            "student_social": ("student_profile_", "department_clubs_", "clubs_", "international_", "campus_student_"),
            "student_wellbeing": ("psychological_", "student_profile_", "library_", "curriculum_workload", "academic_", "career_guidance_"),
            "graduation": ("graduation_", "summer_", "curriculum_semester8", "curriculum_overview"),
            "ranking": ("admission_",),
            "admission": ("admission_",),
            "abroad": ("erasmus_", "abroad_", "international_", "itu_scale_"),
            "comparison": ("differentiator_", "itu_scale_"),
            "candidate_fit": ("candidate_fit_",),
        }
        for topic, prefixes in focused_prefixes.items():
            if (
                topic in topics
                and raw_id.startswith(prefixes)
                and (topic not in {"ranking", "admission"} or topic in direct_topics)
            ):
                score += 7.0
        if "student_experience" in topics and "student_experience" in fact_topics:
            score += 8.0

        # Profil ilgileri zayıf ama yararlı sinyal.
        for interest, val in profile.interests.items():
            if val > 0.15 and interest in hay_tokens:
                score += 0.5

        if score <= 0:
            continue
        scored.append(RetrievedFact(
            id=raw_id,
            text=text,
            label=raw.get("label", ""),
            source=raw.get("source", ""),
            source_url=raw.get("source_url", ""),
            source_urls=raw.get("source_urls", []),
            profile_url=raw.get("profile_url", ""),
            email=raw.get("email", ""),
            year=raw.get("year", ""),
            confidence=raw.get("confidence", "medium"),
            topics=fact_topics,
            examples=raw.get("examples", []),
            answer_card=bool(raw.get("answer_card", False)),
            applicable=rank_applicable,
            score=score,
        ))

    scored.sort(key=lambda f: (f.score, f.confidence == "high"), reverse=True)
    allowed_numbers = re.findall(r"%?\d+(?:[.,]\d+)?", user_text)
    if profile.yks_rank is not None:
        allowed_numbers.append(str(profile.yks_rank))
    return RagResult(query_topics=topics, facts=scored[:max_facts], allowed_numbers=list(dict.fromkeys(allowed_numbers)))


def _focus_terms(
    user_text: str,
    profile: CandidateProfile,
    *,
    include_profile: bool = True,
) -> list[str]:
    low = f" {_fold(user_text)} "
    interest = profile.interests
    aliases: list[str] = []

    if (
        any(p in low for p in (" yapay zeka", " ai ", " yz ", " makine ogren", " derin ogren", " machine learning", " deep learning"))
        or (include_profile and interest.get("ai", 0.0) > 0.15)
    ):
        aliases.extend([
            "artificial intelligence", "yapay zeka", "machine learning", "makine ogrenmesi",
            "deep learning", "derin ogrenme", "data science", "veri bilimi", "data analytics",
            "computer vision", "bilgisayarli goru",
        ])

    if any(p in low for p in (" nlp ", " dogal dil", " natural language", " dil isleme")):
        aliases.extend(["natural language processing", "dogal dil isleme", "nlp"])

    if any(p in low for p in (" robot", " robotik", " robotics")) or (include_profile and interest.get("robotics", 0.0) > 0.15):
        aliases.extend(["robotics", "robotik", "human computer interaction", "wearable computing"])

    if any(p in low for p in (" siber", " guvenlik", " cybersecurity", " security", " ag ", " network")) or (include_profile and interest.get("cybersec", 0.0) > 0.15):
        aliases.extend(["cybersecurity", "security", "privacy", "computer networks", "bilgisayar aglari", "cryptography", "blockchain"])

    if any(p in low for p in (" saglik", " tip", " biyoinformatik", " bioinformatics", " biomedical", " tibbi")):
        aliases.extend(["bioinformatics", "biyoinformatik", "health informatics", "saglik bilisimi", "medical image", "biomedical"])

    if any(p in low for p in (" yazilim", " software", " test", " formal verification")) or (include_profile and interest.get("software", 0.0) > 0.15):
        aliases.extend(["software engineering", "software testing", "formal verification", "yazilim muhendisligi", "yazilim testi"])

    terms: list[str] = []
    for alias in aliases:
        terms.extend(_tokens(alias))
    return list(dict.fromkeys(terms))


_TR_FOLD = str.maketrans("çğıöşüâîûÇĞİÖŞÜÂÎÛ", "cgiosuaiucgiosuaiu")


def _fold(text: str) -> str:
    """ASCII-toleranslı eşleşme: aday 'Cekirdek' yazsa da 'çekirdek' keyword'ü tutsun."""
    normalized = text.replace("’", "'").replace("‘", "'")
    return normalized.translate(_TR_FOLD).lower()


def infer_query_topics(
    user_text: str,
    profile: CandidateProfile,
    argument_id: str = "",
    include_profile: bool = True,
) -> list[str]:
    """include_profile=False → yalnızca METİNDEN türetilen topic'ler.

    Router fallback'i bunu kullanır: profil-türevi topic'ler (housing_needed=True gibi
    kalıcı sinyaller) güncel sorunun force'unu ele geçirmemeli — sess_f450'de 'kalacak
    yerim yok' diyen adayın SONRAKİ TÜM belirsiz soruları yurt argümanına mühürlenmişti.
    """
    low = _fold(user_text)
    direct_topics: list[str] = []
    for topic, words in TOPIC_KEYWORDS.items():
        if any(_keyword_matches(word, low) for word in words):
            direct_topics.append(topic)

    topics = list(direct_topics)
    topics.extend(ARGUMENT_TOPICS.get(argument_id, []))

    if not include_profile:
        return list(dict.fromkeys(topics)) or ["general"]

    ind = profile.indecision
    # Profile context is a tie-breaker for genuinely vague turns. Once the current
    # message has a direct topic, stale housing/comparison needs must not pollute it.
    if not direct_topics:
        if ind.university_alternatives:
            topics.append("comparison")
        if ind.field_alternatives and any(a in ("tıp", "tip", "medicine") for a in ind.field_alternatives):
            topics.append("healthtech")
        if ind.department_alternatives and any("yapay" in a or a in ("ai", "yz") for a in ind.department_alternatives):
            topics.append("curriculum")
        if profile.constraints.housing_needed:
            topics.append("housing")
    financial_direct = bool(
        set(direct_topics) & {"financial_support", "financial_concern", "scholarship"}
    )
    if (
        profile.constraints.cost_sensitivity
        and profile.constraints.cost_sensitivity >= 0.5
        and (not direct_topics or financial_direct)
    ):
        topics.extend(["financial_support", "financial_concern", "scholarship"])
    if profile.constraints.abroad_goal and profile.constraints.abroad_goal >= 0.5:
        topics.append("abroad")

    if not topics:
        topics = ["general"]
    return list(dict.fromkeys(topics))


def _tokens(text: str) -> list[str]:
    # Fold sonrası tokenize — "girişim" ile "girisim" aynı token olur
    return [t for t in re.split(r"[^a-z0-9]+", _fold(text)) if len(t) >= 3]


def _keyword_matches(keyword: str, folded_text: str) -> bool:
    folded_keyword = _fold(keyword)
    if not folded_keyword:
        return False
    end = r"(?![a-z0-9])" if len(folded_keyword) <= 3 else ""
    return bool(re.search(
        rf"(?<![a-z0-9]){re.escape(folded_keyword)}{end}",
        folded_text,
    ))
