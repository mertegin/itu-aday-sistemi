"""Akademik uygunluk — deterministik türetmeler (LLM'e bırakılmaz).

Kaynak: kb/facts.yaml'daki 2025 taban sıraları. Sıralamalar her yıl birkaç yüz
değişebilir; MARGIN ile "sınırda" bandı tanımlanır.
"""

# 2025 taban sıraları (kb/facts.yaml ile senkron tutulmalı)
DEPT_CUTOFFS_2025: dict[str, int] = {
    "bilgisayar": 1435,
    "yapay_zeka_veri": 1947,
    "elektronik_haberlesme": 2126,
    "ucak": 2235,
    "matematik": 3495,
    "endustri": 3723,
    "uzay": 3988,
    "kontrol_otomasyon": 4486,
    "makine": 6106,
    "elektrik": 6124,
}

# Taban her yıl oynar — bu pay kadar üstü "sınırda ama denenebilir" sayıyoruz
BORDERLINE_MARGIN = 1.25


def risk_band(rank: int | None, department: str = "bilgisayar") -> str:
    """Adayın hedef bölüm için risk bandı: safe | borderline | hard | unknown."""
    if rank is None:
        return "unknown"
    cutoff = DEPT_CUTOFFS_2025.get(department)
    if cutoff is None:
        return "unknown"
    if rank <= cutoff * 0.75:
        return "safe"
    if rank <= cutoff * BORDERLINE_MARGIN:
        return "borderline"
    return "hard"


def eligible_departments(rank: int | None) -> list[dict]:
    """Sıralamaya göre gerçekçi İTÜ bölümleri (risk bandıyla).

    Dönen liste cutoff sırasına göre; her öğe {department, cutoff_2025, band}.
    """
    if rank is None:
        return []
    out = []
    for dept, cutoff in sorted(DEPT_CUTOFFS_2025.items(), key=lambda kv: kv[1]):
        band = risk_band(rank, dept)
        if band in ("safe", "borderline"):
            out.append({"department": dept, "cutoff_2025": cutoff, "band": band})
    return out


def risk_bands_for(rank: int | None, departments: list[str]) -> list[dict]:
    """Adayın masasındaki HER bölüm için ayrı risk bandı.

    2800 sıralı robotik adayı örneği: bilgisayar=hard AMA kontrol_otomasyon=safe —
    tek 'Bilgisayar hard' göstermek adayı yanıltır.
    Dönen: [{department, band, cutoff_2025}] — cutoff bilinmeyen bölümler band=unknown.
    """
    seen: set[str] = set()
    out = []
    for dept in departments:
        if not dept or dept in seen:
            continue
        seen.add(dept)
        out.append({
            "department": dept,
            "band": risk_band(rank, dept),
            "cutoff_2025": DEPT_CUTOFFS_2025.get(dept),
        })
    return out


def academic_fit_summary(rank: int | None, rank_type: str = "unknown") -> str:
    """LLM prompt özeti için tek satırlık akademik durum."""
    if rank is None:
        return "Sıralama bilinmiyor — henüz bölüm uygunluğu hesaplanamaz."
    band = risk_band(rank, "bilgisayar")
    band_tr = {"safe": "GÜVENLİ", "borderline": "SINIRDA", "hard": "GERİDE"}[band]
    eligible = eligible_departments(rank)
    names = ", ".join(e["department"] for e in eligible[:5]) or "(daha yüksek tabanlı bölümler)"
    type_note = {"practice": " (deneme sıralaması — kesinleşmedi)",
                 "target": " (hedef sıralama — henüz gerçekleşmedi)"}.get(rank_type, "")
    return (f"Sıralama {rank}{type_note}: İTÜ Bilgisayar için {band_tr} bölgede "
            f"(2025 taban ~{DEPT_CUTOFFS_2025['bilgisayar']}). Erişilebilir İTÜ bölümleri: {names}.")
