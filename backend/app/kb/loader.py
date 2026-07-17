"""facts.yaml helpers.

- confidence: low → satırın sonuna "(doğrulanmalı — yaklaşık/topluluk verisi)" eklenir.
- Kaynak/yıl her satırın sonunda köşeli parantezle: [YÖK Atlas 2025]
- Dosya bir kez okunur, module-level cache'lenir (dev'de restart yeterli).
"""
from functools import lru_cache
from pathlib import Path

import yaml

_YAML_PATH = Path(__file__).parent / "facts.yaml"
_DATA_DIR = Path(__file__).parent / "data"


@lru_cache(maxsize=1)
def load_kb_data() -> dict:
    with open(_YAML_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=1)
def load_structured_kb_data() -> tuple[tuple[str, dict], ...]:
    if not _DATA_DIR.exists():
        return ()

    docs: list[tuple[str, dict]] = []
    for path in sorted(_DATA_DIR.glob("*.yaml")):
        with open(path, encoding="utf-8") as f:
            docs.append((path.stem, yaml.safe_load(f) or {}))
    return tuple(docs)


@lru_cache(maxsize=1)
def load_kb_facts() -> str:
    data = load_kb_data()

    lines = [
        "Yalnızca ihtiyaç olursa şu doğrulanmış verileri kullan. **BURADA OLMAYAN BİR SAYI KULLANMA.**",
        "",
    ]

    meta = data.get("meta", {})
    if meta.get("last_verified"):
        lines.append(f"(Bilgi tabanı son doğrulama: {meta['last_verified']})")
        lines.append("")

    for section in data.get("sections", []):
        lines.append(f"{section['title']}:")
        for fact in section.get("facts", []):
            text = fact["text"]
            src = fact.get("source", "")
            year = fact.get("year", "")
            conf = fact.get("confidence", "medium")
            tag = f" [{src} {year}]".rstrip() if src else ""
            low_note = " (doğrulanmalı — yaklaşık/topluluk verisi olarak çerçevele)" if conf == "low" else ""
            lines.append(f"- {text}{tag}{low_note}")
        lines.append("")

    return "\n".join(lines)


def flatten_facts() -> list[dict]:
    """facts.yaml içindeki tüm fact'leri topic/tag bilgisiyle düz listeye çevir."""
    data = load_kb_data()
    out: list[dict] = []
    for section in data.get("sections", []):
        section_title = section.get("title", "")
        section_topics = section.get("topics", [])
        section_tags = section.get("tags", [])
        for idx, fact in enumerate(section.get("facts", []), 1):
            item = dict(fact)
            item.setdefault("id", f"{slugify(section_title)}_{idx}")
            item["section"] = section_title
            item["topics"] = list(dict.fromkeys(
                item.get("topics", []) + section_topics + infer_topics(section_title, item.get("text", ""))
            ))
            item["tags"] = list(dict.fromkeys(item.get("tags", []) + section_tags))
            out.append(item)
    out.extend(_flatten_structured_sources())
    return out


def _flatten_structured_sources() -> list[dict]:
    out: list[dict] = []
    for doc_id, data in load_structured_kb_data():
        if data.get("facts"):
            out.extend(_flatten_generic_facts(doc_id, data))
        if data.get("faculty_members"):
            out.extend(_flatten_faculty_members(doc_id, data))
        if data.get("area_groups"):
            out.extend(_flatten_area_groups(doc_id, data))
    return out


def _flatten_generic_facts(doc_id: str, data: dict) -> list[dict]:
    """Flatten source-specific fact files while preserving applicability metadata."""
    meta = data.get("meta", {})
    out: list[dict] = []
    for idx, fact in enumerate(data.get("facts", []), 1):
        item = dict(fact)
        item.setdefault("id", f"{doc_id}_{idx}")
        item.setdefault("source", meta.get("source", ""))
        item.setdefault("source_url", meta.get("source_url", ""))
        item.setdefault("year", meta.get("year", ""))
        item.setdefault("confidence", meta.get("confidence", "high"))
        item.setdefault("section", meta.get("section", doc_id))
        item["topics"] = list(dict.fromkeys(item.get("topics", []) + meta.get("topics", [])))
        item["tags"] = list(dict.fromkeys(item.get("tags", []) + meta.get("tags", [])))
        out.append(item)
    return out


def _flatten_area_groups(doc_id: str, data: dict) -> list[dict]:
    meta = data.get("meta", {})
    out: list[dict] = []
    for idx, group in enumerate(data.get("area_groups", []), 1):
        item = dict(group)
        item.setdefault("id", f"{doc_id}_{item.get('id') or idx}")
        item.setdefault("source", meta.get("source", "İTÜ Bilgisayar Mühendisliği resmi"))
        item.setdefault("source_url", meta.get("source_url", ""))
        item.setdefault("year", meta.get("year", ""))
        item.setdefault("confidence", "high")
        item.setdefault("section", meta.get("section", "İTÜ Bilgisayar Mühendisliği Öğretim Üyeleri"))
        item["topics"] = list(dict.fromkeys(item.get("topics", []) + ["faculty", "labs"]))
        item["tags"] = list(dict.fromkeys(item.get("tags", []) + [item.get("area", "")]))
        out.append(item)
    return out


def _flatten_faculty_members(doc_id: str, data: dict) -> list[dict]:
    meta = data.get("meta", {})
    out: list[dict] = []
    for idx, member in enumerate(data.get("faculty_members", []), 1):
        name = member.get("name", "").strip()
        title = member.get("title", "").strip()
        role_group = member.get("role_group", meta.get("section", "")).strip()
        role_group_display = _ROLE_GROUP_LABELS.get(role_group, role_group)
        areas = [a.strip() for a in member.get("research_areas", []) if a and a.strip()]
        area_text = "; ".join(areas)

        if area_text:
            text = (
                f"{name}, İTÜ Bilgisayar Mühendisliği {role_group_display} içinde {title} olarak yer alır; "
                f"resmi sayfadaki araştırma alanları: {area_text}."
            )
        else:
            role = title or "öğretim elemanı"
            text = f"{name}, İTÜ Bilgisayar Mühendisliği {role_group_display} içinde {role} olarak yer alır."

        email = member.get("email", "")
        if email and email != "nan":
            text = f"{text} Resmi sayfada e-posta adresi {email} olarak verilmiştir."

        topics = ["faculty"]
        if areas:
            topics.append("labs")
        topics.extend(t for t in infer_topics(role_group, area_text) if t != "general")

        tags = [
            name,
            title,
            role_group,
            role_group_display,
            *areas,
            *member.get("tags", []),
            *_area_tags(areas),
        ]

        out.append({
            "id": member.get("id") or f"{doc_id}_{slugify(name) or idx}",
            "text": text,
            "source": member.get("source", meta.get("source", "İTÜ Bilgisayar Mühendisliği resmi")),
            "source_url": member.get("source_url", meta.get("source_url", "")),
            "profile_url": member.get("profile_url", ""),
            "email": email,
            "year": member.get("year", meta.get("year", "")),
            "confidence": member.get("confidence", "high"),
            "section": role_group,
            "topics": list(dict.fromkeys(topics)),
            "tags": [t for t in dict.fromkeys(tags) if t],
        })
    return out


_ROLE_GROUP_LABELS = {
    "Computer Engineering Department": "ana akademik kadrosu",
    "BIL Course Coordination Staff": "BIL ders koordinasyon kadrosu",
    "Part Time Faculty Members": "yarı zamanlı öğretim elemanları",
}


_AREA_TAG_ALIASES = {
    "artificial intelligence": ["ai", "yapay zeka"],
    "machine learning": ["ml", "makine öğrenmesi"],
    "deep learning": ["derin öğrenme"],
    "natural language processing": ["nlp", "doğal dil işleme"],
    "computer vision": ["görüntü işleme", "bilgisayarlı görü"],
    "image processing": ["görüntü işleme"],
    "data science": ["veri bilimi"],
    "data analytics": ["veri analitiği"],
    "bioinformatics": ["biyoinformatik"],
    "health informatics": ["sağlık bilişimi"],
    "medical image": ["tıbbi görüntüleme"],
    "robotics": ["robotik"],
    "cybersecurity": ["siber güvenlik"],
    "security": ["siber güvenlik", "güvenlik"],
    "computer networks": ["bilgisayar ağları", "ağ"],
    "software engineering": ["yazılım mühendisliği"],
    "software testing": ["yazılım testi"],
    "game": ["oyun"],
}


def _area_tags(areas: list[str]) -> list[str]:
    hay = " ".join(areas).lower()
    tags: list[str] = []
    for key, aliases in _AREA_TAG_ALIASES.items():
        if key in hay:
            tags.extend(aliases)
    return tags


def slugify(text: str) -> str:
    repl = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    s = text.translate(repl).lower()
    chars = [c if c.isalnum() else "_" for c in s]
    return "_".join("".join(chars).split("_")).strip("_")[:48] or "fact"


def infer_topics(section_title: str, fact_text: str) -> list[str]:
    """Eski facts.yaml formatı için kaba topic çıkarımı."""
    hay = f"{section_title} {fact_text}".lower()
    topics = []
    rules = {
        "ranking": ["sıralama", "taban", "yks", "puan", " say ", "sıra"],
        # NOT: çıplak "say" kaldırıldı — "sayfa/saygın/sayılabilir" ile substring-eşleşip
        # alakasız fact'lere ranking topic'i veriyordu (1.435 taban fact'ini top-6 dışına itti)
        "curriculum": ["müfredat", "ders", "programlama", "capstone", "çap", "çift anadal", "yandal"],
        "faculty": ["öğretim", "hoca", "akademik kadro", "öğretim üyesi"],
        "labs": ["laboratuvar", "araştırma", "robotik", "biyoinformatik", "doğal dil", "yapay zeka"],
        "career": ["kariyer", "mezun", "istihdam", "maaş", "iş"],
        "entrepreneurship": ["çekirdek", "girişim", "startup", "kuluçka", "yatırım"],
        "campus": ["kampüs", "kulüp", "takım", "ayazağa", "maslak"],
        "housing": ["yurt", "barınma", "yatak"],
        "scholarship": ["burs", "teşvik", "ücretsiz"],
        "comparison": ["qs", "odtü", "koç", "boğaziçi", "karşılaştırma"],
        "gamedev": ["oyun", "etkileşim teknolojileri", "otg"],
        "healthtech": ["sağlık", "tıp", "biyoinformatik"],
    }
    for topic, words in rules.items():
        if any(w in hay for w in words):
            topics.append(topic)
    return topics or ["general"]
