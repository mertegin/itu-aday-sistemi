"""FakeLLMClient — OpenAI'siz deterministic test client'ı.

Keyword tabanlı analiz + template cevap. Orchestrator'a inject edilerek kullanılır:
    orch = Orchestrator(llm_client=FakeLLMClient())
"""
import re


class FakeLLMClient:
    async def analyze_message(self, text: str, history: list[dict]) -> dict:
        low = text.lower()

        intent = "neutral"
        if any(w in low for w in ["merhaba", "selam"]):
            intent = "greeting"
        elif any(w in low for w in ["korkuyorum", "endişe", "zor değil mi", "güvenmiyorum", "baskı"]):
            intent = "concern"
        elif "?" in text or any(w in low for w in ["nasıl", "fark", "ne kadar", "var mı"]):
            intent = "seek_info"
        elif any(w in low for w in ["seviyorum", "istiyorum", "ilgim", "meraklıyım", "hedefim"]):
            intent = "engaged"
        elif any(w in low for w in ["istemiyorum", "bana göre değil", "vazgeçtim"]):
            intent = "reject"
        if any(w in low for w in ["görüşürüz", "hoşça kal", "konuşmayı bitirelim"]):
            intent = "close"

        rank = None
        if any(key in low for key in ["sıra", "sirala", "yks", "derece"]):
            m = re.search(
                r"(?:sıralamam|siralamam|sıralama|siralama|sıram|siram|derecem)\D{0,24}(\d{1,7})",
                low,
            )
            if not m:
                m = re.search(r"(\d{1,7})\D{0,8}(?:sıram|siram|sıradayım|siradayim|derecem)", low)
            if not m:
                m = re.search(r"(\d{1,7})\D{0,12}(?:oldum|geldim|geldi)\D{0,12}(?:yks|yksde|yks'de)", low)
            if not m:
                m = re.search(r"(?:yks|yksde|yks'de)\D{0,16}(\d{1,7})\D{0,12}(?:oldum|geldim|geldi)", low)
            if m:
                rank = int(m.group(1))

        name = None
        for pattern in (
            r"\b(?:adım|adim|ismim)\s+([a-zçğıöşü]{2,30})\b",
            r"\b(?:selam|merhaba)[,\s]+ben\s+([a-zçğıöşü]{2,30})\b",
            r"\bben\s+([a-zçğıöşü]{2,30})(?=\s+(?:ve|ama)\b|\s*[,!.?]|$)",
        ):
            nm = re.search(pattern, text, flags=re.IGNORECASE)
            if nm:
                name = nm.group(1).title()
                break

        field_alts = []
        if any(w in low for w in ["tıp", "doktor"]):
            field_alts.append("tıp")
        if "hukuk" in low:
            field_alts.append("hukuk")

        univ_alts = []
        for u in ["koç", "koc", "boğaziçi", "bogazici", "odtü", "odtu", "bilkent", "ytü", "ytu"]:
            if u in low:
                univ_alts.append(u.replace("ç", "c").replace("ğ", "g").replace("ü", "u").replace("ö", "o"))
        univ_alts = list(dict.fromkeys(univ_alts))

        dept_alts = []
        if any(w in low for w in ["yapay zeka müh", "yapay zeka mühendis", "yz müh"]):
            dept_alts.append("yapay_zeka")
        if "elektronik" in low:
            dept_alts.append("elektronik")

        motivation = {"money": 0.0, "science": 0.0, "prestige": 0.0, "interest": 0.0, "family": 0.0,
                      "social_impact": 0.0, "entrepreneurship": 0.0, "abroad": 0.0, "job_security": 0.0}
        if any(w in low for w in ["para", "maaş", "kazan"]):
            motivation["money"] = 0.8
        if any(w in low for w in ["araştırma", "akademi", "doktora", "bilim"]):
            motivation["science"] = 0.8
        if any(w in low for w in ["ailem", "babam", "annem"]):
            motivation["family"] = 0.7
        if any(w in low for w in ["seviyorum", "ilgim", "meraklı"]):
            motivation["interest"] = 0.6
        if any(w in low for w in ["şirket kur", "girişim", "startup"]):
            motivation["entrepreneurship"] = 0.8
        if any(w in low for w in ["yardım etmek", "topluma", "fayda"]):
            motivation["social_impact"] = 0.7
        if "yurt dışı" in low or "yurtdışı" in low:
            motivation["abroad"] = 0.7
        if any(w in low for w in ["garanti meslek", "işsiz kal"]):
            motivation["job_security"] = 0.8

        constraints = {"city_istanbul": None, "public_university": None, "cost_sensitivity": None,
                       "housing_needed": None, "family_influence": None, "english_medium": None,
                       "abroad_goal": None, "campus_social": None}
        if "istanbul" in low:
            constraints["city_istanbul"] = 0.8
        if any(w in low for w in ["maddi", "burs", "ücret", "maliyet"]):
            constraints["cost_sensitivity"] = 0.8
        if "devlet" in low:
            constraints["public_university"] = 0.8
        if "yurt" in low and "yurt dışı" not in low:
            constraints["housing_needed"] = True
        if any(w in low for w in ["ailem", "babam", "annem"]):
            constraints["family_influence"] = 0.7
        if "ingilizce" in low:
            constraints["english_medium"] = 0.8
        if "yurt dışı" in low or "yurtdışı" in low:
            constraints["abroad_goal"] = 0.7

        must_have = []
        deal_breakers = []
        if "olmazsa olmaz" in low or "şart" in low:
            must_have.append(text[:60])
        if "istemiyorum" in low or "asla" in low:
            deal_breakers.append(text[:60])

        interests = []
        for kw, key in [("yazılım", "software"), ("yapay zeka", "ai"), ("oyun", "gamedev"),
                        ("donanım", "hardware"), ("elektronik", "hardware"), ("robotik", "robotics"),
                        ("siber", "cybersec"), ("girişim", "entrepreneurship"), ("araştırma", "research"),
                        ("yurt dışı", "abroad")]:
            if kw in low:
                interests.append(key)

        concerns = []
        if any(w in low for w in ["matematik", "kalırsam"]):
            concerns.append("math")
        if any(w in low for w in ["zor", "korkuyorum"]):
            concerns.append("difficulty")
        if any(w in low for w in ["ailem", "babam", "baskı"]):
            concerns.append("family")
        if any(w in low for w in ["maddi", "para sıkınt", "karşılayam", "ödeyem", "geçinem"]):
            concerns.append("cost")

        retracting = any(w in low for w in ["vazgeçtim", "düşünmüyorum", "istemiyorum", "eledim"])
        retractions = {
            "field_alternatives": field_alts if retracting else [],
            "university_alternatives": univ_alts if retracting else [],
            "department_alternatives": dept_alts if retracting else [],
        }
        concerns_resolved = []
        if any(w in low for w in ["artık sorun değil", "kaygım kalmadı", "korkmuyorum"]):
            concerns_resolved = concerns or ["difficulty"]

        decision_status = "none"
        if any(w in low for w in ["itü bilgisayar yazacağım", "itü bilgisayar birinci tercih", "itü bilgisayarı seçtim"]):
            decision_status = "itu_compe_committed"
        elif any(w in low for w in ["elektronik yazacağım", "başka bölümü seçtim"]):
            decision_status = "other_committed"
        elif any(w in low for w in ["karar veremiyorum", "hala kararsızım"]):
            decision_status = "still_deciding"

        reaction = {
            "engaged": "accepted",
            "seek_info": "curious",
            "concern": "objection",
            "reject": "rejected",
        }.get(intent, "not_applicable" if not history else "neutral")
        relevance = 0.8 if history and intent not in ("greeting", "close") else 0.5
        if any(w in low for w in ["neyse", "konuyu değiştirelim", "şaka şaka"]):
            reaction = "topic_shift"
            relevance = 0.2

        return {
            "intent": intent,
            "sentiment": 0.3 if intent == "engaged" else (-0.3 if intent in ("concern", "reject") else 0.0),
            "asked_followup": "?" in text,
            "response_length": len(text.split()),
            "yks_rank_mentioned": rank,
            "yks_rank_type": "actual" if rank else None,
            "display_name_mentioned": name,
            "field_signals": {"engineering_certain": None, "field_alternatives_mentioned": field_alts},
            "university_signals": {"itu_certain": None, "university_alternatives_mentioned": univ_alts},
            "department_signals": {"compe_certain": None, "department_alternatives_mentioned": dept_alts},
            "motivation_signals": motivation,
            "constraint_signals": constraints,
            "interests_mentioned": interests,
            "experience_hints": "unknown",
            "concerns_mentioned": concerns,
            "must_have_mentioned": must_have,
            "deal_breakers_mentioned": deal_breakers,
            "retractions": retractions,
            "concerns_resolved": concerns_resolved,
            "decision_status": decision_status,
            "new_profile_info": bool(rank or name or field_alts or univ_alts or dept_alts or interests),
            "wants_detail": intent == "seek_info",
            "reception_signal": 0.7 if intent == "engaged" else (0.3 if intent in ("concern", "reject") else 0.5),
            "response_relevance": relevance,
            "argument_reaction": reaction,
            "conversation_language": "tr",
        }

    async def generate_response(self, argument_id: str = "", argument_label: str = "", **kwargs) -> str:
        return f"[fake-yanit:{argument_id}] Test cevabı — {argument_label}."
