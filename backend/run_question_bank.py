"""Soru bankası kombinasyon koşucusu + KB kapsam analizi.

Ne yapar:
  1. Her persona için 8 kategoriden dengeli örneklenmiş soru dizisi üretir (seed'li — tekrarlanabilir).
  2. Soruları API'ye sırayla gönderir.
  3. Her cevabı otomatik değerlendirir:
       - fact_gate: temiz mi, cevap değiştirildi mi (riskli iddia yakalandı)?
       - RAG: kaynaklı fact bulundu mu (bulunamadıysa = KB BOŞLUĞU adayı)?
       - ethics + yasak kalıplar
       - konuşma uzunluk limiti
  4. Kategori bazlı kapsam raporu + KB boşluk listesi üretir.

Kullanım (backend çalışırken):
    .venv\\Scripts\\python.exe run_question_bank.py            # 6 persona x 6 soru = 42 turn
    .venv\\Scripts\\python.exe run_question_bank.py --full      # tüm 91 soru (tek persona rotasyonu)
Çıktı: question_bank_report.md
"""
import random
import sys

# Windows konsolu (cp1254) emoji basamıyor — stdout'u UTF-8'e zorla
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from question_bank import PERSONAS, QUESTION_BANK
from run_scenarios import new_session, post_chat

SEED = 42
QUESTIONS_PER_PERSONA = 6

# ============ LLM HAKEM ============
# Mekanik kontroller (gate temiz mi, kelime sayısı) ALAKA ölçmüyor —
# "kaliteli mi" sorusuna hoca e-postası cevabı tüm mekanik kontrollerden geçmişti.
# Hakem: her cevabı ikinci bir LLM "soruya cevap mı?" diye puanlar.

JUDGE_SYSTEM = """Sen bir tanıtım-danışmanlığı kalite hakemisin. Sana bir aday sorusu ve robotun cevabı verilecek.
SADECE şu JSON'u döndür:
{"relevance": 1-5, "helpful": 1-5, "verdict": "pass"|"fail", "reason": "tek cümle"}

Kriterler:
- relevance: Cevap SORULAN soruya mı cevap veriyor? Alakasız bilgi okumak (soruyla ilgisiz hoca/e-posta/laboratuvar listesi gibi) = 1-2.
- helpful: Aday bu cevapla bir şey öğrendi mi? "Bilgi yok, resmi sayfadan bak" tarzı kaçamak, soru makul bir tanıtım sorusuysa = 1-2.
- verdict=fail: relevance<=2 VEYA helpful<=2 VEYA cevapta absürtlük var (rastgele kişi adı/e-posta/iletişim bilgisi, konuyla ilgisiz sayılar, yarıda kesilme).
- Kısa/öz cevap ceza DEĞİL (sesli sistem, 65 kelime limiti var). Türkçe doğallık beklenir ama küçük kusurlar fail değildir.
"""


def judge_answer(question: str, answer: str) -> dict:
    """Cevabı gpt-4o-mini hakeme puanlat. Hata olursa nötr döner (koşuyu kırmaz)."""
    import json as _json
    try:
        from openai import OpenAI
        from app.config import settings
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": f"SORU: {question}\n\nCEVAP: {answer}"},
            ],
            temperature=0.0,
            max_tokens=150,
            response_format={"type": "json_object"},
        )
        out = _json.loads(resp.choices[0].message.content)
        out.setdefault("verdict", "pass")
        return out
    except Exception as e:
        return {"relevance": None, "helpful": None, "verdict": "error", "reason": str(e)[:80]}

FORBIDDEN_PHRASES = [
    "doğru mu anladım", "yks'ye hazırlık", "kesinlikle en iyi",
    "garanti ederim", "başaramazsın",
]


def build_scenarios(full: bool = False) -> list[dict]:
    rng = random.Random(SEED)
    categories = list(QUESTION_BANK.keys())
    scenarios = []

    if full:
        # Tüm soruları personalar arasında dönüşümlü dağıt
        all_q = [(cat, q) for cat in categories for q in QUESTION_BANK[cat]]
        chunks: list[list] = [[] for _ in PERSONAS]
        for i, item in enumerate(all_q):
            chunks[i % len(PERSONAS)].append(item)
        for persona, chunk in zip(PERSONAS, chunks):
            scenarios.append({"persona": persona, "questions": chunk})
    else:
        # Her persona: her koşuda farklı kategori karışımı (dengeli örnekleme)
        for i, persona in enumerate(PERSONAS):
            rng_p = random.Random(SEED + i)
            cats = rng_p.sample(categories, k=min(QUESTIONS_PER_PERSONA, len(categories)))
            questions = [(cat, rng_p.choice(QUESTION_BANK[cat])) for cat in cats]
            scenarios.append({"persona": persona, "questions": questions})
    return scenarios


def evaluate_turn(question: str, result: dict) -> dict:
    checks = {}
    fg = result.get("fact_gate", {}) or {}
    rag = result.get("rag", {}) or {}
    text = result.get("response_text", "")
    low = text.lower()

    checks["fact_gate_clean"] = bool(fg.get("clean", True))
    checks["fact_gate_replaced"] = bool(fg.get("replaced", False))
    checks["rag_fact_count"] = len(rag.get("facts", []))
    checks["kb_gap_candidate"] = checks["rag_fact_count"] == 0
    checks["forbidden_hit"] = [p for p in FORBIDDEN_PHRASES if p in low]
    checks["word_count"] = len(text.split())
    checks["over_word_limit"] = checks["word_count"] > 65
    checks["empty_or_error"] = (not text.strip()) or text.startswith("(Sistem hatası")
    checks["ok"] = (not checks["empty_or_error"]) and not checks["forbidden_hit"] and not checks["over_word_limit"]
    return checks


def main():
    # MALİYET VARSAYILANLARI: quick mod (2 persona × 4 soru) + hakem KAPALI.
    #   python run_question_bank.py             → ~8 turn  ≈ 16 istek  ≈ ~$0.01
    #   python run_question_bank.py --standard  → ~42 turn ≈ 84 istek  ≈ ~$0.07
    #   python run_question_bank.py --full      → 103 turn ≈ 206 istek ≈ ~$0.17
    #   --judge eklersen: +1 istek/cevap (≈ +%50 istek, hakem yalnızca büyük kontrollerde önerilir)
    full = "--full" in sys.argv
    standard = "--standard" in sys.argv
    use_judge = "--judge" in sys.argv
    quick = not (full or standard)

    global PERSONAS, QUESTIONS_PER_PERSONA
    if quick:
        PERSONAS = PERSONAS[:2]
        QUESTIONS_PER_PERSONA = 4

    scenarios = build_scenarios(full)
    total_turns = sum(len(s["questions"]) for s in scenarios) + len(scenarios)
    est_requests = total_turns * 2 + (total_turns if use_judge else 0)
    est_cost = est_requests * 0.0008  # gpt-4o-mini ortalama istek maliyeti (yaklaşık)
    mode = "QUICK" if quick else ("FULL" if full else "STANDARD")
    print(f"{len(scenarios)} persona, ~{total_turns} turn | mod={mode} hakem={'AÇIK' if use_judge else 'kapalı'}")
    print(f"TAHMİNİ MALİYET: ~{est_requests} istek ≈ ${est_cost:.2f} (gpt-4o-mini)\n")

    category_stats: dict[str, dict] = {
        cat: {"asked": 0, "ok": 0, "kb_gaps": [], "replaced": [], "forbidden": [], "judge_fails": []}
        for cat in QUESTION_BANK
    }
    transcript_rows = []

    for si, sc in enumerate(scenarios, 1):
        persona = sc["persona"]
        print(f"[{si}/{len(scenarios)}] {persona['id']}")
        sid = new_session()
        # Açılış
        opening_result = post_chat(sid, persona["opening"])
        transcript_rows.append({
            "persona": persona["id"], "category": "(açılış)", "q": persona["opening"],
            "a": opening_result["response_text"], "checks": evaluate_turn(persona["opening"], opening_result),
            "arg": opening_result["xai_meta"]["argument_id"], "sid": sid,
        })

        for cat, q in sc["questions"]:
            try:
                result = post_chat(sid, q)
            except Exception as e:
                print(f"    HATA ({cat}): {e}")
                category_stats[cat]["asked"] += 1
                continue
            checks = evaluate_turn(q, result)
            judge = judge_answer(q, result["response_text"]) if use_judge else {}
            checks["judge"] = judge
            stats = category_stats[cat]
            stats["asked"] += 1
            if checks["ok"] and judge.get("verdict") != "fail":
                stats["ok"] += 1
            if checks["kb_gap_candidate"]:
                stats["kb_gaps"].append(q)
            if checks["fact_gate_replaced"]:
                stats["replaced"].append(q)
            if checks["forbidden_hit"]:
                stats["forbidden"].append((q, checks["forbidden_hit"]))
            if judge.get("verdict") == "fail":
                stats["judge_fails"].append((q, judge.get("reason", ""), result["response_text"][:150]))
            transcript_rows.append({
                "persona": persona["id"], "category": cat, "q": q,
                "a": result["response_text"], "checks": checks,
                "arg": result["xai_meta"]["argument_id"], "sid": sid,
            })
            flag = "" if checks["ok"] else "  ⚠"
            gap = " [KB-BOŞLUK]" if checks["kb_gap_candidate"] else ""
            rep = " [GATE-DEĞİŞTİ]" if checks["fact_gate_replaced"] else ""
            jf = f" [HAKEM-FAIL: {judge.get('reason','')[:40]}]" if judge.get("verdict") == "fail" else ""
            print(f"    {cat:20s} | {q[:55]:57s}{flag}{gap}{rep}{jf}")
        print()

    # ============ RAPOR ============
    lines = ["# Soru Bankası Kapsam Raporu", ""]
    lines.append(f"Seed: {SEED} · Persona: {len(scenarios)} · Toplam soru: {sum(s['asked'] for s in category_stats.values())}")
    lines.append("")
    lines.append("## Kategori Özeti")
    lines.append("")
    lines.append("| Kategori | Sorulan | Sorunsuz | KB boşluğu | Gate değişimi | Hakem-fail |")
    lines.append("|---|---|---|---|---|---|")
    for cat, s in category_stats.items():
        if s["asked"] == 0:
            continue
        lines.append(f"| {cat} | {s['asked']} | {s['ok']} | {len(s['kb_gaps'])} | {len(s['replaced'])} | {len(s['judge_fails'])} |")
    lines.append("")

    all_judge_fails = [(cat, q, r, a) for cat, s in category_stats.items() for q, r, a in s["judge_fails"]]
    if all_judge_fails:
        lines.append("## ⚖️ HAKEM-FAIL (cevap soruya cevap değil / kaçamak / absürt)")
        lines.append("")
        for cat, q, reason, ans in all_judge_fails:
            lines.append(f"- **[{cat}]** {q}")
            lines.append(f"  - Hakem: {reason}")
            lines.append(f"  - Cevap: {ans}…")
        lines.append("")

    all_gaps = [(cat, q) for cat, s in category_stats.items() for q in s["kb_gaps"]]
    if all_gaps:
        lines.append("## 🔴 KB Boşluğu Adayları (RAG hiç fact bulamadı — facts.yaml'a içerik eklenmeli)")
        lines.append("")
        for cat, q in all_gaps:
            lines.append(f"- **[{cat}]** {q}")
        lines.append("")

    all_replaced = [(cat, q) for cat, s in category_stats.items() for q in s["replaced"]]
    if all_replaced:
        lines.append("## 🟡 Fact Gate Cevabı Değiştirdi (LLM kaynak dışına çıktı — KB'ye veri eklemek cevap kalitesini artırır)")
        lines.append("")
        for cat, q in all_replaced:
            lines.append(f"- **[{cat}]** {q}")
        lines.append("")

    lines.append("## Tam Döküm")
    lines.append("")
    current_persona = None
    for row in transcript_rows:
        if row["persona"] != current_persona:
            current_persona = row["persona"]
            lines.append(f"### {current_persona} — session `{row['sid']}`")
            lines.append("")
        c = row["checks"]
        badges = []
        if c["kb_gap_candidate"]:
            badges.append("🔴KB-boşluk")
        if c["fact_gate_replaced"]:
            badges.append("🟡gate-değişti")
        if c["forbidden_hit"]:
            badges.append(f"⛔yasak:{c['forbidden_hit']}")
        if c["over_word_limit"]:
            badges.append(f"📏{c['word_count']}kelime")
        badge_str = (" " + " ".join(badges)) if badges else ""
        lines.append(f"**[{row['category']}] 🧑:** {row['q']}")
        lines.append(f"**🤖 ({row['arg']}){badge_str}:** {row['a']}")
        lines.append("")

    with open("question_bank_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Rapor: question_bank_report.md")
    print(f"KB boşluğu adayı: {len(all_gaps)} · Gate değişimi: {len(all_replaced)}")


if __name__ == "__main__":
    main()
