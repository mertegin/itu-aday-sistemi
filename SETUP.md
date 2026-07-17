# SETUP — Negotiation Tabanlı Aday Öğrenci Sistemi

Sadece Python + OpenAI API key gerekli. Frontend backend'in içinde static olarak servisleniyor — ayrı bir dev server yok.

## Kurulum (Tek seferlik)

PowerShell'de:

```powershell
cd C:\Users\90553\Desktop\itu-aday-sistemi\backend

# 1) Virtual env oluştur
python -m venv .venv

# 2) Aktifleştir
.\.venv\Scripts\Activate.ps1

# (Not: PowerShell scripti bloklarsa bir kez şunu çalıştır: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned)

# 3) Bağımlılıkları kur
pip install -r requirements.txt
```

## Çalıştırma

Aynı terminalde (venv aktif):

```powershell
cd C:\Users\90553\Desktop\itu-aday-sistemi\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Şunu görmelisin:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## Kullanım

Tarayıcıda aç: **http://127.0.0.1:8000**

Sol yan: session bilgileri (FSM state, turn, sıralama, motivasyon).
Orta: chat.
Sağ yan: XAI karar paneli (hangi argüman seçildi, neden, hangi FSM geçişi).

### Test Senaryoları

Bir kaç senaryoyu manuel dene:

**Senaryo 1 — Top 1000 + Bilgisayar odaklı**
```
User: Merhaba
User: Adım Ali, sıralamam 750
User: Yazılım ve AI ilgim var, girişim de kurmak istiyorum
User: İTÜ Bilgisayar mı Yapay Zeka Müh. mi karar veremiyorum
```

**Senaryo 2 — Sınırda + kaygı**
```
User: Merhaba
User: Sıralamam 1400 civarı
User: Matematikte çok iyi değilim, İTÜ zor değil mi
```

**Senaryo 3 — Koç alternatifi**
```
User: Selam
User: 800 sıra bekliyorum
User: Ailem Koç'ta okumamı istiyor, ama ben İTÜ'yü düşünüyorum
```

**Senaryo 4 — Tıp arası kararsız**
```
User: Merhaba
User: 500 sıra, ama aslında tıp da düşünüyorum
User: Sağlıkla ilgili bir şey yapmayı seviyorum
```

## API Endpoint'leri

- `POST /api/chat` — mesaj gönder (`{ session_id, text }` → `{ response_text, xai_meta, profile, ... }`)
- `POST /api/session/new` — yeni session ID al
- `GET /api/session/{id}` — session detay + mesaj history + strateji log'ları
- `DELETE /api/session/{id}` — session sil
- `GET /api/health` — health check

Swagger UI: **http://127.0.0.1:8000/docs**

## Konfigürasyon

`backend/.env` içinde:
- `OPENAI_API_KEY` — bitirme projesinden alındı, hazır.
- `OPENAI_MODEL` — default `gpt-4o-mini` (hızlı ve ucuz). Kalite için `gpt-4o` yapabilirsin.
- `DATABASE_URL` — SQLite, `aday_sistemi.db` dosyası backend/ içinde otomatik oluşur.

## Veritabanını sıfırla

```powershell
Remove-Item C:\Users\90553\Desktop\itu-aday-sistemi\backend\aday_sistemi.db
```

Backend'i yeniden başlat — boş bir DB oluşturur.

## Yaygın Sorunlar

| Sorun | Çözüm |
|---|---|
| `ModuleNotFoundError: openai` | venv aktif değil veya `pip install` başarısız |
| `OPENAI_API_KEY missing` | `.env` dosyası backend/ içinde mi kontrol et |
| `port 8000 already in use` | Başka bir process kullanıyor — port değiştir (`--port 8001`) |
| `Set-ExecutionPolicy` gerekiyor | Bir kez yönetici değil normal kullanıcı olarak çalıştır `RemoteSigned` |
| Frontend açılmıyor / boş | Backend çalışıyor mu? `http://127.0.0.1:8000/api/health` gitmelisin, `{"ok": true}` görmen lazım |

## Kod Yapısı (Özet)

```
itu-aday-sistemi/
├── backend/
│   ├── app/
│   │   ├── main.py              — FastAPI + static serve
│   │   ├── config.py            — Settings (.env okur)
│   │   ├── database.py          — SQLAlchemy async engine
│   │   ├── orchestrator.py      — ⭐ Per-turn pipeline
│   │   ├── api/routes.py        — /chat, /session/*
│   │   ├── models/db.py         — Conversation, Message, StrategyLog
│   │   ├── profile/schema.py    — CandidateProfile, IndecisionMatrix
│   │   ├── arguments/catalog.py — Savunma argümanları (16 adet)
│   │   ├── fsm/                 — states.py + machine.py (transition table)
│   │   ├── strategy/bandit.py   — UCB1 + payoff matrix
│   │   ├── llm/                 — OpenAI wrapper + prompts
│   │   ├── xai/engine.py        — Deterministik açıklama
│   │   └── guardrails/ethics.py — Etik keyword filter
│   ├── requirements.txt
│   └── .env
├── frontend/                    — Tek-sayfa HTML/CSS/JS chat UI
│   ├── index.html
│   ├── style.css
│   └── app.js
├── DESIGN.md                    — Ana tasarım dokümanı
├── README.md
└── docs/                        — Mert'in notları + Majidov prompt referansı
```

## Testler

```powershell
cd C:\Users\90553\Desktop\itu-aday-sistemi\backend
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

50 test: FSM geçişleri, bandit (prior fallback regresyonu dahil), ethics filter, Pydantic şema, API endpoint'leri.
API testleri `FakeLLMClient` kullanır — OpenAI çağrısı yapmaz, ücretsizdir.

## Senaryo Kalite Değerlendirmesi (otomatik)

Backend çalışırken:

```powershell
.\.venv\Scripts\python.exe run_eval.py
```

10 senaryoyu koşar ve her birini otomatik değerlendirir: profil extraction doğru mu, beklenen argüman seçildi mi,
etik ihlal var mı, yasak ifadeler ("sınırda", "doğru mu anladım" vb.) geçiyor mu. Çıktı: `eval_report.md`.
**Not:** Gerçek OpenAI çağrısı yapar (~80 istek, birkaç dakika).

Sadece ham konuşma dökümü istersen: `run_scenarios.py` → `scenario_report.md`.

## Bilgi Tabanını Güncelleme

Tüm sayısal veriler `backend/app/kb/facts.yaml` içinde — her fact'in `source`, `year`, `confidence` alanı var.
Sıralama/QS/maaş verisi değişince YAML'ı düzenle, backend'i yeniden başlat. `confidence: low` işaretli
veriler prompt'ta otomatik "(doğrulanmalı)" etiketiyle görünür.

⚠ **Demo öncesi** `meta.verify_before_demo` listesindeki verileri yeniden doğrula.

## Sonraki Adımlar (V2)

- **RAG** — Bilgi tabanı Chroma/FAISS ile embed'li, güncellenebilir
- **Game theory overlay** — Bandit üstüne beklenen fayda katmanı
- **React frontend** — Şu anki HTML/JS testi bitirinde reactify edilebilir
- **Input normalizer** — STT'den gelecek gürültülü metin için ön katman
- **Argüman kataloğunu genişlet** — Daha fazla motivasyon/kararsızlık kombinasyonu
- **Unit test suite** — Bitirme'deki pytest yapısı
