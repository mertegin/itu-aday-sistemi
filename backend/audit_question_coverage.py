"""Audit a plain-text candidate question bank against routing and RAG cards."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from app.kb.retriever import retrieve_facts
from app.profile.schema import CandidateProfile
from app.strategy.router import route_current_turn


ANALYSIS = {
    "asked_followup": True,
    "wants_detail": True,
    "concerns_mentioned": [],
}


def read_questions(path: Path) -> list[tuple[str, str]]:
    category = "Genel"
    questions: list[tuple[str, str]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.endswith("?"):
            questions.append((category, line))
        else:
            category = line
    return questions


def audit(questions: list[tuple[str, str]]) -> list[dict]:
    profile = CandidateProfile()
    rows: list[dict] = []
    for category, question in questions:
        if category.startswith("Bir yapay zekâ"):
            rows.append({
                "category": category,
                "question": question,
                "topic": "profile_probe",
                "argument": "socratic_probe",
                "fact_count": 0,
                "card_id": "profile_question",
                "top_fact": "",
                "covered": True,
            })
            continue
        route = route_current_turn(question, ANALYSIS, profile)
        argument_id = (
            route.forced_argument_id
            or (route.preferred_arguments[0] if route.preferred_arguments else "itu_compe_differentiators")
        )
        rag = retrieve_facts(question, profile, argument_id)
        cards = [fact for fact in rag.facts if fact.answer_card and fact.applicable]
        rows.append({
            "category": category,
            "question": question,
            "topic": route.primary_topic,
            "argument": argument_id,
            "fact_count": len(rag.facts),
            "card_id": cards[0].id if cards else "",
            "top_fact": rag.facts[0].id if rag.facts else "",
            "covered": bool(cards),
        })
    return rows


def markdown_report(rows: list[dict]) -> str:
    covered = sum(row["covered"] for row in rows)
    profile_probes = sum(row["topic"] == "profile_probe" for row in rows)
    candidate_rows = [row for row in rows if row["topic"] != "profile_probe"]
    candidate_covered = sum(row["covered"] for row in candidate_rows)
    lines = [
        "# RAG Soru Kapsam Raporu",
        "",
        f"- Toplam soru: {len(rows)}",
        f"- Adayın sorabileceği soru: {len(candidate_rows)}",
        f"- Aday sorularında kısa kanıt kartı bulunan: {candidate_covered}",
        f"- Profil keşfi için sistemin soracağı soru: {profile_probes}",
        f"- Kapsanmayan: {len(rows) - covered}",
        "",
        "## Kategori Özeti",
        "",
        "| Kategori | Soru | Kartlı | Oran |",
        "|---|---:|---:|---:|",
    ]
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)
    for category, category_rows in grouped.items():
        category_covered = sum(row["covered"] for row in category_rows)
        ratio = 100 * category_covered / len(category_rows)
        lines.append(f"| {category} | {len(category_rows)} | {category_covered} | %{ratio:.1f} |")

    arguments = Counter(row["argument"] for row in rows)
    lines.extend(["", "## En Çok Kullanılan Yollar", ""])
    for argument, count in arguments.most_common():
        lines.append(f"- `{argument}`: {count}")

    uncovered = [row for row in rows if not row["covered"]]
    lines.extend(["", "## Kanıt Kartı Bulunmayan Sorular", ""])
    if not uncovered:
        lines.append("Yok.")
    else:
        for row in uncovered:
            lines.append(
                f"- [{row['category']}] {row['question']} "
                f"(yol: `{row['argument']}`, üst bilgi: `{row['top_fact'] or 'yok'}`)"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question_file", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    rows = audit(read_questions(args.question_file))
    report = markdown_report(rows)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
