"""OpenAI LLM client wrapper — analyze_message + generate_response."""
import json
import re

from openai import AsyncOpenAI
from pydantic import ValidationError

from ..config import settings
from .prompts import ANALYZER_SYSTEM_PROMPT, RESPONSE_SYSTEM_TEMPLATE
from .schema import MessageAnalysis


class LLMClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def analyze_message(self, text: str, history: list[dict]) -> dict:
        """Adayın mesajını yapılandırılmış, Pydantic-doğrulanmış dict'e çevir.

        Bozuk JSON / eksik alan / yanlış tip → heuristik fallback. Asla exception sızdırmaz.
        """
        history_str = self._format_history(history, max_turns=6)
        user_prompt = f"KONUŞMA GEÇMİŞİ:\n{history_str}\n\nADAYIN SON MESAJI:\n{text}"

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": ANALYZER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=600,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content
            parsed = json.loads(raw)
            analysis = MessageAnalysis.model_validate(parsed)
            result = analysis.to_orchestrator_dict()
            # response_length'i LLM'e güvenme — kendimiz sayarız
            result["response_length"] = len(text.split())
            explicit_rank = self._extract_rank(text)
            if explicit_rank is not None:
                result["yks_rank_mentioned"] = explicit_rank
                result["yks_rank_type"] = result.get("yks_rank_type") or "actual"
                result["new_profile_info"] = True
            explicit_name = self._extract_display_name(text)
            if explicit_name is not None:
                result["display_name_mentioned"] = explicit_name
                result["new_profile_info"] = True
            return result
        except (json.JSONDecodeError, ValidationError) as e:
            return self._fallback_analysis(text, f"schema/json: {e}")
        except Exception as e:
            return self._fallback_analysis(text, str(e))

    async def generate_response(
        self,
        argument_id: str,
        argument_label: str,
        argument_technique: str,
        talking_points: list[str],
        expected_pushback: list[str],
        profile_summary: str,
        fsm_state: str,
        turn_count: int,
        main_indecision_axis: str,
        dominant_motivation: str,
        revealed_arguments: list[str],
        history: list[dict],
        rag_context: str = "",
    ) -> str:
        """Kararı LLM promptuna enjekte et, kısa bir cevap üret."""
        system_prompt = RESPONSE_SYSTEM_TEMPLATE.format(
            argument_id=argument_id,
            argument_label=argument_label,
            argument_technique=argument_technique,
            talking_points="\n".join(f"- {p}" for p in talking_points),
            expected_pushback=(
                "\n".join(f"- {p}" for p in expected_pushback)
                if expected_pushback else "(tanımlı özel itiraz yok)"
            ),
            profile_summary=profile_summary,
            fsm_state=fsm_state,
            turn_count=turn_count,
            main_indecision_axis=main_indecision_axis,
            dominant_motivation=dominant_motivation,
            revealed_arguments=", ".join(revealed_arguments[-6:]) if revealed_arguments else "(henüz yok)",
            rag_context=rag_context or (
                "Bu tur için kaynaklı fact bulunamadı. Sayı, garanti, bölüm adı veya kesin iddia verme; "
                "karar çerçevesi sun ve gerekirse resmi kaynaktan doğrulamayı öner."
            ),
        )

        # RAG context system prompt'un içinde. Tüm KB'yi körlemesine vermiyoruz.
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["text"]})

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200,
            )
            return self._sanitize(resp.choices[0].message.content or "")
        except Exception as e:
            return f"(Sistem hatası — {type(e).__name__}) Bir saniye, tekrar dener misin?"

    def _format_history(self, history: list[dict], max_turns: int = 6) -> str:
        recent = history[-max_turns:]
        if not recent:
            return "(konuşma henüz başlamadı)"
        lines = []
        for m in recent:
            role = "Aday" if m["role"] == "user" else "Bot"
            lines.append(f"{role}: {m['text']}")
        return "\n".join(lines)

    def _fallback_analysis(self, text: str, err: str) -> dict:
        # Basit heuristic — LLM/schema başarısız olursa asgari sinyaller
        text_lower = text.lower()
        intent = "neutral"
        if any(w in text_lower for w in ["merhaba", "selam"]):
            intent = "greeting"
        elif "?" in text or any(w in text_lower for w in ["nasıl", "neden", "ne kadar"]):
            intent = "seek_info"
        elif any(w in text_lower for w in ["istemiyorum", "olmaz", "hayır", "kabul etmiyorum"]):
            intent = "reject"
        elif any(w in text_lower for w in ["ama", "endişe", "korkuyorum", "zor"]):
            intent = "concern"
        elif any(w in text_lower for w in ["tamam", "anladım", "olur", "iyi", "güzel"]):
            intent = "engaged"

        # YKS rank
        rank = None
        rank = self._extract_rank(text)

        # İsim ("ben Deniz", "adım Zeynep", "ismim Can")
        name = self._extract_display_name(text)

        raw = {
            "intent": intent,
            "sentiment": 0.0,
            "asked_followup": "?" in text,
            "response_length": len(text.split()),
            "yks_rank_mentioned": rank,
            "yks_rank_type": "actual" if rank else None,
            "display_name_mentioned": name,
            "new_profile_info": rank is not None or name is not None,
            "conversation_language": "tr",
        }
        try:
            result = MessageAnalysis.model_validate(raw).to_orchestrator_dict()
        except ValidationError:
            result = MessageAnalysis().to_orchestrator_dict()
            result["response_length"] = len(text.split())
        result["_fallback_reason"] = err[:120]
        return result

    @staticmethod
    def _extract_rank(text: str) -> int | None:
        """Extract an explicitly stated YKS rank, including single-digit degrees."""
        low = text.lower()
        if not any(key in low for key in ("sıra", "sirala", "yks", "derece")):
            return None

        patterns = (
            r"(?:sıralamam|siralamam|sıralama|siralama|sıram|siram|derecem)\D{0,24}(\d{1,7})",
            r"(?:yks|türkiye|turkiye)\D{0,16}(\d{1,7})\D{0,12}(?:sıra|sira|derece)",
            r"(?:yks|yksde|yks'de|türkiye|turkiye)\D{0,16}(\d{1,7})\D{0,12}(?:oldum|geldim|geldi)",
            r"(\d{1,7})\D{0,8}(?:sıram|siram|sıradayım|siradayim|derecem)",
            r"(\d{1,7})\D{0,12}(?:oldum|geldim|geldi)\D{0,12}(?:yks|yksde|yks'de)",
        )
        for pattern in patterns:
            match = re.search(pattern, low, flags=re.IGNORECASE)
            if match:
                value = int(match.group(1))
                return value if value > 0 else None
        return None

    @staticmethod
    def _extract_display_name(text: str) -> str | None:
        """Extract self-introductions without treating ordinary 'ben ...' phrases as names."""
        patterns = (
            r"\b(?:adım|adim|ismim)\s+([a-zçğıöşü]{2,30})\b",
            r"\b(?:selam|merhaba)[,\s]+ben\s+([a-zçğıöşü]{2,30})\b",
            r"\bben\s+([a-zçğıöşü]{2,30})(?=\s+(?:ve|ama)\b|\s*[,!.?]|$)",
        )
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).title()
        return None

    def _sanitize(self, text: str) -> str:
        """Basit temizlik — banned openers, filler, uzun dangling cümleyi kırp."""
        text = text.strip()
        # Banned openers (LLM'in klasik gereksiz başlangıçları)
        banned_prefixes = [
            "elbette,", "tabii ki,", "harika bir soru,", "elbette!", "tabii!",
            "kesinlikle,", "kesinlikle!",
        ]
        low = text.lower()
        for p in banned_prefixes:
            if low.startswith(p):
                text = text[len(p):].lstrip(" ,")
                break

        # Fazla emoji'yi kaldır (V1 için kaba)
        text = re.sub(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF]", "", text)

        # Truncate at token cap — kesilmiş yarım cümleyi at
        if len(text) > 300:
            # Son noktalama yerinde kes
            m = re.search(r"[.!?…](?!.*[.!?…])", text[:300])
            if m:
                text = text[:m.end()]

        return text.strip()
