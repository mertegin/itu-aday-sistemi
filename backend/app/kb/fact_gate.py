"""Fact gate: LLM yanıtındaki riskli iddiaları RAG fact'leriyle sınırla.

Bu katman kanıtlayıcı bir doğruluk motoru değildir; demo için en riskli sızıntıları
yakalar: desteklenmeyen sayılar, garanti/kesinlik dili, lisans bölümü uydurma,
çift anadal/aylık para gibi kaynak gerektiren kesin iddialar.
"""
from dataclasses import dataclass, field
import re

from .retriever import RagResult


@dataclass
class FactGateResult:
    clean: bool
    violations: list[dict] = field(default_factory=list)
    replaced: bool = False
    original_text: str | None = None

    def to_dict(self) -> dict:
        return {
            "clean": self.clean,
            "violations": self.violations,
            "replaced": self.replaced,
            "original_text": self.original_text,
        }


RISK_PATTERNS = [
    ("absolute", r"\b(kesinlikle|garanti|garantili|rahatça garanti|mutlaka)\b"),
    ("cash_support", r"\b(aylık para|para desteği|nakit destek)\b"),
    ("degree_program", r"\b(oyun teknolojileri|blockchain|siber güvenlik).{0,40}\b(lisans|bölüm|bölümü)\b"),
    ("double_major", r"\b(çift anadal|çap).{0,40}\b(yapabilirsin|mümkün|var)\b"),
    ("faculty_names", r"\b(prof\.|doç\.|dr\. öğretim|hoca adı|şu hoca)\b"),
    ("prep_not_required", r"\bhazırlık.{0,25}\b(zorunlu değil|isteğe bağlı)\b"),
]


# Broad qualitative claims can be just as misleading as unsupported numbers.
# Each rule requires at least one explicit support anchor in the retrieved facts.
QUALITATIVE_CLAIMS = [
    (
        "student_satisfaction",
        r"öğrenci\s+memnuniyeti.{0,25}\b(yüksek|iyi|çok iyi)\b",
        ("öğrenci memnuniyeti", "memnuniyet oranı"),
    ),
    (
        "women_representation",
        r"kadın.{0,45}\b(artıyor|artmakta|giderek art|oranı yüksek|sayısı yüksek)\b",
        ("kadın oranı", "kadınların sayısı", "kadın öğrenci oranı"),
    ),
    (
        "housing_quality",
        r"yurtlar?.{0,30}\b(çok iyi|oldukça iyi|konforlu|modern|kaliteli)\b",
        ("yurtlar çok iyi", "yurtlar oldukça iyi", "konforlu yurt", "modern yurt"),
    ),
    (
        "employment_outcome",
        r"(iş bulma|işe yerleşme).{0,35}\b(oranı yüksek|şansı yüksek|oldukça yüksek|kolay)\b",
        ("iş bulma oranı", "işe yerleşme oranı", "istihdam oranı"),
    ),
]


def enforce_fact_gate(text: str, rag: RagResult, question: str = "") -> tuple[str, dict]:
    result = check_fact_gate(text, rag)
    if result.clean:
        return text, result.to_dict()

    # KURTARMA: cevabı komple atmadan önce yalnızca İHLALLİ CÜMLELERİ çıkarmayı dene.
    # (sess_051a bulgusu: "kaliteli mi" sorusunda LLM'in iyi cevabı tek sayı yüzünden
    #  tamamen atılıp yerine 'kaynak yok' konuyordu.)
    salvaged = _drop_violating_sentences(text, rag)
    if salvaged:
        salvage_check = check_fact_gate(salvaged, rag)
        if salvage_check.clean:
            result.replaced = True
            result.original_text = text
            out = result.to_dict()
            out["salvaged"] = True
            return salvaged, out

    safe = build_safe_response(rag, question=question)
    result.replaced = True
    result.original_text = text
    out = result.to_dict()
    out["salvaged"] = False
    return safe, out


def split_sentences_tr(text: str) -> list[str]:
    """Türkçe ordinal-farkında cümle bölme.

    "QS'de 91. sırada yer alması" ifadesindeki "91." cümle sonu DEĞİLDİR —
    naif split bunu bölüp sayıyı düşürüyordu ("...91." atıldı, "sırada yer alması..."
    kaldı — sess_1329'daki bozuk cevapların kökü).
    """
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    merged: list[str] = []
    for p in parts:
        if merged and re.search(r"\d\.$", merged[-1]):
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return merged


def _drop_violating_sentences(text: str, rag: RagResult) -> str | None:
    """İhlal içeren cümleleri at; en az 1 temiz-anlamlı cümle kalıyorsa onları döndür."""
    sentences = split_sentences_tr(text)
    if len(sentences) <= 1:
        return None
    clean_sentences = []
    for s in sentences:
        if not s.strip():
            continue
        if check_fact_gate(s, rag).clean:
            clean_sentences.append(s.strip())
    if not clean_sentences:
        return None
    out = " ".join(clean_sentences)
    return out if len(out.split()) >= 5 else None


def check_fact_gate(text: str, rag: RagResult) -> FactGateResult:
    low = text.lower()
    corpus = "\n".join(f"{f.text} {f.source} {f.year}" for f in rag.facts).lower()
    violations: list[dict] = []

    for category, pattern in RISK_PATTERNS:
        if re.search(pattern, low, flags=re.IGNORECASE):
            # Aynı riskli ifade kaynak fact içinde de geçiyorsa serbest bırak.
            # Örn. "çift diploma" fact'te var; ama "çift anadal yapabilirsin" yoksa yakalanır.
            matched = re.search(pattern, low, flags=re.IGNORECASE)
            snippet = matched.group(0) if matched else pattern
            if snippet.lower() not in corpus:
                violations.append({"category": category, "claim": snippet})

    for category, pattern, support_anchors in QUALITATIVE_CLAIMS:
        matched = re.search(pattern, low, flags=re.IGNORECASE)
        if matched and not any(anchor in corpus for anchor in support_anchors):
            violations.append({"category": category, "claim": matched.group(0)})

    # Yanıttaki sayılar RAG'de yoksa riskli. Kısa sınıf/sıra ifadeleri de sayı sayılır.
    allowed_numbers = set(getattr(rag, "allowed_numbers", []) or [])
    for num in _numbers(text):
        if num in allowed_numbers:
            continue
        if not _number_supported(num, corpus):
            violations.append({"category": "unsupported_number", "claim": num})

    # Oyun teknolojileri özel düzeltme: lisans bölümü diye sunulmasın.
    if "oyun teknolojileri" in low and any(w in low for w in ("bölüm", "lisans")):
        if "yüksek lisans" not in corpus and "lisans bölümü" not in corpus:
            violations.append({"category": "unsupported_degree_program", "claim": "oyun teknolojileri lisans/bölüm"})

    # Kaynakta olmayan kulağa makul kulüp adlarını engelle.
    for named_club in re.findall(
        r"\b(?:İTÜ\s+)?[A-ZÇĞİÖŞÜ][\wÇĞİÖŞÜçğıöşü-]*(?:\s+[A-ZÇĞİÖŞÜ][\wÇĞİÖŞÜçğıöşü-]*){0,3}\s+Kulübü\b",
        text,
    ):
        if named_club.casefold() not in corpus.casefold():
            violations.append({"category": "unsupported_named_club", "claim": named_club})

    if re.search(r"2025(?:'te| yılında).{0,45}5[.]?000", text, flags=re.IGNORECASE) and "14 yılda" in corpus:
        violations.append({
            "category": "entrepreneurship_period_collapse",
            "claim": "14 yıllık toplamı yalnız 2025'te gerçekleşmiş gibi sunma",
        })

    return FactGateResult(clean=len(violations) == 0, violations=violations)


# Bota yazılmış yönerge kalıpları — bu fact'ler kullanıcıya OLDUĞU GİBİ kopyalanamaz.
# (Örn. "asla 'sınırda' deme", "RAG'de isim yoksa hoca adı uydurma" adaya sızmıştı.)
_INSTRUCTIONAL_MARKERS = (
    "deme", "söyle", "çerçevele", "küçümseme", "kabul et", "vurgula",
    "kullan", "sunma", "önce", "geç.", "→", "uyarısı", "diye",
    "doğrulanmalı", "uydurma", "teyit et", "yönerge", "rag",
)


def _is_instructional(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in _INSTRUCTIONAL_MARKERS)


_TR_FOLD_GATE = str.maketrans("çğıöşüâîûÇĞİÖŞÜÂÎÛ", "cgiosuaiucgiosuaiu")

# Her fact'te geçen domain kelimeleri alaka sinyali DEĞİLDİR — bunlar yüzünden
# "itü bilgisayar kaliteli mi" sorusuna hoca-eposta fact'i "alakalı" sayılmıştı.
_DOMAIN_STOPWORDS = {
    "itu", "bilgisayar", "muhendislik", "muhendisligi", "bolum", "bolumu",
    "universite", "universitesi", "icin", "gibi", "olarak", "resmi", "sayfa",
}


def _q_tokens(text: str) -> set[str]:
    toks = {t for t in re.split(r"[^a-z0-9]+", text.lower().translate(_TR_FOLD_GATE)) if len(t) >= 3}
    return toks - _DOMAIN_STOPWORDS


def _token_overlap(a: set[str], b: set[str]) -> int:
    """Türkçe ek toleranslı kesişim: 'kaliteli' ~ 'kalitesi' (ortak 5+ harf prefix) eşleşir."""
    exact = len(a & b)
    fuzzy = 0
    for ta in a:
        if ta in b:
            continue
        for tb in b:
            if len(ta) >= 5 and len(tb) >= 5 and (ta.startswith(tb[:5]) or tb.startswith(ta[:5])):
                fuzzy += 1
                break
    return exact + fuzzy


def build_safe_response(rag: RagResult, question: str = "", compact: bool = False) -> str:
    """Gate cevabı değiştirirken SORUYLA ALAKALI konuşulabilir fact seç.

    (Regresyon: 'tercih listemde kaçıncı sıraya yazayım' sorusuna 'araştırma alanları'
    fact'i dönüyordu — alaka kontrolü yoktu.)
    """
    no_source_text = (
        "Bu konuda net kaynaklı bilgi yok; kesin sayı veya garanti vermem doğru olmaz. "
        "Bunu resmi bölüm sayfası ya da tanıtım masasından doğrulayalım; ben İTÜ Bilgisayar'ın kaynaklı diğer güçlü yönlerini anlatabilirim."
    )
    if not rag.facts:
        return no_source_text

    # Yalnızca adaya doğrudan söylenebilir (yönergesiz) fact'ler kullanılabilir
    speakable = [
        f for f in rag.facts
        if f.applicable and f.confidence in ("high", "medium") and not _is_instructional(f.text)
    ]
    if not speakable:
        return no_source_text

    # Soru verildiyse: soruyla token kesişimi olan fact'i tercih et; hiç kesişen yoksa
    # alakasız fact okumak yerine kaynak-yok metnine düş.
    chosen = speakable[0]
    matching_cards = [
        f for f in speakable
        if f.answer_card and set(f.topics) & set(rag.query_topics)
    ]
    if matching_cards:
        chosen = max(matching_cards, key=lambda f: f.score)
    elif question:
        q_tok = _q_tokens(question)
        overlapping = [(_token_overlap(q_tok, _q_tokens(f.text)), f) for f in speakable]
        overlapping.sort(key=lambda x: x[0], reverse=True)
        if overlapping[0][0] > 0:
            chosen = overlapping[0][1]
        else:
            return no_source_text

    if compact:
        return chosen.text

    return (
        f"Kaynaklı bilgi şu: {chosen.text} "
        "Bunun dışında kesin garanti vermem doğru olmaz; ayrıntıyı resmi sayfadan doğrulayabiliriz."
    )


def enforce_answer_relevance(text: str, rag: RagResult, question: str) -> tuple[str, dict]:
    """Replace a clearly off-topic answer with the retriever's top answer card."""
    if not question or not rag.facts:
        return text, {"repaired": False, "reason": "no_question_or_facts"}

    cards = [
        fact for fact in rag.facts
        if fact.answer_card
        and fact.applicable
        and fact.confidence in ("high", "medium")
        and not _is_instructional(fact.text)
    ]
    if not cards:
        return text, {"repaired": False, "reason": "no_answer_card"}

    card = cards[0]
    q_tokens = _q_tokens(question)
    answer_overlap = _token_overlap(q_tokens, _q_tokens(text))
    card_overlap = _token_overlap(q_tokens, _q_tokens(card.text))
    clearly_off_topic = (
        card_overlap >= 2
        and (answer_overlap == 0 or card_overlap >= answer_overlap + 2)
    )
    if not clearly_off_topic:
        return text, {
            "repaired": False,
            "reason": "relevant",
            "answer_overlap": answer_overlap,
            "card_overlap": card_overlap,
            "card_id": card.id,
        }

    return card.text, {
        "repaired": True,
        "reason": "top_card_more_relevant",
        "answer_overlap": answer_overlap,
        "card_overlap": card_overlap,
        "card_id": card.id,
        "original_text": text,
    }


def enforce_non_repetition(
    text: str,
    rag: RagResult,
    question: str,
    history: list[dict],
) -> tuple[str, dict]:
    """Advance to another relevant RAG card when the answer repeats verbatim."""
    previous = [
        str(message.get("text", ""))
        for message in history
        if message.get("role") == "assistant" and message.get("text")
    ][-2:]
    if not previous:
        return text, {"repaired": False, "reason": "no_previous_answer"}

    similarity = max(_token_similarity(text, old) for old in previous)
    if similarity < 0.86:
        return text, {"repaired": False, "reason": "distinct", "similarity": round(similarity, 3)}

    q_tokens = _q_tokens(question)
    candidates = []
    for fact in rag.facts:
        if (
            not fact.answer_card
            or not fact.applicable
            or fact.confidence not in ("high", "medium")
            or _is_instructional(fact.text)
        ):
            continue
        candidate_similarity = max(_token_similarity(fact.text, old) for old in previous)
        overlap = _token_overlap(q_tokens, _q_tokens(fact.text))
        if candidate_similarity < 0.72 and overlap > 0:
            candidates.append((overlap, fact.score, fact))

    if not candidates:
        return text, {"repaired": False, "reason": "no_distinct_relevant_card", "similarity": round(similarity, 3)}

    _, _, chosen = max(candidates, key=lambda item: (item[0], item[1]))
    return chosen.text, {
        "repaired": True,
        "reason": "duplicate_answer",
        "similarity": round(similarity, 3),
        "card_id": chosen.id,
        "original_text": text,
    }


def enforce_scholarship_eligibility(
    text: str,
    rag: RagResult,
    question: str,
) -> tuple[str, dict]:
    """Keep a known-rank burs answer on the applicable cash tier and its conditions."""
    folded_question = question.lower().translate(_TR_FOLD_GATE)
    direct_burs_question = any(term in folded_question for term in ("burs", "basari odulu", "maddi destek"))
    ranked_cards = [
        fact for fact in rag.facts
        if fact.applicable and fact.id.startswith("scholarship_rank_")
    ]
    if not ranked_cards:
        return text, {"repaired": False, "reason": "no_applicable_rank_card"}

    card = ranked_cards[0]
    expected_amounts = {
        "scholarship_rank_1_10": ("100.000", "10.000"),
        "scholarship_rank_11_100": ("10.000",),
        "scholarship_rank_101_500": ("8.500",),
        "scholarship_rank_501_1000": ("6.750", "60.750"),
    }.get(card.id, ())
    folded_text = text.lower().translate(_TR_FOLD_GATE)
    has_expected_amount = any(amount in text for amount in expected_amounts)
    has_complete_tier = {
        "scholarship_rank_1_10": (
            "100.000" in text and text.count("10.000") >= 2 and "9 ay" in folded_text
        ),
        "scholarship_rank_11_100": text.count("10.000") >= 2 and "9 ay" in folded_text,
        "scholarship_rank_101_500": "8.500" in text and "9 ay" in folded_text,
        "scholarship_rank_501_1000": (
            "6.750" in text and "9 ay" in folded_text and "ilk tercih" in folded_text
        ),
    }.get(card.id, has_expected_amount)

    if direct_burs_question and expected_amounts and (not has_complete_tier or "sans" in folded_text):
        return card.text, {
            "repaired": True,
            "reason": "applicable_rank_tier",
            "card_id": card.id,
            "original_text": text,
        }

    requires_first_choice = card.id == "scholarship_rank_501_1000"
    mentions_first_choice = "ilk tercih" in folded_text or "1. tercih" in folded_text
    if has_expected_amount and requires_first_choice and not mentions_first_choice:
        return f"{text.rstrip()} Bu destek ilk tercih ve devam koşullarına bağlı.", {
            "repaired": True,
            "reason": "missing_first_choice_condition",
            "card_id": card.id,
            "original_text": text,
        }

    return text, {"repaired": False, "reason": "eligible_tier_and_conditions_present", "card_id": card.id}


def enforce_admission_reality(
    text: str,
    rag: RagResult,
    question: str,
    rank: int | None,
) -> tuple[str, dict]:
    """Make rank-sensitive admission claims deterministic."""
    if rank is None:
        return text, {"repaired": False, "reason": "rank_unknown"}

    folded = question.lower().translate(_TR_FOLD_GATE)
    rank_terms = (
        "siralam", "taban", "puan", "gelir mi", "girer mi", "girebilir",
        "yeter mi", "sansim", "tercih", "kac bin", "tutar mi", "olur mu",
    )
    competitor_terms = ("koc", "ytu", "yildiz teknik", "odtu", "bogazici", "bilkent", "sabanci")
    has_rank_intent = any(term in folded for term in rank_terms)
    has_comparison_intent = any(term in folded for term in competitor_terms)
    financial_terms = ("burs", "basari odulu", "maddi destek", "aylik odul", "yurt destegi")
    admission_predicates = ("taban", "gelir mi", "girer mi", "girebilir", "yeter mi", "sansim", "kabul", "olur mu")
    if (
        any(term in folded for term in financial_terms)
        and not any(term in folded for term in admission_predicates)
        and not has_comparison_intent
    ):
        return text, {"repaired": False, "reason": "financial_question_not_admission"}
    if not has_rank_intent and not has_comparison_intent:
        return text, {"repaired": False, "reason": "not_an_admission_turn"}

    itu_compe = 1435
    itu_ai = 1947
    if "koc" in folded:
        koc_full = 113
        if rank <= koc_full:
            prefix = (
                f"2025'te Koç Bilgisayar %100 burslu 113, İTÜ Bilgisayar 1.435 ile kapattı; "
                f"{_format_rank(rank)} sıralaman iki tabanın da önünde, fakat yeni yıl için ikisi de garanti değil. "
                f"İTÜ devlet üniversitesi olduğu için eğitim ücretsiz; {_itu_merit_summary(rank)} "
                "Koç'un net toplam teklifini bu paketle karşılaştırmak gerekir."
            )
        elif rank <= itu_compe:
            prefix = (
                "2025'te Koç Bilgisayar %100 burslu 113, İTÜ Bilgisayar 1.435 ile kapattı. "
                f"{_format_rank(rank)} sıralamanla Koç'un %100 burslu kontenjanı geçen yıl gerçekçi değildi; "
                "bizim İTÜ Bilgisayar tabanının ise önündesin. "
                f"İTÜ'de eğitim ücretsiz; {_itu_merit_summary(rank)} Yeni yıl garantisi veremem."
            )
        else:
            prefix = (
                "2025'te Koç Bilgisayar %100 burslu 113, İTÜ Bilgisayar 1.435 ile kapattı. "
                f"{_format_rank(rank)} sıralaman iki tabanın da gerisinde; ikisini de gelecek yıl kesin kabul gibi anlatamam."
            )
        return prefix, {
            "repaired": prefix != text,
            "reason": "koc_full_scholarship_rank_context",
            "rank": rank,
            "cutoffs": {"koc_compe_full": koc_full, "itu_compe": itu_compe},
            "original_text": text,
        }

    if has_comparison_intent and not has_rank_intent:
        return text, {"repaired": False, "reason": "comparison_without_admission_question"}

    if rank <= itu_compe:
        proximity = "çok yakın biçimde " if rank >= 1300 else ""
        prefix = (
            f"İTÜ Bilgisayar 2025'te 1.435 ile kapattı; {_format_rank(rank)} sıralaman "
            f"geçen yılki tabanın {proximity}önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem."
        )
        reason = "ahead_of_itu_compe_2025"
        alternative = None
    elif rank <= itu_ai:
        prefix = (
            f"İTÜ Bilgisayar'ın 2025 tabanı 1.435'ti; {_format_rank(rank)} sıralaman bunun gerisinde, "
            "bu yüzden Bilgisayar'ı gerçekçi ana seçenek gibi gösteremem. İTÜ Yapay Zekâ ve Veri 1.947'de "
            "kapattığı için geçen yılki veride daha gerçekçi İTÜ seçeneğiydi; gelecek yıl yine garanti değil."
        )
        reason = "behind_compe_ahead_of_ai_2025"
        alternative = "yapay_zeka_veri"
    else:
        alternative, cutoff = _strict_itu_alternative(rank)
        if alternative:
            prefix = (
                f"{_format_rank(rank)} sıralaman, 2025'te İTÜ Bilgisayar'ın 1.435 ve Yapay Zekâ-Veri'nin "
                f"1.947 tabanının gerisinde; ikisini de gerçekçi ana seçenek gibi satmam doğru olmaz. "
                f"İTÜ içinde {_department_label(alternative)} {_format_rank(cutoff)} ile kapattığı için "
                "geçen yılki tabloya göre daha gerçekçi bir yoldu."
            )
        else:
            prefix = (
                f"{_format_rank(rank)} sıralaman, 2025'te İTÜ Bilgisayar'ın 1.435 ve Yapay Zekâ-Veri'nin "
                "1.947 tabanının gerisinde; bu iki programı gerçekçi ana seçenek gibi satmam doğru olmaz."
            )
        reason = "behind_compe_and_ai_2025"

    return prefix, {
        "repaired": prefix != text,
        "reason": reason,
        "rank": rank,
        "cutoffs": {"itu_compe": itu_compe, "itu_ai_data": itu_ai},
        "alternative": alternative,
        "original_text": text,
    }


def _strict_itu_alternative(rank: int) -> tuple[str | None, int | None]:
    from ..profile.academic import DEPT_CUTOFFS_2025

    excluded = {"bilgisayar", "yapay_zeka_veri"}
    for department, cutoff in sorted(DEPT_CUTOFFS_2025.items(), key=lambda item: item[1]):
        if department not in excluded and rank <= cutoff:
            return department, cutoff
    return None, None


def _department_label(department: str) -> str:
    return {
        "elektronik_haberlesme": "Elektronik-Haberleşme",
        "ucak": "Uçak Mühendisliği",
        "matematik": "Matematik Mühendisliği",
        "endustri": "Endüstri Mühendisliği",
        "uzay": "Uzay Mühendisliği",
        "kontrol_otomasyon": "Kontrol ve Otomasyon Mühendisliği",
        "makine": "Makine Mühendisliği",
        "elektrik": "Elektrik Mühendisliği",
    }.get(department, department.replace("_", " ").title())


def _format_rank(value: int | None) -> str:
    if value is None:
        return ""
    return f"{value:,}".replace(",", ".")


def _itu_merit_summary(rank: int) -> str:
    if rank <= 10:
        return "ilk-10 paketinde tek seferlik 100.000 TL ve başarı koşullarına bağlı düzenli ödül var."
    if rank <= 100:
        return "11-100 paketinde başarı koşullarına bağlı, yılda 9 ay düzenli ödül var."
    if rank <= 500:
        return "101-500 paketinde yılda 9 ay aylık 8.500 TL başarı ödülü var."
    if rank <= 1000:
        return "501-1000 paketinde ilk tercih koşuluyla yılda 9 ay aylık 6.750 TL başarı ödülü var."
    return "başarı ödülü dilimi yerine ihtiyaç ve ilk tercih destekleri ayrıca incelenmeli."


def _prepend_without_duplicate(prefix: str, text: str) -> str:
    prefix_tokens = _q_tokens(prefix)
    text_tokens = _q_tokens(text)
    if prefix_tokens and len(prefix_tokens & text_tokens) / len(prefix_tokens) >= 0.72:
        return prefix
    return f"{prefix} {text}".strip()


def _token_similarity(left: str, right: str) -> float:
    left_tokens = set(_q_tokens(left))
    right_tokens = set(_q_tokens(right))
    if not left_tokens or not right_tokens:
        return 1.0 if left.strip().casefold() == right.strip().casefold() else 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _numbers(text: str) -> list[str]:
    # 1.435, 4800, %17,9, 3. sınıf gibi sayıları yakalar.
    return re.findall(r"%?\d+(?:[.,]\d+)?", text)


def _number_supported(num: str, corpus: str) -> bool:
    raw = num.lower().replace("%", "")
    variants = {
        raw,
        raw.replace(".", ""),
        raw.replace(",", "."),
        raw.replace(".", ","),
    }
    compact_corpus = corpus.replace(".", "").replace(",", ".")
    return any(v in corpus or v in compact_corpus for v in variants)
