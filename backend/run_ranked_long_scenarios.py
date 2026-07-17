r"""Ekli aday soru havuzuyla uzun, gerçek API sıralama senaryoları çalıştırır.

Varsayılan koşu:
  - 8 ayrı sıralama profili, profil başına 12 tur
  - 1 uzun oturum stres senaryosu, tüm ana kategorilerden en az bir soru
  - Markdown tam döküm ve JSON ham sonuç

Kullanım:
  .venv\Scripts\python.exe run_ranked_long_scenarios.py ^
    --questions-file "C:\path\pasted-text.txt" --api http://127.0.0.1:8002/api
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random
import re
import sys
import time
import urllib.error
import urllib.request
import uuid


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


SEED = 20260717
FORBIDDEN = (
    "doğru mu anladım",
    "bunu düşünür müsün",
    "güvenli bölgedesin",
    "yks'ye hazırlık",
    "kesinlikle en iyi",
    "garanti ederim",
)
SENSITIVE_TARGETING = (
    "muhafazakâr görün",
    "muhafazakar görün",
    "sana bakınca dindar",
    "kıyafetinden",
    "isminden din",
)


PERSONAS = [
    {
        "id": "rank_0005_ai_girisim",
        "rank": 5,
        "opening": "Merhaba, ben Defne. SAY sıralamam 5 geldi; yapay zekâ ve girişimcilikle ilgileniyorum, İTÜ Bilgisayar'ı değerlendiriyorum.",
        "focus": ["Kariyer ve mezuniyet sonrası", "Projeler ve araştırma imkânları", "İTÜ’nün diğer üniversitelerle karşılaştırılması"],
        "probes": [
            "Sıralamam 5 olduğuna göre İTÜ'nün başarı ödülü ve bursları bana ne sağlar?",
            "Koç Bilgisayar %100 burslu ile İTÜ Bilgisayar arasında kabul ve maliyet açısından durumum ne?",
            "Yapay zekâ alanında çalışabileceğim hoca ve laboratuvarlardan somut örnek verir misin?",
        ],
    },
    {
        "id": "rank_0035_arastirma",
        "rank": 35,
        "opening": "Selam, adım Arda. SAY sıralamam 35; araştırma, yurt dışı doktora ve güçlü akademik kadro benim için önemli.",
        "focus": ["Hocalar ve eğitim kalitesi", "Laboratuvarlar ve teknik olanaklar", "Erasmus ve yurt dışı fırsatları"],
        "probes": [
            "35. olduğum için İTÜ başarı bursunda hangi tutar ve koşullar geçerli?",
            "Hocalarımızla lisans öğrencisiyken proje yapmak gerçekten mümkün mü, örnek verir misin?",
            "İTÜ Bilgisayar'ı diğer güçlü okullardan sayılarla ayıran şey ne?",
        ],
    },
    {
        "id": "rank_0435_koc_karsilastirma",
        "rank": 435,
        "opening": "Merhaba, ben Selin. SAY sıralamam 435; İTÜ Bilgisayar ile Koç Bilgisayar arasında karar vermeye çalışıyorum.",
        "focus": ["İTÜ’nün diğer üniversitelerle karşılaştırılması", "Kariyer ve mezuniyet sonrası", "Kampüs hayatı"],
        "probes": [
            "435 sıralamayla Koç Bilgisayar %100 burslu gelir mi, İTÜ Bilgisayar için durumum ne?",
            "İTÜ'yü seçersem Koç'a göre somut olarak ne kazanırım?",
            "Kariyer Zirvesi'ne gelen şirketlerden örnek vererek anlatır mısın?",
        ],
    },
    {
        "id": "rank_0950_maddi_yurt",
        "rank": 950,
        "opening": "Merhaba, ben Mert. SAY sıralamam 950; ailemin bütçesi sınırlı, burs ve yurtta kalma imkânı kararımı çok etkiliyor.",
        "focus": ["Yurt ve barınma", "Kampüs hayatı", "İstanbul’da öğrenci olmak"],
        "probes": [
            "950 sıralamayla alabileceğim İTÜ başarı ödülünün tutarı ve ilk tercih koşulu nedir?",
            "Yurt başvurusu nasıl yapılır, oda, mutfak ve internet imkânları nedir?",
            "Kampüste uygun fiyatlı yemek ve market seçeneklerini isimleriyle söyler misin?",
        ],
    },
    {
        "id": "rank_1400_sinir_ders",
        "rank": 1400,
        "opening": "Selam, ben Ece. SAY sıralamam 1400; İTÜ Bilgisayar istiyorum ama tabana yakın olmam ve derslerin zorluğu beni düşündürüyor.",
        "focus": ["Üniversiteye kabul ve tercih süreci", "Derslerin zorluğu ve akademik hayat", "İngilizce eğitim ve hazırlık"],
        "probes": [
            "1400 sıralamayla İTÜ Bilgisayar gelir mi, dürüstçe söyler misin?",
            "Hazırlığı geçemezsem ne olur ve yeterliysem nasıl atlarım?",
            "Sınavların aynı haftaya yığılması ve çan sistemi gerçekten nasıl?",
        ],
    },
    {
        "id": "rank_1500_ai_alternatif",
        "rank": 1500,
        "opening": "Merhaba, ben Can. SAY sıralamam 1500; hedefim yapay zekâ ama ilk tercihim İTÜ Bilgisayar olsun istiyorum.",
        "focus": ["Üniversiteye kabul ve tercih süreci", "Uzmanlaşma alanları ve seçmeli dersler", "Bölümün içeriği hakkında"],
        "probes": [
            "1500 sıralamayla İTÜ Bilgisayar gerçekten gelir mi?",
            "Bilgisayar olmazsa İTÜ Yapay Zekâ ve Veri benim sıralamam için gerçekçi mi?",
            "Yapay zekâ alanında hoca, laboratuvar ve ders örnekleriyle iki yolu karşılaştırır mısın?",
        ],
    },
    {
        "id": "rank_2000_itu_icinde",
        "rank": 2000,
        "opening": "Selam, ben Zeynep. SAY sıralamam 2000; yazılım ve yapay zekâ istiyorum, mümkünse İTÜ içinde kalmak istiyorum.",
        "focus": ["Üniversiteye kabul ve tercih süreci", "Çift anadal, yandal ve bölüm değiştirme", "Doğal ve konuşma dilinde sorular"],
        "probes": [
            "2000 sıralamayla İTÜ Bilgisayar veya Yapay Zekâ ve Veri gelir mi?",
            "Bu sıralamayla İTÜ içinde hangi bölüm geçen yıl daha gerçekçiydi?",
            "Başka İTÜ bölümünden Bilgisayar'a geçerim diye tercih yapmak ne kadar riskli?",
        ],
    },
    {
        "id": "rank_2500_itu_icinde",
        "rank": 2500,
        "opening": "Merhaba, ben Emir. SAY sıralamam 2500; bilgisayar ve yazılım ilgim var ama İTÜ'den de vazgeçmek istemiyorum.",
        "focus": ["Üniversiteye kabul ve tercih süreci", "Bölümün içeriği hakkında", "İTÜ’nün diğer üniversitelerle karşılaştırılması"],
        "probes": [
            "2500 ile İTÜ Bilgisayar olur mu, boş umut vermeden anlatır mısın?",
            "İTÜ Yapay Zekâ ve Veri de olmazsa sıralamama uyan gerçekçi İTÜ yolu nedir?",
            "YTÜ Bilgisayar ile sıralamama uygun bir İTÜ bölümünü nasıl dürüstçe karşılaştırırsın?",
        ],
    },
]


def parse_questions(path: Path) -> dict[str, list[str]]:
    categories: dict[str, list[str]] = defaultdict(list)
    current = "Genel"
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if "?" not in line:
            current = line.rstrip(":")
            continue
        categories[current].append(line)
    return {
        category: questions
        for category, questions in categories.items()
        if not category.lower().startswith("bir yapay zekâ öğrenciyi")
    }


def request_json(url: str, payload: dict | None, timeout: int = 90) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else b""
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"API isteği başarısız: {last_error}")


def new_session(api: str) -> str:
    result = request_json(f"{api}/session/new", None, timeout=20)
    return str(result["session_id"])


def post_chat(api: str, session_id: str, text: str) -> dict:
    return request_json(f"{api}/chat", {"session_id": session_id, "text": text})


def token_similarity(left: str, right: str) -> float:
    fold = str.maketrans("çğıöşüâîûÇĞİÖŞÜÂÎÛ", "cgiosuaiucgiosuaiu")
    tokenize = lambda value: {
        token for token in re.split(r"[^a-z0-9]+", value.translate(fold).lower()) if len(token) >= 3
    }
    a, b = tokenize(left), tokenize(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def evaluate(result: dict, previous_answers: list[str]) -> dict:
    answer = str(result.get("response_text", ""))
    rag = result.get("rag") or {}
    facts = rag.get("facts") or []
    fallback = result.get("generation_fallback") or {}
    low = answer.casefold()
    similarities = [token_similarity(answer, old) for old in previous_answers[-3:]]
    checks = {
        "word_count": len(answer.split()),
        "over_limit": len(answer.split()) > 65,
        "empty": not answer.strip(),
        "generation_fallback": bool(fallback.get("used")),
        "rag_fact_count": len(facts),
        "rag_top_id": facts[0].get("id") if facts else None,
        "rag_top_label": facts[0].get("label") if facts else None,
        "forbidden": [phrase for phrase in FORBIDDEN if phrase in low],
        "sensitive_targeting": [phrase for phrase in SENSITIVE_TARGETING if phrase in low],
        "max_recent_similarity": round(max(similarities, default=0.0), 3),
        "near_duplicate": max(similarities, default=0.0) >= 0.86,
        "admission_check": result.get("admission_check") or {},
        "fact_gate": result.get("fact_gate") or {},
        "relevance": result.get("answer_relevance") or {},
        "repetition": result.get("repetition_check") or {},
        "fallback_ok": not bool(fallback.get("used")),
    }
    checks["ok"] = not any((
        checks["over_limit"], checks["empty"], checks["generation_fallback"],
        bool(checks["forbidden"]), bool(checks["sensitive_targeting"]), checks["near_duplicate"],
    ))
    return checks


def sample_questions(
    bank: dict[str, list[str]],
    persona: dict,
    count: int,
    rng: random.Random,
) -> list[tuple[str, str]]:
    chosen = [("Özel sıralama kontrolü", question) for question in persona["probes"]]
    focus = [category for category in persona["focus"] if bank.get(category)]
    all_categories = list(bank)
    index = 0
    while len(chosen) < count:
        category = focus[index % len(focus)] if focus else rng.choice(all_categories)
        available = [q for q in bank[category] if all(q != old for _, old in chosen)]
        if not available:
            category = rng.choice(all_categories)
            available = bank[category]
        chosen.append((category, rng.choice(available)))
        index += 1
    tail = chosen[3:]
    rng.shuffle(tail)
    chosen[3:] = tail
    return chosen[:count]


def build_stress_questions(bank: dict[str, list[str]], rng: random.Random) -> list[tuple[str, str]]:
    questions: list[tuple[str, str]] = []
    for category, items in bank.items():
        if items:
            questions.append((category, rng.choice(items)))
    extras = [
        ("Özel sosyal yaşam", "Kampüste sinema kulübü veya topluca maç izleyebileceğimiz bir yer var mı?"),
        ("Özel sosyal yaşam", "Pizza yiyebileceğim yer, gölet, stadyum ve marketlerden somut örnek verir misin?"),
        ("Özel açık ihtiyaç", "Kampüste cami ve fakültede mescit var mı?"),
        ("Özel açık ihtiyaç", "Ramazan ayında sınav sırasında namaz izni kesin veriliyor mu?"),
        ("Özel tekrar", "Hocalara ulaşmak gerçekten kolay mı?"),
        ("Özel tekrar", "Hocalarla e-posta veya birebir iletişim kurabilir miyim?"),
        ("Özel sıralama", "950 sıralamayla Koç Bilgisayar tam burslu ve İTÜ Bilgisayar için durumum ne?"),
        ("Özel sıralama", "950 sıralamaya göre İTÜ burs tutarım ve koşullarım ne?"),
    ]
    return questions + extras


def run_conversation(api: str, opening: str, questions: list[tuple[str, str]]) -> dict:
    session_id = new_session(api)
    rows: list[dict] = []
    previous_answers: list[str] = []
    for category, user_text in [("Açılış", opening), *questions]:
        started = time.monotonic()
        result = post_chat(api, session_id, user_text)
        elapsed = round(time.monotonic() - started, 2)
        checks = evaluate(result, previous_answers)
        answer = str(result.get("response_text", ""))
        previous_answers.append(answer)
        rows.append({
            "category": category,
            "question": user_text,
            "answer": answer,
            "elapsed_seconds": elapsed,
            "argument_id": (result.get("xai_meta") or {}).get("argument_id"),
            "route": (result.get("xai_meta") or {}).get("route") or result.get("route"),
            "profile_rank": (result.get("profile") or {}).get("yks_rank"),
            "academic": result.get("academic") or {},
            "checks": checks,
            "rag_topics": (result.get("rag") or {}).get("topics") or [],
        })
        status = "OK" if checks["ok"] else "UYARI"
        print(
            f"    {len(rows):02d} {status:5s} {elapsed:5.1f}s | "
            f"{checks['rag_top_id'] or '-':42.42s} | {user_text[:62]}"
        )
    return {"session_id": session_id, "turns": rows}


def summarize(results: list[dict]) -> dict:
    rows = [turn for item in results for turn in (item.get("result") or {}).get("turns", [])]
    warnings = Counter()
    for row in rows:
        checks = row["checks"]
        for key in ("over_limit", "empty", "generation_fallback", "near_duplicate"):
            if checks.get(key):
                warnings[key] += 1
        if checks.get("forbidden"):
            warnings["forbidden"] += 1
        if checks.get("sensitive_targeting"):
            warnings["sensitive_targeting"] += 1
        if checks.get("rag_fact_count") == 0:
            warnings["rag_empty"] += 1
    return {
        "conversations": len(results),
        "turns": len(rows),
        "ok_turns": sum(1 for row in rows if row["checks"]["ok"]),
        "warnings": dict(warnings),
        "fallback_turns": sum(1 for row in rows if row["checks"]["generation_fallback"]),
        "fact_gate_replacements": sum(1 for row in rows if row["checks"]["fact_gate"].get("replaced")),
        "relevance_repairs": sum(1 for row in rows if row["checks"]["relevance"].get("repaired")),
        "admission_repairs": sum(1 for row in rows if row["checks"]["admission_check"].get("repaired")),
    }


def write_report(path: Path, results: list[dict], summary: dict, question_count: int) -> None:
    lines = [
        "# Sıralama Duyarlı Uzun Senaryo Raporu",
        "",
        f"- Ekli aday soru havuzu: {question_count} soru",
        f"- Gerçek API konuşması: {summary['conversations']}",
        f"- Toplam tur: {summary['turns']}",
        f"- Mekanik olarak sorunsuz tur: {summary['ok_turns']}",
        f"- Model/API fallback: {summary['fallback_turns']}",
        f"- Sıralama gerçekliği müdahalesi: {summary['admission_repairs']}",
        f"- Fact gate müdahalesi: {summary['fact_gate_replacements']}",
        f"- Alaka müdahalesi: {summary['relevance_repairs']}",
        f"- Uyarılar: `{json.dumps(summary['warnings'], ensure_ascii=False)}`",
        "",
        "Mekanik `OK`, cevabın insan değerlendirmesinde kusursuz olduğu anlamına gelmez; tam konuşmalar aşağıdadır.",
        "",
    ]
    for item in results:
        lines.extend([f"## {item['id']} - {item['title']}", ""])
        if item.get("error"):
            lines.extend([f"**HATA:** {item['error']}", ""])
            continue
        result = item["result"]
        lines.extend([f"Session: `{result['session_id']}`", ""])
        for index, turn in enumerate(result["turns"], 1):
            checks = turn["checks"]
            flags = []
            if not checks["ok"]:
                flags.append("UYARI")
            if checks["generation_fallback"]:
                flags.append("fallback")
            if checks["near_duplicate"]:
                flags.append(f"tekrar={checks['max_recent_similarity']}")
            if checks["admission_check"].get("repaired"):
                flags.append(f"sıralama={checks['admission_check'].get('reason')}")
            flag_text = " | " + ", ".join(flags) if flags else ""
            lines.append(
                f"**Tur {index} [{turn['category']}]** `{turn['argument_id']}` "
                f"RAG: `{checks['rag_top_id']}` / `{checks['rag_top_label']}`{flag_text}"
            )
            lines.append(f"- Aday: {turn['question']}")
            lines.append(f"- Neco: {turn['answer']}")
            lines.append("")
        lines.append("---")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions-file", required=True, type=Path)
    parser.add_argument("--api", default="http://127.0.0.1:8002/api")
    parser.add_argument("--turns-per-persona", type=int, default=11)
    parser.add_argument("--persona-start", type=int, default=0)
    parser.add_argument("--persona-limit", type=int, default=len(PERSONAS))
    parser.add_argument("--skip-stress", action="store_true")
    parser.add_argument("--report", type=Path, default=Path("ranked_long_scenario_report.md"))
    parser.add_argument("--json", type=Path, default=Path("ranked_long_scenario_results.json"))
    args = parser.parse_args()

    bank = parse_questions(args.questions_file)
    question_count = sum(len(items) for items in bank.values())
    rng = random.Random(SEED)
    print(f"Soru havuzu: {len(bank)} kategori, {question_count} aday sorusu")

    results: list[dict] = []
    persona_start = max(0, min(args.persona_start, len(PERSONAS)))
    persona_end = max(persona_start, min(persona_start + args.persona_limit, len(PERSONAS)))
    personas = PERSONAS[persona_start:persona_end]
    total_runs = len(personas) + (0 if args.skip_stress else 1)
    for index, persona in enumerate(personas, 1):
        print(f"[{index}/{total_runs}] {persona['id']} rank={persona['rank']}")
        questions = sample_questions(bank, persona, args.turns_per_persona, rng)
        try:
            result = run_conversation(args.api, persona["opening"], questions)
            results.append({
                "id": persona["id"],
                "title": f"SAY {persona['rank']} profili",
                "rank": persona["rank"],
                "result": result,
                "error": None,
            })
        except Exception as exc:
            results.append({"id": persona["id"], "title": "", "rank": persona["rank"], "result": None, "error": str(exc)})
            print(f"    HATA: {exc}")

    if not args.skip_stress:
        print(f"[{len(personas) + 1}/{total_runs}] stress_rank_0950")
        stress_questions = build_stress_questions(bank, rng)
        try:
            stress = run_conversation(
                args.api,
                "Merhaba, ben Ada. SAY sıralamam 950; İTÜ Bilgisayar'ı ciddi düşünüyorum ve karar vermeden önce çok ayrıntılı soru soracağım.",
                stress_questions,
            )
            results.append({
                "id": "stress_rank_0950",
                "title": "Tek oturumda tüm ana kategoriler",
                "rank": 950,
                "result": stress,
                "error": None,
            })
        except Exception as exc:
            results.append({"id": "stress_rank_0950", "title": "", "rank": 950, "result": None, "error": str(exc)})
            print(f"    HATA: {exc}")

    summary = summarize(results)
    payload = {
        "run_id": uuid.uuid4().hex[:12],
        "seed": SEED,
        "api": args.api,
        "questions_file": str(args.questions_file),
        "summary": summary,
        "results": results,
    }
    args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(args.report, results, summary, question_count)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Rapor: {args.report}")
    print(f"Ham JSON: {args.json}")


if __name__ == "__main__":
    main()
