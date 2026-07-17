"""Etik guardrail — LLM cevabını hafif filtreler.

V1: keyword bazlı. LLM tekrar-çağrısı yok (basit tutuyoruz).
"""
import re


# --- Yasak/Riskli desenler ---

# Rakip üniversiteyi kötüleyen ifadeler
DISPARAGING_PATTERNS = [
    r"\b(kötü|zayıf|yetersiz|başarısız|düşük kaliteli|geride|geri kalmış|ikinci sınıf)\s+(bir\s+)?(üniversite|okul|program|bölüm)",
    r"(odtü|boğaziçi|koç|ytu|bilkent|sabancı)['\s]+.{0,20}?(kötü|zayıf|yetersiz|başarısız|değersiz)",
    r"(kötü|zayıf|yetersiz|başarısız).{0,20}?(odtü|boğaziçi|koç|ytu|bilkent|sabancı)",
]

# Mutlak/manipülatif ifadeler
ABSOLUTIST_PATTERNS = [
    r"\bİTÜ\s+kesinlikle\s+en\s+iyi",
    r"\bİTÜ\s+her(kes|\s+açıdan)?\s+en\s+iyi",
    r"\bhiç\s+şüphesiz\s+İTÜ",
    r"\b(hiçbir|başka)\s+üniversite\s+.{0,20}?İTÜ\s+kadar",
    r"kaçırırsan\s+pişman\s+ol",
    r"bu\s+fırsat\s+sadece",
]

# Değer yargısı
JUDGMENTAL_PATTERNS = [
    r"\bbaşaramazsın\b",
    r"\bsenin\s+için\s+zor\s+olur\b",
    r"\byapamazsın\b",
]


ALL_PATTERNS = [
    ("disparaging", DISPARAGING_PATTERNS),
    ("absolutist", ABSOLUTIST_PATTERNS),
    ("judgmental", JUDGMENTAL_PATTERNS),
]


# Soft-sanitize ile de temizlenemeyen ihlallerde kullanılacak güvenli yanıtlar (kategoriye göre)
SAFE_REPLACEMENTS = {
    "disparaging": (
        "ODTÜ, Boğaziçi ve diğer güçlü seçenekleri küçümsemeyiz; bizim farkımızı kaynaklı "
        "İTÜ Bilgisayar verileri ve adayın hedefi üzerinden anlatırız."
    ),
    "absolutist": (
        "Biz İTÜ Bilgisayar'ı güçlü bir seçenek olarak görüyoruz; uygunluğunu somut bölüm "
        "verileri ve adayın hedefi üzerinden kurmak daha doğru."
    ),
    "judgmental": (
        "Bizim bölümümüzde zorlayıcı dönemler olabilir; danışmanlık, düzenli çalışma ve "
        "öğrencinin ilgisiyle ilerlemek mümkün."
    ),
}
DEFAULT_SAFE_TEXT = (
    "Bizim bölümümüzün güçlü yanlarını hedefinle eşleştirip kaynaklı ve somut biçimde anlatacağım; "
    "kararı etkileyen belirsizlikleri de saklamayacağım."
)


class EthicsFilter:
    """Keyword tabanlı hızlı filter.

    Akış: soft_sanitize (kalıp temizliği) → check → hâlâ ihlal varsa enforce ile güvenli metin.
    """

    def check(self, text: str) -> dict:
        text_lower = text.lower()
        violations = []
        for category, patterns in ALL_PATTERNS:
            for p in patterns:
                if re.search(p, text_lower):
                    violations.append({"category": category, "pattern": p})

        return {
            "clean": len(violations) == 0,
            "violations": violations,
        }

    def enforce(self, text: str) -> tuple[str, dict]:
        """Sanitize + check + gerekirse yanıtı güvenli metinle değiştir.

        Returns: (final_text, ethics_result). ethics_result["replaced"]=True ise yanıt değişti.
        """
        sanitized = self.soft_sanitize(text)
        result = self.check(sanitized)
        if result["clean"]:
            result["replaced"] = False
            return sanitized, result

        category = result["violations"][0]["category"]
        safe_text = SAFE_REPLACEMENTS.get(category, DEFAULT_SAFE_TEXT)
        result["replaced"] = True
        result["original_text"] = text
        return safe_text, result

    def soft_sanitize(self, text: str) -> str:
        """En yaygın kırmızı bayrakları soft-yumuşat.

        V1'de LLM ping-back yerine minimal text değişikliği yapıyoruz.
        """
        replacements = [
            (r"\bkesinlikle\s+en\s+iyi\b", "güçlü seçeneklerden biri"),
            (r"\bhiç\s+şüphesiz\b", "büyük ihtimalle"),
            (r"\bbaşaramazsın\b", "belki zorlanabilirsin ama destek mekanizmaları var"),
            (r"\byapamazsın\b", "kolay olmayabilir ama mümkün"),
            # Sınava hazırlık yorumu — yanlış bağlam
            (r"YKS'ye\s+hazırlık\s+sürecinde", "tercih sürecinde"),
            (r"sınava\s+hazırlanırken", "tercih yaparken"),
        ]
        result = text
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Adayın sıralamasını mekanik biçimde "güvenli bölge" diye etiketlemek
        # doğal konuşmayı bozuyor ve yerleşme garantisi çağrışımı yapıyor.
        result = re.sub(
            r"[^.!?]*(?:güvenli\s+bir\s+bölge(?:de|desin)|güvenli\s+bölgedesin)[.!?]?\s*",
            "",
            result,
            flags=re.IGNORECASE,
        ).strip()

        # "Doğru mu anladım?" kalıbını cümlenin sonundaysa temizle
        result = re.sub(r"[.,!]?\s*Doğru\s+mu\s+anladım\s*\??", ".", result, flags=re.IGNORECASE)
        # Uç-cümledeki ", doğru mu?" da benzer şekilde
        result = re.sub(r",\s*doğru\s+mu\s*\?", ".", result, flags=re.IGNORECASE)

        return result


def enforce_spoken_length(text: str, max_words: int = 40) -> tuple[str, dict]:
    """Keep robot speech within the prompt's hard word budget."""
    words = text.split()
    if len(words) <= max_words:
        return text, {"trimmed": False, "word_count": len(words), "max_words": max_words}

    # Ordinal-farkında bölme: "91. sırada" ifadesindeki nokta cümle sonu değildir
    from ..kb.fact_gate import split_sentences_tr
    sentences = split_sentences_tr(text)
    selected: list[str] = []
    count = 0
    for sentence in sentences:
        sentence_words = sentence.split()
        if count + len(sentence_words) > max_words:
            break
        selected.append(sentence)
        count += len(sentence_words)

    if selected:
        shortened = " ".join(selected).strip()
    else:
        shortened = " ".join(words[:max_words]).rstrip(" ,;:")
        if shortened and shortened[-1] not in ".!?":
            shortened += "."
    return shortened, {
        "trimmed": True,
        "word_count": len(shortened.split()),
        "original_word_count": len(words),
        "max_words": max_words,
    }


_QUESTION_ARGUMENTS = {"socratic_probe", "rank_probe"}
_CANNED_TRAILING_QUESTIONS = (
    r"bunu\s+düşünür\s+müsün",
    r"ne\s+dersin",
    r"senin\s+için\s+hangisi",
    r"sana\s+en\s+uygun\s+olan\s+hangisi",
    r"hangisi\s+daha\s+önemli",
    r"ister\s+misin",
    r"bunu\s+yapar\s+mısın",
    r"hazır\s+mısın",
)


def enforce_conversation_voice(
    text: str,
    argument_id: str,
    *,
    user_asked_question: bool = False,
    wants_detail: bool = False,
    allow_followup: bool = False,
) -> tuple[str, dict]:
    """Remove the model's habitual closing question from direct answers.

    Discovery turns may ask one real question. Other turns always drop canned
    prompts; direct information requests also drop any trailing extra question.
    """
    if argument_id in _QUESTION_ARGUMENTS:
        return text, {"question_removed": False, "reason": "discovery_argument"}

    from ..kb.fact_gate import split_sentences_tr

    sentences = split_sentences_tr(text)
    if not sentences:
        return text, {"question_removed": False, "reason": "empty"}

    trailing = sentences[-1].strip()
    folded = trailing.casefold()
    is_canned = trailing.endswith("?") and any(
        re.search(pattern, folded, flags=re.IGNORECASE)
        for pattern in _CANNED_TRAILING_QUESTIONS
    )
    is_extra_direct_question = (
        trailing.endswith("?")
        and (user_asked_question or wants_detail)
        and not allow_followup
    )
    if not (is_canned or is_extra_direct_question) or len(sentences) == 1:
        return text, {"question_removed": False, "reason": "not_applicable"}

    cleaned = " ".join(sentences[:-1]).strip()
    return cleaned, {
        "question_removed": True,
        "reason": "canned" if is_canned else "direct_answer",
        "removed_text": trailing,
    }
