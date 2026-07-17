# Negotiation Tabanlı Aday Öğrenci Sistemi

İTÜ Bilgisayar Mühendisliği tanıtım günlerinde, ziyaretçi lise öğrencileriyle **negotiation (müzakere)** mantığıyla etkileşime geçen humanoid robot sistemi.

## Proje Kimliği

- **Amaç:** Adayı, kendi profil ve motivasyonuna uygun **kişiselleştirilmiş etik savunma argümanlarıyla** İTÜ Bilgisayar Mühendisliği'ni tercih etmeye ikna etmek.
- **Etik Kısıt:** Hiçbir alternatif üniversite/bölüm kötülenmez. Manipülasyon değil, doğru eşleşme.
- **Kaynak Mimari:** [AI Negotiator (bitirme projesi)](../bitirme/) — orada geliştirilen FSM + Contextual Bandit + Game Theory + XAI iskeleti bu projeye adapte ediliyor.
- **Genişleyebilirlik:** Şu an İTÜ Bilg. Müh. için. İleride başka İTÜ bölümleri veya farklı üniversite bölümleri için genişletilebilir.

## Güncel Negotiation Motoru

Sabit hedef İTÜ Bilgisayar Mühendisliği'dir. Her turda güncel soru router ile
önceliklendirilir; bandit geçmiş tepkilerden öğrenir; utility katmanı aday uyumu
ve hedef faydasını birlikte değerlendirir. RAG hazır cevap vermek yerine atomik
bir kanıt paketi üretir; LLM doğal cevabı yazar, doğrulayıcı sorun bulursa tek bir
kanıta bağlı yeniden yazım yapılır. Deterministik kart cevabı yalnız API hatası
veya başarısız ikinci yazımda son çaredir. Çıktı 65 kelimeyle sınırlandırılır.

Teknik akış ve formüller: [`docs/negotiation-v2.md`](docs/negotiation-v2.md)

## Kapsam Sınırı

Robotun tümü ekip projesi. **Bu repo yalnızca negotiation modülü + test için web UI** içerecek.

```
DIŞ EKİP (STT/CV/TTS/robot)         BU REPO
─────────────────────────           ────────────────────────────
STT / mikrofon                      Negotiation Module (FastAPI)
CV / kamera                 ───►    - FSM + Bandit + RAG + LLM     ◄─── Web Test UI
TTS / hoparlör              ◄───    - Text-in / Text-out               (React)
H-Neurons / motion                  - Etik guardrails
```

**Arayüz:** `POST /chat { session_id, text } → { response_text, xai_meta }` — detay `DESIGN.md`'de.

## Klasör Yapısı

```
itu-aday-sistemi/
├── README.md               # Bu dosya
├── DESIGN.md               # ⭐ Ana tasarım dokümanı (mimari, adaptasyon, yol haritası)
└── docs/
    └── mert-notes.md           # Kaynak talimatlar (gereksinim kaynağı)
```

İleride eklenecek: `backend/`, `kb/` (RAG bilgi tabanı), `arguments/` (savunma argümanları kataloğu).

## Sonraki Adımlar

1. `DESIGN.md`'yi birlikte gözden geçir, kararlar üzerinde hemfikir ol
2. `bitirme/backend/app/`'i iskelet olarak klonla
3. Domain-specific modülleri sırayla yeniden yaz (profile → reward → FSM → arms → mode → prompt)
4. Multimodal I/O katmanını ekle (STT/TTS/CV/H-Neurons köprüsü)
