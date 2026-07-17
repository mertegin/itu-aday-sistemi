"""Canonical normalizasyon — LLM'in ürettiği serbest varyantları tek forma indirir.

Örnekler:
  "yapay_zeka", "veri_mühendisliği", "veri_muhendisligi", "YZ" → "yapay_zeka_veri"
  "koç", "Koc", "koç üniversitesi" → "koc"
  "bilgisayar_mühendisliği" → HEDEF bölümdür; department_alternatives'e girmez
    (orchestrator bunu target_department + certainty sinyaline çevirir)

Canonical bölüm slug'ları academic.DEPT_CUTOFFS_2025 anahtarlarıyla uyumludur —
böylece her alternatif için risk bandı hesaplanabilir.
"""

_TR_FOLD = str.maketrans("çğıöşüâîûÇĞİÖŞÜÂÎÛ", "cgiosuaiucgiosuaiu")


def _fold(raw: str) -> str:
    """lowercase + Türkçe karakter düzleştirme + boşluk/tire → alt çizgi."""
    s = raw.strip().lower().translate(_TR_FOLD)
    for ch in (" ", "-", "'", "."):
        s = s.replace(ch, "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


# ============ BÖLÜMLER ============
# canonical → varyantlar (fold edilmiş halleriyle eşleşir)
_DEPT_SYNONYMS: dict[str, list[str]] = {
    "bilgisayar": [
        "bilgisayar", "bilgisayar_muhendisligi", "bilgisayar_muh", "compe", "cs",
        "computer", "computer_engineering", "bilg", "blg",
    ],
    "yapay_zeka_veri": [
        "yapay_zeka_veri", "yapay_zeka", "yz", "ai", "yapay_zeka_muhendisligi",
        "yapay_zeka_ve_veri", "yapay_zeka_ve_veri_muhendisligi",
        "veri_muhendisligi", "veri_bilimi", "data", "data_science", "veri",
    ],
    "elektronik_haberlesme": [
        "elektronik_haberlesme", "elektronik", "elektronik_muhendisligi", "ehm",
        "elektronik_ve_haberlesme", "haberlesme",
    ],
    "elektrik": ["elektrik", "elektrik_muhendisligi", "ee"],
    "kontrol_otomasyon": [
        "kontrol_otomasyon", "kontrol", "otomasyon", "kontrol_ve_otomasyon",
        "robotik", "robotik_otonom", "robotik_ve_otonom_sistemler", "robot",
    ],
    "ucak": ["ucak", "ucak_muhendisligi", "havacilik", "aeronautical"],
    "uzay": ["uzay", "uzay_muhendisligi", "aerospace", "astronotik"],
    "makine": ["makine", "makine_muhendisligi", "mechanical"],
    "endustri": ["endustri", "endustri_muhendisligi", "industrial"],
    "matematik": ["matematik", "matematik_muhendisligi", "math"],
    "siber_guvenlik": ["siber_guvenlik", "siber", "cyber", "cybersecurity", "bilgi_guvenligi"],
    "yazilim": ["yazilim", "yazilim_muhendisligi", "software", "software_engineering", "yazilim_muh"],
    # (İTÜ'de yazılım lisansı yok — bu canonical, software_vs_compe argümanını tetikler)
    "insaat": ["insaat", "insaat_muhendisligi", "civil"],
    "gemi": ["gemi", "gemi_insaati", "denizcilik"],
    "kimya": ["kimya", "kimya_muhendisligi"],
}

_DEPT_LOOKUP = {variant: canon for canon, variants in _DEPT_SYNONYMS.items() for variant in variants}

# Hedef bölümümüz — alternatif listesine girmez
TARGET_DEPT = "bilgisayar"


def normalize_department(raw: str) -> str | None:
    """Serbest bölüm adı → canonical slug. Eşleşmezse None (profili kirletme)."""
    if not raw:
        return None
    folded = _fold(raw)
    if folded in _DEPT_LOOKUP:
        return _DEPT_LOOKUP[folded]
    # Substring denemesi: "itu_yapay_zeka_bolumu" gibi sarmalamalar
    for variant, canon in _DEPT_LOOKUP.items():
        if len(variant) >= 4 and variant in folded:
            return canon
    return None


# ============ ÜNİVERSİTELER ============
_UNIV_SYNONYMS: dict[str, list[str]] = {
    "itu": ["itu", "istanbul_teknik", "istanbul_teknik_universitesi", "teknik_universite"],
    "koc": ["koc", "koc_universitesi", "ku"],
    "bogazici": ["bogazici", "bogazici_universitesi", "boun", "bogazici_uni"],
    "odtu": ["odtu", "metu", "orta_dogu", "orta_dogu_teknik", "orta_dogu_teknik_universitesi"],
    "ytu": ["ytu", "yildiz", "yildiz_teknik", "yildiz_teknik_universitesi"],
    "bilkent": ["bilkent", "bilkent_universitesi"],
    "sabanci": ["sabanci", "sabanci_universitesi", "su"],
    "hacettepe": ["hacettepe", "hacettepe_universitesi"],
    "istanbul": ["istanbul_universitesi", "iu"],
    "marmara": ["marmara", "marmara_universitesi"],
}

_UNIV_LOOKUP = {variant: canon for canon, variants in _UNIV_SYNONYMS.items() for variant in variants}


def normalize_university(raw: str) -> str | None:
    if not raw:
        return None
    folded = _fold(raw)
    if folded in _UNIV_LOOKUP:
        return _UNIV_LOOKUP[folded]
    for variant, canon in _UNIV_LOOKUP.items():
        if len(variant) >= 3 and variant in folded:
            return canon
    return None


# ============ ALANLAR (mühendislik-dışı) ============
_FIELD_SYNONYMS: dict[str, list[str]] = {
    "tip": ["tip", "tıp", "doktorluk", "hekimlik", "medicine", "medical"],
    "dis_hekimligi": ["dis_hekimligi", "dis", "dentistry"],
    "eczacilik": ["eczacilik", "pharmacy"],
    "hukuk": ["hukuk", "law", "avukatlik"],
    "isletme": ["isletme", "business", "iktisat", "ekonomi", "economics"],
    "mimarlik": ["mimarlik", "architecture", "mimari"],
    "psikoloji": ["psikoloji", "psychology"],
    "ogretmenlik": ["ogretmenlik", "egitim", "teaching"],
}

_FIELD_LOOKUP = {variant: canon for canon, variants in _FIELD_SYNONYMS.items() for variant in variants}


def normalize_field(raw: str) -> str | None:
    if not raw:
        return None
    folded = _fold(raw)
    if folded in _FIELD_LOOKUP:
        return _FIELD_LOOKUP[folded]
    for variant, canon in _FIELD_LOOKUP.items():
        if len(variant) >= 3 and variant in folded:
            return canon
    return None
