"""Akademik uygunluk testleri — risk_band + eligible_departments (deterministik)."""
from app.profile.academic import eligible_departments, risk_band, academic_fit_summary


def test_risk_band_safe():
    assert risk_band(600, "bilgisayar") == "safe"
    assert risk_band(1000, "bilgisayar") == "safe"     # 1435*0.75 ≈ 1076


def test_risk_band_borderline():
    assert risk_band(1200, "bilgisayar") == "borderline"
    assert risk_band(1435, "bilgisayar") == "borderline"
    assert risk_band(1700, "bilgisayar") == "borderline"  # 1435*1.25 ≈ 1794


def test_risk_band_hard():
    assert risk_band(2500, "bilgisayar") == "hard"
    assert risk_band(10000, "bilgisayar") == "hard"


def test_risk_band_unknown():
    assert risk_band(None) == "unknown"
    assert risk_band(500, "olmayan_bolum") == "unknown"


def test_eligible_departments_top_rank():
    depts = eligible_departments(600)
    names = [d["department"] for d in depts]
    assert "bilgisayar" in names
    assert "yapay_zeka_veri" in names
    assert all(d["band"] in ("safe", "borderline") for d in depts)


def test_eligible_departments_mid_rank():
    depts = eligible_departments(3000)
    names = [d["department"] for d in depts]
    assert "bilgisayar" not in names          # 3000 > 1435*1.25
    assert "matematik" in names               # 3495 → borderline/safe bölgesi
    assert "makine" in names                  # 6106 → safe


def test_eligible_departments_none():
    assert eligible_departments(None) == []


def test_fit_summary_mentions_band():
    s = academic_fit_summary(600)
    assert "GÜVENLİ" in s
    s2 = academic_fit_summary(2500)
    assert "GERİDE" in s2
    s3 = academic_fit_summary(None)
    assert "bilinmiyor" in s3.lower()


def test_fit_summary_practice_note():
    s = academic_fit_summary(800, "practice")
    assert "deneme" in s.lower()
