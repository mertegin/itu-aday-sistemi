"""API endpoint testleri — FakeLLM ile gerçek OpenAI çağrısı olmadan."""
import httpx
import pytest

from app.api import routes
from app.database import init_db
from app.main import app
from .fake_llm import FakeLLMClient


@pytest.fixture(autouse=True)
def _fake_llm():
    """Global orchestrator'ın LLM'ini fake ile değiştir."""
    original = routes._orchestrator.llm
    routes._orchestrator.llm = FakeLLMClient()
    yield
    routes._orchestrator.llm = original


@pytest.fixture
async def client():
    await init_db()  # ASGITransport lifespan çalıştırmaz — tabloları elle kur
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def test_health(client):
    r = await client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


async def test_session_new(client):
    r = await client.post("/api/session/new")
    assert r.status_code == 200
    assert r.json()["session_id"].startswith("sess_")


async def test_fsm_definition(client):
    r = await client.get("/api/fsm")
    assert r.status_code == 200
    data = r.json()
    assert len(data["states"]) == 11
    assert len(data["transitions"]) > 20
    assert all("from" in t and "to" in t and "trigger" in t for t in data["transitions"])


async def test_chat_creates_session_and_responds(client):
    r = await client.post("/api/chat", json={"text": "Merhaba, ben Deniz. Sıralamam 800."})
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"].startswith("sess_")
    assert data["response_text"]
    assert data["turn_count"] == 1
    assert data["profile"]["yks_rank"] == 800
    assert data["profile"]["display_name"] == "Deniz"
    assert "argument_id" in data["xai_meta"]


async def test_chat_session_persists_across_turns(client):
    r1 = await client.post("/api/chat", json={"text": "Selam, ben Zeynep. 900 sıram var."})
    sid = r1.json()["session_id"]
    r2 = await client.post("/api/chat", json={"session_id": sid, "text": "Yazılım seviyorum, girişim kurmak istiyorum."})
    data = r2.json()
    assert data["turn_count"] == 2
    assert data["profile"]["yks_rank"] == 900  # önceki turdan hatırlanıyor
    assert data["reward_previous_turn"] is not None
    assert data["reward_breakdown_previous_turn"] is not None
    assert "argument_effectiveness" in data["reward_breakdown_previous_turn"]


async def test_chat_empty_text_rejected(client):
    r = await client.post("/api/chat", json={"text": "   "})
    assert r.status_code == 400


async def test_session_detail_and_delete(client):
    r1 = await client.post("/api/chat", json={"text": "Merhaba"})
    sid = r1.json()["session_id"]

    r2 = await client.get(f"/api/session/{sid}")
    assert r2.status_code == 200
    detail = r2.json()
    assert len(detail["messages"]) == 2  # user + assistant
    assert len(detail["strategy_logs"]) == 1

    r3 = await client.delete(f"/api/session/{sid}")
    assert r3.json()["deleted"] is True
    r4 = await client.get(f"/api/session/{sid}")
    assert r4.status_code == 404


async def test_fsm_session_path(client):
    r1 = await client.post("/api/chat", json={"text": "Merhaba, 700 sıram var"})
    sid = r1.json()["session_id"]
    r2 = await client.get(f"/api/fsm/session/{sid}")
    assert r2.status_code == 200
    data = r2.json()
    assert data["current_state"]
    assert len(data["path"]) == 1


async def test_bandit_stats(client):
    await client.post("/api/chat", json={"text": "Merhaba, 850 sıralamam var"})
    r = await client.get("/api/bandit/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total_turns"] >= 1
    assert isinstance(data["arguments"], list)
    if data["arguments"]:
        first = data["arguments"][0]
        assert "argument_id" in first and "selected_count" in first


async def test_current_faculty_question_routes_before_bandit(client):
    r = await client.post("/api/chat", json={
        "text": "Yapay zeka alanında çalışan hocalar var mı?",
    })
    assert r.status_code == 200
    data = r.json()
    assert data["xai_meta"]["argument_id"] == "itu_faculty_research"
    route = data["xai_meta"]["decision_factors"]["route"]
    assert route["primary_topic"] == "faculty_research"
    assert route["forced_argument_id"] == "itu_faculty_research"


async def test_closed_conversation_reopens_on_new_support_question(client):
    r1 = await client.post("/api/chat", json={"text": "Merhaba, 800 sıralamam var."})
    sid = r1.json()["session_id"]
    await client.post("/api/chat", json={
        "session_id": sid,
        "text": "Yazılım seviyorum ve İTÜ Bilgisayar düşünüyorum.",
    })
    r3 = await client.post("/api/chat", json={"session_id": sid, "text": "Görüşürüz."})
    assert r3.json()["fsm_state"] == "S8_IDEAL_MATCH_SUMMARY"

    r4 = await client.post("/api/chat", json={
        "session_id": sid,
        "text": "Bir şey daha: yurtlar ve burslar nasıl?",
    })
    data = r4.json()
    assert data["fsm_state"] == "S6_RAG_DEEP_DIVE"
    assert data["xai_meta"]["argument_id"] == "itu_financial_support"


async def test_financial_answer_keeps_rank_specific_amount(client):
    first = await client.post("/api/chat", json={"text": "Merhaba, YKS sıralamam Türkiye 3."})
    session_id = first.json()["session_id"]
    assert first.json()["profile"]["yks_rank"] == 3
    response = await client.post("/api/chat", json={
        "session_id": session_id,
        "text": "Burs imkanları var mı, ne kadar?",
    })
    data = response.json()
    assert data["xai_meta"]["argument_id"] == "itu_financial_support"
    assert "100.000 TL" in data["response_text"]
    assert "10.000 TL + 10.000 TL" in data["response_text"]
    assert data["evidence_check"]["repaired"] is True
    assert len(data["response_text"].split()) <= 65


async def test_generation_api_error_falls_back_to_relevant_rag(client):
    class ErrorResponseLLM(FakeLLMClient):
        async def generate_response(self, **kwargs):
            return "(Sistem hatası — APIConnectionError) Bir saniye, tekrar dener misin?"

    original = routes._orchestrator.llm
    routes._orchestrator.llm = ErrorResponseLLM()
    try:
        response = await client.post("/api/chat", json={
            "text": "Hocalara maille ulaşabilir miyim, danışman hoca atanıyor mu?",
        })
    finally:
        routes._orchestrator.llm = original

    data = response.json()
    assert data["generation_fallback"]["used"] is True
    assert "Sistem hatası" not in data["response_text"]
    assert "danışman hoca" in data["response_text"]
    assert len(data["response_text"].split()) <= 65


async def test_sess_9504_curriculum_regression(client):
    first = await client.post("/api/chat", json={
        "text": "selam ben mert ve ben 700. oldum yksde Bilgisayar Mühendisliği bölümünde tam olarak ne öğretiliyor?",
    })
    first_data = first.json()
    session_id = first_data["session_id"]
    assert first_data["profile"]["display_name"] == "Mert"
    assert first_data["profile"]["yks_rank"] == 700
    assert first_data["xai_meta"]["argument_id"] == "itu_curriculum_overview"
    assert "veri yapıları" in first_data["response_text"]

    second = await client.post("/api/chat", json={
        "session_id": session_id,
        "text": "İlk sınıfta hangi dersler var?",
    })
    second_data = second.json()
    assert second_data["xai_meta"]["argument_id"] == "itu_first_year_curriculum"
    assert "Bilgi Sistemlerine Giriş" in second_data["response_text"]
    assert "C ile Programlamaya Giriş" in second_data["response_text"]
    assert "BLG 417E" not in second_data["response_text"]

    third = await client.post("/api/chat", json={
        "session_id": session_id,
        "text": "Bölüm sadece kod yazmaktan mı oluşuyor? Daha önce hiç programlama yapmadım, zorlanır mıyım?",
    })
    third_data = third.json()
    assert third_data["xai_meta"]["argument_id"] == "itu_curriculum_beginner"
    assert "BLG 102E" in third_data["response_text"]
    assert "ODTÜ" not in third_data["response_text"]


async def test_api_output_respects_spoken_word_limit(client):
    r = await client.post("/api/chat", json={"text": "İTÜ Bilgisayar hakkında bilgi verir misin?"})
    data = r.json()
    assert len(data["response_text"].split()) <= 65
    assert data["speech_check"]["max_words"] == 65


async def test_active_session_style_faculty_and_course_questions_are_specific_and_distinct(client):
    first = await client.post("/api/chat", json={
        "text": "selam ben Nil yksde 347. oldum ve İTÜ bilgisayar için bölüm hocaları öğrencilere karşı ilgili mi?",
    })
    first_data = first.json()
    session_id = first_data["session_id"]
    assert first_data["profile"]["yks_rank"] == 347
    assert first_data["rag"]["facts"][0]["label"] == "Hocaların öğrenci ilgisi"
    assert "Burak Berk Üstündağ" in first_data["response_text"]
    assert "?" in first_data["response_text"]

    second = await client.post("/api/chat", json={
        "session_id": session_id,
        "text": "Hocalara ulaşmak kolay mı?",
    })
    second_data = second.json()
    assert second_data["rag"]["facts"][0]["label"] == "Hocalara ulaşım ve danışmanlık"
    assert second_data["response_text"] != first_data["response_text"]
    assert "kurumsal e-posta" in second_data["response_text"]

    coding = await client.post("/api/chat", json={
        "session_id": session_id,
        "text": "Sınavlarda kod yazmamız isteniyor mu?",
    })
    coding_data = coding.json()
    assert coding_data["rag"]["facts"][0]["label"] == "Sınavlarda kod yazma"
    assert "BLG 102E" in coding_data["response_text"]

    algorithms = await client.post("/api/chat", json={
        "session_id": session_id,
        "text": "Algoritma dersleri çok zor mu?",
    })
    algorithms_data = algorithms.json()
    assert algorithms_data["rag"]["facts"][0]["label"] == "Algoritma dersinin yapısı"
    assert "BLG 335E" in algorithms_data["response_text"]
    assert coding_data["response_text"] != algorithms_data["response_text"]
