"""Normalizasyon katmanı testleri — varyant → canonical + hedef/alternatif ayrımı."""
import pytest

from app.orchestrator import Orchestrator
from app.profile.academic import risk_bands_for
from app.profile.normalize import normalize_department, normalize_field, normalize_university
from app.profile.schema import CandidateProfile
from tests.fake_llm import FakeLLMClient


# ============ BÖLÜM ============

@pytest.mark.parametrize("raw", [
    "yapay_zeka", "veri_mühendisliği", "veri_muhendisligi", "YZ", "ai",
    "Yapay Zeka ve Veri Mühendisliği", "veri bilimi",
])
def test_dept_ai_family(raw):
    assert normalize_department(raw) == "yapay_zeka_veri"


@pytest.mark.parametrize("raw", [
    "bilgisayar", "bilgisayar_mühendisliği", "Bilgisayar Mühendisliği", "compe", "CS",
])
def test_dept_compe_family(raw):
    assert normalize_department(raw) == "bilgisayar"


@pytest.mark.parametrize("raw,expected", [
    ("elektronik", "elektronik_haberlesme"),
    ("Elektronik-Haberleşme", "elektronik_haberlesme"),
    ("robotik", "kontrol_otomasyon"),
    ("kontrol ve otomasyon", "kontrol_otomasyon"),
    ("makine mühendisliği", "makine"),
    ("uçak", "ucak"),
])
def test_dept_various(raw, expected):
    assert normalize_department(raw) == expected


def test_dept_unknown_returns_none():
    assert normalize_department("astroloji bölümü") is None
    assert normalize_department("") is None


# ============ ÜNİVERSİTE ============

@pytest.mark.parametrize("raw", ["koç", "koc", "Koç Üniversitesi", "KOC"])
def test_univ_koc_family(raw):
    assert normalize_university(raw) == "koc"


@pytest.mark.parametrize("raw,expected", [
    ("boğaziçi", "bogazici"),
    ("ODTÜ", "odtu"),
    ("metu", "odtu"),
    ("yıldız teknik", "ytu"),
    ("İstanbul Teknik Üniversitesi", "itu"),
])
def test_univ_various(raw, expected):
    assert normalize_university(raw) == expected


# ============ ALAN ============

@pytest.mark.parametrize("raw", ["tıp", "tip", "doktorluk", "Tıp Fakültesi", "medicine"])
def test_field_tip_family(raw):
    assert normalize_field(raw) == "tip"


# ============ HEDEF/ALTERNATİF AYRIMI (orchestrator entegrasyonu) ============

def _orch() -> Orchestrator:
    return Orchestrator(llm_client=FakeLLMClient())


def _analysis_with_depts(alts, target=None):
    return {
        "department_signals": {
            "compe_certain": None,
            "target_department_mentioned": target,
            "department_alternatives_mentioned": alts,
        },
    }


def test_compe_in_alternatives_becomes_target():
    """'bilgisayar' alternatif listesine gelirse: alternatives'e GİRMEZ, hedefe yazılır."""
    orch = _orch()
    p = CandidateProfile()
    orch._update_profile_from_analysis(p, _analysis_with_depts(["bilgisayar_mühendisliği", "yapay_zeka"]), turn=1)
    assert "bilgisayar" not in p.indecision.department_alternatives
    assert p.indecision.target_department == "bilgisayar"
    assert p.indecision.department_alternatives == ["yapay_zeka_veri"]


def test_variant_dedup_via_canonical():
    """'yapay_zeka' + 'veri_mühendisliği' iki turda gelirse tek canonical kayıt olmalı."""
    orch = _orch()
    p = CandidateProfile()
    orch._update_profile_from_analysis(p, _analysis_with_depts(["yapay_zeka"]), turn=1)
    orch._update_profile_from_analysis(p, _analysis_with_depts(["veri_mühendisliği"]), turn=2)
    assert p.indecision.department_alternatives == ["yapay_zeka_veri"]


def test_explicit_target_recorded():
    orch = _orch()
    p = CandidateProfile()
    orch._update_profile_from_analysis(p, _analysis_with_depts([], target="elektronik"), turn=1)
    assert p.indecision.target_department == "elektronik_haberlesme"


def test_itu_never_in_university_alternatives():
    orch = _orch()
    p = CandidateProfile()
    analysis = {
        "university_signals": {
            "itu_certain": None,
            "university_alternatives_mentioned": ["İstanbul Teknik Üniversitesi", "koç"],
        },
    }
    orch._update_profile_from_analysis(p, analysis, turn=1)
    assert p.indecision.university_alternatives == ["koc"]


# ============ ÇOKLU RİSK BANDI ============

def test_risk_bands_for_robotics_candidate():
    """2800 sıralı robotik aday: bilgisayar hard AMA kontrol_otomasyon safe görünmeli."""
    bands = risk_bands_for(2800, ["bilgisayar", "kontrol_otomasyon", "elektronik_haberlesme"])
    by_dept = {b["department"]: b["band"] for b in bands}
    assert by_dept["bilgisayar"] == "hard"
    assert by_dept["kontrol_otomasyon"] == "safe"      # taban ~4486, 2800 rahat
    assert by_dept["elektronik_haberlesme"] == "hard"  # taban ~2126, 2800 geride (2126*1.25≈2657)


def test_risk_bands_dedup_and_unknown():
    bands = risk_bands_for(1000, ["bilgisayar", "bilgisayar", "siber_guvenlik"])
    assert len(bands) == 2  # dedup
    by_dept = {b["department"]: b["band"] for b in bands}
    assert by_dept["siber_guvenlik"] == "unknown"  # cutoff bilinmiyor
