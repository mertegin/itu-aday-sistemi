"""Senaryo koşusu + OTOMATİK KALİTE DEĞERLENDİRMESİ.

Her senaryo için kontrol edilir:
  1. PROFİL   — rank/alternatif/motivasyon/kaygı doğru extract edildi mi?
  2. ARGÜMAN  — beklenen argüman(lar) seçildi mi, yasaklılar seçilmedi mi?
  3. ETİK     — bot cevaplarında ihlal/yasak kalıp var mı?
  4. DOĞRULUK — sıralama yorumu yanlış mı ("sınırda/yetersiz" hataları)?

Kullanım (backend çalışırken):
    .venv\\Scripts\\python.exe run_eval.py
Çıktı: eval_report.md + konsol PASS/FAIL özeti. Exit code: fail sayısı.
"""
import sys

sys.path.insert(0, ".")  # app importları için

from run_scenarios import SCENARIOS, run_scenario
from app.guardrails.ethics import EthicsFilter

# ============ BEKLENTİLER ============
# must_select_any: konuşma boyunca EN AZ BİRİ seçilmiş olmalı
# must_not_select: HİÇBİRİ seçilmemiş olmalı
# profile: final profildeki beklenen değerler
# forbidden_phrases: bot cevaplarında geçmemesi gereken kalıplar (lower-case aranır)

EXPECTATIONS = {
    "S01_top1000_yazilim": {
        "profile": {"yks_rank": 600},
        "must_select_any": ["compe_priority_top1000"],
        "must_not_select": ["concern_family_pressure", "concern_math_difficulty"],
        "forbidden_phrases": ["sınırda", "yeterli değil", "yetersiz"],
    },
    "S02_tip_muhendislik": {
        "profile": {"yks_rank": 1200, "field_alternatives_contains": "tip"},  # canonical (normalize.py)
        "must_select_any": ["med_vs_eng_health_tech", "compe_borderline_1000_1500"],
        "must_not_select": ["concern_family_pressure"],
        "forbidden_phrases": ["tıp için yeterli olmayabilir", "tıp için yetersiz", "tıbba yetmez"],
    },
    "S03_koc_alternatifi": {
        "profile": {"yks_rank": 800, "university_alternatives_contains": "koc"},
        "must_select_any": ["koc_vs_itu_value"],
        "forbidden_phrases": ["koç kötü", "koç zayıf"],
    },
    "S04_matematik_kaygisi": {
        "profile": {"yks_rank": 1400, "concerns_contains": "math"},
        "must_select_any": ["concern_math_difficulty"],
        "must_not_select": ["concern_family_pressure"],
        "forbidden_phrases": ["başaramazsın", "yapamazsın", "senin için zor olur"],
    },
    "S05_yz_vs_compe": {
        "profile": {"yks_rank": 1800, "department_alternatives_contains": "yapay_zeka"},
        "must_select_any": ["ai_vs_compe_foundation"],
        "must_not_select": ["concern_family_pressure"],
        "forbidden_phrases": [],
    },
    "S06_elektronik_ilgisi": {
        "profile": {"yks_rank": 3000},
        "must_select_any": ["electronics_vs_compe_overlap", "balanced_perspective"],
        "must_not_select": ["concern_family_pressure", "compe_priority_top1000"],
        "forbidden_phrases": [],
    },
    "S07_para_motivasyonu": {
        "profile": {"yks_rank": 900, "dominant_motivation": "money"},
        "must_select_any": ["money_motivated_data"],
        "must_not_select": ["concern_family_pressure", "concern_math_difficulty"],
        "forbidden_phrases": [],
    },
    "S08_bilim_akademi": {
        "profile": {"yks_rank": 700, "dominant_motivation": "science"},
        "must_select_any": ["science_motivated_labs"],
        "must_not_select": ["concern_family_pressure", "concern_math_difficulty"],
        "forbidden_phrases": [],
    },
    "S09_aile_baskisi": {
        "profile": {"yks_rank": 1100, "concerns_contains": "family"},
        "must_select_any": ["concern_family_pressure"],
        "forbidden_phrases": ["odtü kötü", "odtü zayıf", "odtü'den iyi", "odtüden iyi"],
    },
    "S10_kararsiz_siralamasiz": {
        "profile": {},  # rank belirsiz kalabilir (deneme aralığı verildi)
        "must_not_select": ["compe_priority_top1000"],
        "max_rank_probe": 2,
        "forbidden_phrases": [],
    },
}


def eval_scenario(sc: dict, result: dict, ethics: EthicsFilter) -> list[dict]:
    """Bir senaryonun tüm kontrolleri. Her kontrol: {check, ok, detail}."""
    exp = EXPECTATIONS.get(sc["id"], {})
    checks = []
    profile = result["final_profile"]
    ind = profile.get("indecision", {})
    picked = [t["argument"] for t in result["turns"]]
    bot_texts = [t["bot"] for t in result["turns"]]

    # --- 1. PROFİL ---
    pexp = exp.get("profile", {})
    if "yks_rank" in pexp:
        ok = profile.get("yks_rank") == pexp["yks_rank"]
        checks.append({"check": f"profil: yks_rank == {pexp['yks_rank']}", "ok": ok,
                       "detail": f"got {profile.get('yks_rank')}"})
    if "field_alternatives_contains" in pexp:
        want = pexp["field_alternatives_contains"]
        ok = any(want in a for a in ind.get("field_alternatives", []))
        checks.append({"check": f"profil: alan alternatifi '{want}'", "ok": ok,
                       "detail": str(ind.get("field_alternatives"))})
    if "university_alternatives_contains" in pexp:
        want = pexp["university_alternatives_contains"]
        ok = any(want in a for a in ind.get("university_alternatives", []))
        checks.append({"check": f"profil: üniv alternatifi '{want}'", "ok": ok,
                       "detail": str(ind.get("university_alternatives"))})
    if "department_alternatives_contains" in pexp:
        want = pexp["department_alternatives_contains"]
        ok = any(want in a for a in ind.get("department_alternatives", []))
        checks.append({"check": f"profil: bölüm alternatifi '{want}'", "ok": ok,
                       "detail": str(ind.get("department_alternatives"))})
    if "concerns_contains" in pexp:
        want = pexp["concerns_contains"]
        ok = want in profile.get("concerns", [])
        checks.append({"check": f"profil: kaygı '{want}'", "ok": ok,
                       "detail": str(profile.get("concerns"))})
    if "dominant_motivation" in pexp:
        mot = ind.get("motivation", {})
        dom = max(mot.items(), key=lambda kv: kv[1])[0] if mot and max(mot.values()) >= 0.15 else "unknown"
        ok = dom == pexp["dominant_motivation"]
        checks.append({"check": f"profil: dominant motivasyon == {pexp['dominant_motivation']}", "ok": ok,
                       "detail": f"got {dom}"})

    # --- 2. ARGÜMAN ---
    for want in exp.get("must_select_any", []):
        pass  # tek tek değil, any olarak aşağıda
    if exp.get("must_select_any"):
        ok = any(a in picked for a in exp["must_select_any"])
        checks.append({"check": f"argüman: {exp['must_select_any']} içinden en az biri seçilmeli", "ok": ok,
                       "detail": f"seçilenler: {picked}"})
    for banned in exp.get("must_not_select", []):
        ok = banned not in picked
        checks.append({"check": f"argüman: '{banned}' SEÇİLMEMELİ", "ok": ok,
                       "detail": f"seçilenler: {picked}"})
    if "max_rank_probe" in exp:
        count = picked.count("rank_probe")
        ok = count <= exp["max_rank_probe"]
        checks.append({"check": f"argüman: rank_probe ≤ {exp['max_rank_probe']}", "ok": ok,
                       "detail": f"{count} kez"})

    # --- 3. ETİK ---
    for i, text in enumerate(bot_texts, 1):
        r = ethics.check(text)
        if not r["clean"]:
            checks.append({"check": f"etik: turn {i} ihlalsiz olmalı", "ok": False,
                           "detail": str(r["violations"])})
    else:
        checks.append({"check": "etik: tüm turlar temiz", "ok": all(ethics.check(t)["clean"] for t in bot_texts),
                       "detail": ""})
    low_all = " ".join(bot_texts).lower()
    if "doğru mu anladım" in low_all:
        checks.append({"check": "stil: 'doğru mu anladım' kalıbı yok", "ok": False, "detail": "bulundu"})
    if "yks'ye hazırlık" in low_all:
        checks.append({"check": "bağlam: 'YKS'ye hazırlık' ifadesi yok", "ok": False, "detail": "bulundu"})

    # --- 4. DOĞRULUK (yasak ifadeler) ---
    for phrase in exp.get("forbidden_phrases", []):
        ok = phrase not in low_all
        checks.append({"check": f"doğruluk: '{phrase}' geçmemeli", "ok": ok, "detail": ""})

    return checks


def main():
    ethics = EthicsFilter()
    all_results = []
    total_pass = total_fail = 0

    print(f"{len(SCENARIOS)} senaryo koşulup değerlendirilecek...\n")
    for i, sc in enumerate(SCENARIOS, 1):
        print(f"[{i}/{len(SCENARIOS)}] {sc['id']}")
        try:
            result = run_scenario(sc)
        except Exception as e:
            print(f"    KOŞU HATASI: {e}")
            all_results.append({"scenario": sc, "checks": [{"check": "koşu", "ok": False, "detail": str(e)}]})
            total_fail += 1
            continue
        checks = eval_scenario(sc, result, ethics)
        n_ok = sum(1 for c in checks if c["ok"])
        n_bad = len(checks) - n_ok
        total_pass += n_ok
        total_fail += n_bad
        status = "PASS" if n_bad == 0 else f"FAIL ({n_bad})"
        print(f"    {status} — {n_ok}/{len(checks)} kontrol")
        for c in checks:
            if not c["ok"]:
                print(f"      ✗ {c['check']} | {c['detail']}")
        all_results.append({"scenario": sc, "checks": checks})
        print()

    # Markdown rapor
    lines = ["# Otomatik Kalite Değerlendirme Raporu", ""]
    lines.append(f"**Toplam kontrol:** {total_pass + total_fail} · **Geçen:** {total_pass} · **Kalan:** {total_fail}")
    lines.append("")
    for r in all_results:
        sc = r["scenario"]
        n_bad = sum(1 for c in r["checks"] if not c["ok"])
        icon = "✅" if n_bad == 0 else "❌"
        lines.append(f"## {icon} {sc['id']} — {sc['title']}")
        lines.append("")
        for c in r["checks"]:
            mark = "✓" if c["ok"] else "✗"
            detail = f" — {c['detail']}" if c["detail"] and not c["ok"] else ""
            lines.append(f"- {mark} {c['check']}{detail}")
        lines.append("")

    with open("eval_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"=== TOPLAM: {total_pass} geçti, {total_fail} kaldı → eval_report.md ===")
    sys.exit(min(total_fail, 250))


if __name__ == "__main__":
    main()
