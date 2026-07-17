# Negotiation Tabanlı Aday Öğrenci Sistemi — Tasarım Dokümanı

**Versiyon:** 0.1 (2026-07-09)
**Durum:** Tasarım fazı, kod başlamadı
**Kaynak Mimari:** `C:\Users\90553\Desktop\bitirme\backend\app\` (AI Negotiator)

---

## 1. Vizyon & Felsefe

### Amaç
Adayın profili, motivasyonları ve kararsızlıklarını **açık uçlu sorular** ile analiz eden, sonra **aday-özel savunma argümanlarıyla** İTÜ Bilgisayar Mühendisliği'ni önerebilen humanoid robot sistemi.

### ⚠️ Kapsam Sınırı (Bu Repo)

Robotun tümü ekip projesi. **Bu repo yalnızca negotiation modülünü kapsıyor.**

| Bileşen | Kim yapıyor | Bu repo'da? |
|---|---|---|
| STT (Whisper) | Ekip (diğer) | ❌ |
| CV (kamera, mimik) | Ekip (diğer) | ❌ |
| TTS | Ekip (diğer) | ❌ |
| H-Neurons (robot motion) | Ekip (diğer) | ❌ |
| **Negotiation modülü** (FSM + Bandit + LLM + RAG + XAI) | **Ben** | ✅ |
| **Web UI (test için)** | Ben | ✅ |

**Sözleşme:** Modülün arayüzü **text-in → text-out**. Diğer ekip STT çıktısını buraya HTTP/WebSocket üzerinden bağlar, TTS'e çıktımızı verir. Multimodal detaylar bu tasarımın parçası değil — bu tasarım LLM/RAG/FSM/karar mantığına odaklanır.

### Kritik Etik Kısıtlar
1. **Alternatif üniversite/bölüm kötülenmez.** Karşılaştırma yapılırsa "farklılık" dilinde yapılır, "üstünlük" dilinde değil.
2. **Manipülasyon yok.** Adayın kendi hedefleri/motivasyonları temel alınır; onları bükmek yerine onlara **uyan gerçek** İTÜ imkanları öne çıkarılır.
3. **Karar adaya aittir.** Robot argüman sunar, öneri yapar; ama nihai karar için "sen düşün, sana en uygun olan hangisi" mesajını korur.
4. **Bilgi doğrulu.** Yalnızca RAG'dan çekilmiş güncel/doğrulanmış bilgi konuşulur. Hallüsinasyon kabul edilmez.

### AI Negotiator Felsefesinden Farkı
| AI Negotiator (Bitirme) | Bu Proje |
|---|---|
| **İkna** (satış hedefli) | **Etik ikna** (uygun aday için) |
| Reject = fail | Adayın "bana uymuyor" öz-değerlendirmesi = **başarısızlık değil** |
| Cialdini prensipleri | Aday-özel **savunma argümanı setleri** |
| WhatsApp text | Sesli robot (STT + TTS + CV + H-Neurons) |
| Uzun konuşmalar | ~5-15 dakikalık tanıtım günü etkileşimi |

---

## 2. Mert'in 3 Aşamalı Süreci

### Aşama 1 — Profil ve Kararsızlık Analizi (Giriş)
Adayın **netlik seviyesini** ölçen bir kararsızlık matrisi:

- **Mühendislik kesin mi?** → Tıp/Hukuk/Sosyal Bilimler gibi tamamen farklı alana kayma eğilimi var mı?
- **Üniversite tercihi net mi?** → İTÜ kesin mi, yoksa Koç / Boğaziçi / Bilkent / ODTÜ gibi güçlü alternatifler arasında mı?
- **Bölüm tercihi net mi?** → İTÜ içinde Yapay Zeka / Elektronik / Endüstri / Yazılım Müh. gibi alternatifler mi düşünülüyor?
- **Motivasyon tipi ne?** → Para / Bilim / Prestij / İlgi / Aile baskısı / Kariyer belirsizliği?

Bu **4 boyutlu kararsızlık uzayında** adayın konumu, sonraki aşamanın argüman setini seçer.

### Aşama 2 — Karakter/Motivasyon Bazlı Savunma Algoritmaları
Adayın kararsızlık tipine göre **önceden hazırlanmış argüman şablonları** (RAG kaynaklı, aday cevabına adapte edilerek):

**Örnek matches (Mert'in verdiği):**
- *Tıp ↔ Mühendislik arası:* Sağlık teknolojisi (biyomedikal AI, tıbbi görüntüleme, hastane bilgi sistemleri, sağlık verisi analizi) → CompE'nin sağlığa dokunduğu noktaları göster.
- *Koç ↔ İTÜ Bilgisayar arası:* Köklü ekol, devasa mezun ağı, sektördeki ağırlık, **ilk 1000 için İTÜ bursları**, yurt imkanı, akademik teşvikler.
- *İTÜ Yapay Zeka ↔ İTÜ Bilgisayar arası:* AI, Bilgisayar Müh.'nin bir alt kümesi. Bilgisayar diploması daha geniş esneklik ve temel sağlar; AI yolu Bilgisayar'dan da erişilebilir.

**Genişletilecek matches (henüz tamamlanmadı):**
- *Elektronik ↔ Bilgisayar:* Gömülü sistemler, IoT, donanım-yazılım kesişimi, çift anadal fırsatı.
- *"Çok para kazanmak istiyorum":* Sektör maaş verileri, mezun yerleştirme oranları, girişimcilik ekosistemi (Çekirdek, ARI Teknokent).
- *"Bilim yapmak istiyorum":* AR-GE labları, lisansüstü fırsatları, TÜBİTAK projeleri, uluslararası yayın çıktıları, Erasmus.
- *"Ailem başka bir üniversite istiyor":* Ailelere yönelik veri (istihdam istatistikleri, mezun başarıları) + kararın nihai olarak adaya ait olduğu vurgusu.
- *"Matematikte kötüyüm":* Destek mekanizmaları (mentörlük, ders çalışma grupları, tekrar dersi hakkı).
- *"İTÜ çok zor":* Gerçek başarı oranları, kredi/burs sistemi, mezun olma süreleri.

### Aşama 3 — Etkileşim ve Test Modülü
- **Durum-tabanlı sorular** ile aday profilinin sürekli güncellenmesi
- Her turda **"İdeal Tercih Analizi"**nin adaya özel olarak yeniden hesaplanması
- Konuşma sonunda **kişiselleştirilmiş özet:** "Şu sebeplerden ötürü İTÜ Bilg. senin için uygun görünüyor; şu noktalarda dikkatli olmalısın" gibi dengeli bir çıktı

---

## 3. Sistem Mimarisi (Bu Repo'nun Kapsamı)

```
     ┌─────────────────────────────┐        ┌─────────────────────┐
     │  DIŞ EKİP (STT/CV/TTS/robot)│        │  BU REPO            │
     │  — bu repo'nun ilgisi yok — │        │  Web Test UI        │
     └────────────┬────────────────┘        │  (React/Vite)       │
                  │                         └──────────┬──────────┘
                  │  (ileride)                         │
                  │                                    │
                  ▼    ┌───────── HTTP JSON ────────── ▼
              ┌──────────────────────────────────────────────┐
              │           NEGOTIATION MODULE (FastAPI)       │
              │                                              │
              │   POST /chat  { session_id, text } ──►       │
              │                                              │
              │   ┌───────────── ORCHESTRATOR ────────────┐  │
              │   │ 1. Input normalize (typo/kısalık)     │  │
              │   │ 2. Safety/Fallback check              │  │
              │   │ 3. LLM message analysis               │  │
              │   │ 4. Kararsızlık matrisi güncelle       │  │
              │   │ 5. Aday profil update                 │  │
              │   │ 6. FSM transition                     │  │
              │   │ 7. RAG trigger (İTÜ KB)               │  │
              │   │ 8. Bandit: argument set seçimi        │  │
              │   │ 9. Game theory: which move?           │  │
              │   │ 10. XAI log                           │  │
              │   │ 11. Prompt build + LLM cevap          │  │
              │   │ 12. Safeguard/keyword filter          │  │
              │   └───────────────────────────────────────┘  │
              │              ▲                               │
              │              │                               │
              │        ┌─────┴──────┐                        │
              │        │  RAG       │  (Chroma/Faiss)        │
              │        │  İTÜ KB    │  müfredat, lab, kulüp, │
              │        │            │  burs, staj, mezun,    │
              │        │            │  Erasmus               │
              │        └────────────┘                        │
              │                                              │
              │   ◄── { response_text, xai_meta, session }   │
              └──────────────────────────────────────────────┘
```

### Input Sözleşmesi (Kritik)

```json
POST /chat
{
  "session_id": "sess_abc123",
  "text": "Merhaba, ben aslında tıp da düşünüyorum..."
}
```

**STT'den gelecek metni normalize eden ön katman olmalı** — çünkü konuşmadan gelen text:
- Kısa/parçalanmış olabilir ("ıı… bilmiyorum ki…")
- Typo/tanıma hatası içerebilir ("koç" → "koc" / "goç")
- Noktalama eksik olabilir
- Duraklamalar/geri gitmeler ("şey…yani…tıp değil aslında mühendislik")

`input_normalizer.py` (yeni modül):
- LLM analyzer ile birlikte veya öncesinde
- "Bu ne demek istedi?"i tolere eden esneklik
- Boş/anlamsız input'ta S0_FALLBACK

### Output Sözleşmesi

```json
{
  "session_id": "sess_abc123",
  "response_text": "Anladım, teknoloji ve sağlık kesişimi seni çekmiş olabilir...",
  "xai_meta": {
    "fsm_state": "S4_ARGUMENT_DELIVERY",
    "argument_id": "med_vs_eng_health_tech",
    "reason_tr": "...", "reason_en": "..."
  },
  "session": { "current_phase": 2, "engagement": 0.72 }
}
```

TTS ekibi sadece `response_text`'i kullanır. `xai_meta` dashboard ve debug içindir.

### Latency (Sözlü Değil, Web Test)

Web UI için 3-5 saniye kabul edilebilir (streaming yok da olur). Robot entegrasyonunda ekip streaming katmanı ekler; bu bizim işimiz değil.

---

## 4. Kararsızlık Matrisi (Phase 1 Detayı)

### Boyutlar

```python
IndecisionState:
    field_certainty: float        # 0 = başka alan / 1 = mühendislik kesin
    field_alternatives: list      # ["tıp", "hukuk", ...] (kararsızsa)

    university_certainty: float   # 0 = başka üniv / 1 = İTÜ kesin
    university_alternatives: list # ["koc", "bogazici", "odtu", ...]

    department_certainty: float   # 0 = başka bölüm / 1 = Bilg. kesin
    department_alternatives: list # ["yapay_zeka", "elektronik", "endustri", ...]

    motivation_type: dict         # {money: 0.7, science: 0.3, prestige: 0.4, ...}
```

### Kararsızlık Skorları

```
overall_indecision = 1 - min(field, university, department)_certainty
```

- `overall_indecision > 0.7` → **DERİN KARARSIZ**, Phase 1'de kal, discovery odaklı
- `0.3 < overall_indecision < 0.7` → **SEÇİCİ KARARSIZ**, Phase 2'ye geç, savunma argümanları başlat
- `overall_indecision < 0.3` → **KARARLI**, Phase 3'e geç, doğrulama + pekiştirme

### Sorular Şablonu (Aşama 1)

Sorular **spesifik olarak indecision boyutunu ölçmek** için tasarlanır:

- **Field probe:** "Mühendislik seni en çok neyle çekiyor?" → cevap sağlık, sosyal etki gibi işaret verirse `field_certainty` düşer.
- **University probe:** "Aklında başka üniversiteler var mı?" → "Koç" derse Koç alternatifi tetiklenir.
- **Department probe:** "Bilgisayar mı yapay zeka mı düşünüyorsun?" → alt bölüm alternatifleri.
- **Motivation probe:** "5 yıl sonra kendini nerede görüyorsun?" / "Mezun olunca ne yapmak istiyorsun?" → para/bilim/prestij karışımı.

---

## 5. Savunma Argümanları Kataloğu (Phase 2 Detayı)

### Argüman Şablonu Yapısı

```python
DefenseArgument:
    id: str                        # "koc_vs_itu_scholarship"
    trigger_conditions: dict       # {university_alt: "koc", top_1000: True}
    argument_type: str             # "financial" | "academic" | "career" | "emotional"
    rag_query_template: str        # RAG'a sorulan sorgu şablonu
    delivery_tone: str             # "informative" | "empathetic" | "concrete"
    expected_pushback: list        # muhtemel itirazlar
    followup_hooks: list           # sonraki soru için bağlantı noktaları
```

### İlk 12 Argüman (Backlog)

| ID | Tetikleyici | Argüman Özü |
|---|---|---|
| `med_vs_eng_health_tech` | field_alt=tıp | Sağlık teknolojisi kesişimi (biyomedikal AI, hastane sistemleri) |
| `law_vs_eng_impact` | field_alt=hukuk | Teknoloji hukukunun büyümesi, hybrid kariyerler |
| `koc_vs_itu_heritage` | univ_alt=koc | Köklü ekol, mezun ağı büyüklüğü |
| `koc_vs_itu_scholarship` | univ_alt=koc, ilk_1000=True | İTÜ bursları, yurt, akademik teşvik |
| `bogazici_vs_itu_practical` | univ_alt=bogazici | Uygulama/proje odaklı yaklaşım, Teknokent |
| `odtu_vs_itu_istanbul` | univ_alt=odtu | İstanbul lokasyonu, staj/networking |
| `ai_vs_compe_foundation` | dept_alt=yapay_zeka | AI, CompE'nin alt kümesi; geniş temel |
| `electronics_vs_compe_overlap` | dept_alt=elektronik | Gömülü, IoT, çift anadal |
| `endustri_vs_compe_broader` | dept_alt=endustri | CompE + endüstri hybrid kariyerler |
| `money_motivated_data` | motivation.money>0.6 | Sektör maaş verileri, girişimcilik |
| `science_motivated_labs` | motivation.science>0.6 | AR-GE labları, TÜBİTAK, Erasmus |
| `family_pressure_balanced` | concerns=[family] | Aileye veri + karar aday hakkı |

**Not:** Bu backlog yaşayan bir dokümandır. Her müfredat/burs/laboratuvar değişikliğinde güncellenmeli. Katalog `docs/defense-arguments.md`'de detaylandırılacak.

---

## 6. Aday Profil Şeması

```python
@dataclass
class CandidateProfile:
    # Kimlik (session-bazlı, kalıcı değil — GDPR/veri minimizasyonu)
    display_name: str | None
    session_id: str

    # Kararsızlık Matrisi (Phase 1)
    field_certainty: float        # 0-1
    field_alternatives: list[str]
    university_certainty: float
    university_alternatives: list[str]
    department_certainty: float
    department_alternatives: list[str]
    motivation_type: dict[str, float]  # {money, science, prestige, interest, family}

    # İlgi Alanları (Phase 2)
    academic_interests: dict[str, float]   # {ai, cybersec, gamedev, robotics, ...}
    experience_level: str                  # none | hobby | competition | project
    concerns: list[str]                    # [math, difficulty, family, cost, ...]

    # Meta-signals
    engagement_level: float       # 0-1 (turn süresi + follow-up + CV attention)
    trust_level: float            # 0-1 (progressive disclosure)
    reception_signal: float       # 0-1 (argüman kabulü — pozitif/negatif)

    # Session state
    covered_topics: set[str]
    revealed_arguments: list[str]  # bir argümanı 2. kez sunma
    revealed_facts: list[str]      # "kardeşim İTÜ'de okudu" gibi biyografik

    # Aşama takibi
    current_phase: int             # 1, 2, 3
    phase_transitions: list        # aşama değişim log'u
```

---

## 7. FSM Tasarımı

Mert'in 3-aşama yapısını FSM state'lerine haritalıyoruz:

| State | Aşama | Ne Yapar |
|---|---|---|
| **S0_FALLBACK** | - | STT bozuk / anlaşılmayan input |
| **S1_GREETING** | 1 | Karşılama, güven, isim alma |
| **S2_INDECISION_PROBE** | 1 | Kararsızlık matrisini ölçen sorular |
| **S2R_PROFILE_UPDATE** | 1↔2 | Yeni sinyal geldi → profil/matris güncelle |
| **S3_ARGUMENT_SELECTION** | 2 | Kararsızlık tipi + motivasyona göre argüman seç |
| **S4_ARGUMENT_DELIVERY** | 2 | Seçilen argümanı RAG destekli sun |
| **S5_RECEPTION_EVAL** | 2/3 | Adayın tepkisini oku (kabul/itiraz/yeni bilgi) |
| **S6_RAG_DEEP_DIVE** | 2 | Somut veri / örnek isteği (lab, burs, kulüp detayı) |
| **S7_OBJECTION_HANDLING** | 2 | Endişe/itiraz yönetimi (validate → reframe → data) |
| **S8_IDEAL_MATCH_SUMMARY** | 3 | Kişiselleştirilmiş "İdeal Tercih Analizi" özeti |
| **S9_CLOSING** | 3 | Sonraki adım (broşür/link/randevu) + veda |

### Kritik Predikatlar

```python
_indecision_depth_deep()      → S2 kalması gerekiyor
_ready_for_arguments()        → 2+ kararsızlık boyutu ölçüldü → S3'e
_argument_landed_well()       → reception_signal > 0.6 → S6 (deepen)
_argument_pushback()          → reception_signal < 0.3 → S7 (objection)
_new_concern_surfaced()       → S7
_all_key_indecisions_resolved → S8 (özet)
_student_disengaging()        → CV attention düşük + kısa cevap → S1'e geri dön
_conversation_time_limit()    → 12+ dakika → S9 (kapanış)
```

---

## 8. Karar Katmanı (Bandit + Game Theory)

### Bandit Arms — Argüman Kategorileri

**AI Negotiator'daki Cialdini arm'ları yerine, argüman kategorileri:**

```
'ask_open_question'      — daha fazla profil bilgisi topla
'active_listening'       — dediklerini yansıt, güven kur
'financial_argument'     — burs, para, ROI
'academic_argument'      — müfredat, ders, lab
'career_argument'        — mezun ağı, sektör, staj
'research_argument'      — AR-GE, TÜBİTAK, Erasmus
'lifestyle_argument'     — İstanbul, kampüs, kulüpler
'family_reassurance'     — aileye veri, güvenilirlik
'balanced_perspective'   — dengeli, artı/eksi
'success_story'          — mezun/öğrenci başarı örneği
```

### Context (Bandit Query)
`user_type` yerine daha zengin bir vektör:
- `dominant_motivation`: {money, science, prestige, interest, family_pressure}
- `main_indecision_axis`: {field, university, department, motivation}
- `top_alternative`: {koc, bogazici, medicine, ai, electronics, ...}
- `engagement_level`
- `trust_level`

### Payoff Matrix — Argüman × Motivasyon
```
                        money  science  prestige  interest  family
financial_argument       0.90   0.30    0.60      0.40      0.75
academic_argument        0.40   0.85    0.55      0.70      0.60
career_argument          0.85   0.50    0.75      0.55      0.80
research_argument        0.35   0.90    0.60      0.60      0.40
lifestyle_argument       0.30   0.30    0.50      0.60      0.40
family_reassurance       0.50   0.30    0.60      0.30      0.95
balanced_perspective     0.55   0.60    0.50      0.65      0.70
success_story            0.65   0.55    0.65      0.70      0.75
```

### Game Theory Overlay
AI Negotiator'daki formül aynen korunabilir:
```
U(argument) = 0.55·bandit_score + 0.30·candidate_compatibility + 0.15·itu_compe_goal_alignment
override eşiği = 0.08
```

Bu overlay `backend/app/strategy/utility.py` içinde uygulanmıştır. Açık bir
güncel soru varsa `strategy/router.py` önce doğru argümanı zorlar; utility
overlay profil tabanlı/belirsiz seçimlerde bandit alternatiflerini yeniden değerlendirir.

**System moves** yeniden düşünülmeli (eski 12 move'un ~8'i uyar, 4'ü yeniden yazılır).

---

## 9. Reward Function (Yeniden Kalibre)

Kritik felsefe: "reject" cezası **çok düşük**. Adayın kendi yolunu bulması başarısızlık değildir.

| Sinyal | Δ |
|---|---|
| Follow-up sorusu sordu | **+0.30** |
| Yeni ilgi/motivasyon ortaya çıktı | +0.25 |
| Sunulan argümanı somutlaştırdı ("Peki X nasıl?") | +0.25 |
| Uzun/detaylı cevap verdi | +0.15 |
| Pozitif mimik/tonlama (CV+STT) | +0.15 |
| RAG bilgisi kullanıldı ve adaya dokundu | +0.10 |
| Konuyu değiştirdi | −0.05 |
| Kısa cevap, monoton | −0.10 |
| CV attention düştü | −0.15 |
| Açıkça "bu bana uymuyor" dedi | **0.0** (nötr, cezalandırma) |
| Konuşmayı bitirmek istedi (erken) | −0.10 |

Update: EWMA `α = 0.1` (AI Negotiator ile aynı)

---

## 10. LLM Prompt Tasarımı

### System Prompt İskeleti (AI Negotiator ile aynı yapı)

```
{language_directive}  — Türkçe konuşma

# ROLÜN
Sen İTÜ Bilgisayar Mühendisliği tanıtım robotu Neco'sun. Görevin:
- Adayı dinleyip motivasyon ve endişelerini anlamak
- İTÜ Bilg. Müh.'nin ADAY-ÖZEL neden uygun olduğunu (veya olmadığını) net göstermek
- Manipülasyon yapmadan, alternatifleri kötülemeden, doğru bilgiyle konuşmak

# ADAY PROFİLİ
{profile_summary}
Kararsızlık: {indecision_state}
Dominant motivasyon: {motivation_type}
Bilinen endişeler: {concerns}

# BU TUR SEÇİLEN ARGÜMAN
{argument_id}: {argument_description}
Kaynak (RAG): {rag_snippets}
System move: {system_move}

# KURAL SLOTLARı (dinamik, sadece aktif olanlar)
{fsm_state_rule}
{mode_rule}
{argument_type_rule}
{objection_rule}

# ETİK KURALLAR (sabit)
1. Hiçbir alternatif üniversite/bölüm kötülenmez.
2. "İTÜ herkes için en iyidir" YASAK.
3. Doğrulanmamış istatistik verilme. Sadece {rag_snippets}'teki bilgiyi kullan.
4. Her turda ≤2 cümle. Uzun monolog yok.
5. Robotik değil, samimi ama profesyonel ton.
6. Endişe geldiğinde önce **kabul et**, sonra bilgilendir.
7. "Sen karar ver" vurgusu turn'ün sonunda gerektiğinde.
8. Aday kısa cevap veriyorsa açık uçlu bir soru ile bağla.
9. Somut örnekler > genel iddialar.
10. Aynı argümanı 2. kez sunma ({revealed_arguments} listesine bak).
```

### Çıkış Formatı
- Plain text (JSON değil)
- `max_tokens=200` (kısa, sesli konuşma için)
- `temperature=0.7`
- Post-process: banned openers, filler, dangling half-sentence temizle

---

## 11. RAG Bilgi Tabanı

### İçerik Kategorileri

```
kb/
├── mufredat/           - Zorunlu + seçmeli dersler, kredi bilgisi
├── akademisyenler/     - Öğretim üyeleri, çalışma alanları
├── laboratuvarlar/     - AR-GE lab, ekipman, projeler
├── kulupler/           - IEEE, ACM, girişimcilik, robotik kulüpleri
├── burs_ve_yurt/       - İTÜ bursları (ilk 1000), yurt, indirimler
├── staj_ve_mezun/      - Sektör bağlantıları, mezun başarıları
├── erasmus_ve_dogal/   - Yurt dışı programları, çift anadal
├── girisimcilik/       - ARI Teknokent, Çekirdek, mezun startup'ları
└── karsilastirmali/    - Nötr dilde farklılık kartları (Koç, Boğaziçi, ODTÜ, MIT, ...)
```

**Karşılaştırmalı kartlar özel dikkat:** "Boğaziçi vs İTÜ" gibi bir karta ihtiyaç var ama içerik **dengeli, verilerle** olmalı ("Boğaziçi sosyal bilimler ve sanat alanında güçlü, İTÜ mühendislik ve uygulama odaklı" tarzı).

### Embed & Retrieval
- Chroma / FAISS (basit başlangıç)
- Embedding: `text-embedding-3-small` (OpenAI) veya `bge-m3` (open-source)
- Retrieval: top-3, mode-aware query rewriting
- Kaynağı prompt'ta göster (hallüsinasyon önlemi)

---

## 12. Dış Arayüz Sözleşmesi (Bizim Kapsamımız Dışı)

Multimodal katman **diğer ekip üyelerinin** sorumluluğu. Onların modüllerine bakış:

### STT (Ekip yapacak)
- Beklenti: metin çıktısı verecek. Kaliteyi kontrol etmeyeceğiz.
- **Bizim adaptasyonumuz:** `input_normalizer.py` gürültülü/parçalanmış input'a toleranslı olacak.

### TTS (Ekip yapacak)
- Beklenti: `response_text`'i alıp seslendirecek.
- **Bizim adaptasyonumuz:** LLM promptunda "kısa cümleler, ≤2 cümle, jargonsuz" kuralı — sözlü sistem için doğal.

### CV (Ekip yapacak)
- **Opsiyonel entegrasyon:** İleride ekipten `engagement_signal` (0-1) veya `attention_dropped` (bool) geliyorsa `POST /chat` payload'una ekstra field olarak alabiliriz. İlk versiyonda yok.

### H-Neurons / Robot Motion (Ekip yapacak)
- **Opsiyonel çıktı:** Response'a `gesture_intent` field'ı ekleyebiliriz (`nod`, `smile`, `explaining`, `listening`). Ekibin talebi olursa.

**Kısacası:** İlk versiyon %100 text-in/text-out. Multimodal genişleme opsiyonel ve API-level.

---

## 13. Etik Sınırlar (Guardrails)

Her cevap `safeguard/keyword_filter.py`'den geçer:

**Yasaklı ifade kategorileri:**
- Karşı üniversite/bölüm hakkında olumsuz sıfat ("kötü", "zayıf", "yetersiz")
- Kesin üstünlük iddiaları ("İTÜ en iyidir", "başkasında bulamazsın")
- Doğrulanmamış istatistik ("çoğu mezun", "genellikle")
- Manipülatif dil ("kaçırırsan pişman olursun", "bu fırsat sadece burada")
- Aday hakkında değer yargısı ("başaramazsın", "senin için zor olur")

**Zorunlu ifade kategorileri (özet turunda):**
- "Karar sana ait"
- "Alternatiflerini de değerlendir"
- "Sana en uygun olan"

---

## 14. AI Negotiator → Bu Proje Adaptasyon Haritası

### 🟢 Aynen Getir
| Bileşen | Neden |
|---|---|
| `orchestrator.py` iskeleti (per-turn pipeline) | Genel amaçlı |
| `fsm/` (state machine + transition table pattern) | Genel amaçlı |
| `strategy/` (bandit iskeleti — UCB/Thompson/Greedy) | Genel amaçlı |
| `game_theory/` (utility overlay + override guard) | Genel amaçlı |
| `xai/` (deterministik açıklama üretici) | Genel amaçlı |
| `research/` (Perplexity/DDG RAG entegrasyonu — RAG için template) | Genel amaçlı |
| Loop-break guards (consecutive-state limiter) | Genel amaçlı |
| Reality check pattern | Genel amaçlı, hallüsinasyon önleme |
| Dinamik prompt kural slot sistemi | Genel amaçlı, token tasarrufu |

### 🟡 Değiştir
| Bileşen | Ne değişir |
|---|---|
| `strategy/` payoff matrix + arms | Cialdini → argüman kategorileri |
| `profiler/` schema | Cialdini scores → kararsızlık matrisi + motivasyon |
| `modes/engine.py` classifier | 8 mode → 5-6 aşama-bazlı mode |
| `fsm/machine.py` states + predicates | 11 state → yukarıdaki 11 state |
| `llm/prompts.py` template | Cialdini persuasion → etik ikna, RAG destekli |
| `safety/engine.py` guard | Kriz safety → keyword safeguard (etik ihlal) |
| `research/` client | Perplexity → İTÜ KB (Chroma/Faiss) |

### 🔴 Sıfırdan Yaz
| Bileşen | Neden |
|---|---|
| `input/normalizer.py` | STT'den gelecek gürültülü text'i temizler |
| `kb/itu_ingest.py` | İTÜ KB build & embed |
| `arguments/catalog.py` | Savunma argüman şablon kataloğu |
| `guardrails/ethics_filter.py` | Etik keyword filtresi |
| Web UI (test için) | Bitirme dashboard'undan uyarlanacak (chat + XAI panel) |

### ❌ Getirme
- `whatsapp/` — sesli sistem, WhatsApp yok
- `profiles/identity.py` çoklu-profil — tanıtım günü, her aday tek session
- Anchoring/scarcity/concession Cialdini arm'ları — etik dışı
- `belief_correction` mode (komplo teorisi listeleri) — alakasız
- `product_sales` mode + catalog/competitor cards — satış konsepti yok

---

## 15. Yol Haritası

### Faz A — İskelet (1-2 hafta)
1. `bitirme/backend/app/`'i klonla, isimlendir (`neco_backend/app/` gibi)
2. Getirilmeyecekleri sil (whatsapp, profiles/identity, belief_correction, product_sales)
3. Test suite'i inherit et, karşılığı olmayanları kaldır

### Faz B — Domain Katmanı (2-3 hafta)
4. `CandidateProfile` şeması + `IndecisionMatrix` sınıfı
5. Reward function yeniden yaz
6. Argüman kataloğu (`defense-arguments.md` → `arguments/catalog.py`)
7. FSM state'lerini + predikatlarını değiştir
8. Bandit arm'larını + payoff matrix'i değiştir
9. Mode classifier yeniden yaz

### Faz C — LLM & RAG (1-2 hafta)
10. System prompt yeniden yaz (etik kurallar + RAG bloğu)
11. İTÜ KB verisini topla + embed et
12. RAG retrieval + prompt injection
13. Ethics filter (guardrails)

### Faz D — Web Test UI (1 hafta)
14. Bitirme frontend'ini kopyala, İTÜ-özel değiştir
15. Chat sayfası — text send/receive
16. XAI panel — FSM state, seçilen argüman, reasoning görünür
17. Session yönetimi — birden fazla aday senaryosu simüle et
18. Kararsızlık matrisi visualizer (radar/bar chart)

### Faz E — Test & Kalibrasyon
19. Rol-oyunu senaryoları (10-15 farklı aday tipi)
20. Argüman katalogunu genişlet
21. Kararsızlık matris ölçümü validasyonu
22. Etik ihlal red-team testleri (guardrails atlatılabilir mi?)

### Faz F — Ekip Entegrasyonu (opsiyonel, ileride)
23. HTTP API sözleşmesini ekiple netleştir
24. STT/TTS köprüsünü ekip yapınca birlikte smoke test

---

## 16. Açık Sorular (Karar Verilmesi Gerekenler)

Multimodal soruları ekipteki diğer arkadaşlar sorumlu — bizim aklımızda tutmamız gereken sorular:

1. **Konuşma sayısı limiti?** Tek session'da 5-15 dakikalık akış varsayımı; kaç turn hedefliyoruz?
2. **Aday verisi persist edilecek mi?** KVKK — session sonunda tam silme mi, opt-in analiz mi?
3. **Aynı adayın 2. session'ı?** Web test'te tanısın mı, prod'da nasıl? İlk versiyonda muhtemelen "her session sıfırdan".
4. **RAG'ın güncelleme kadansı?** Bölüm sekreterliği güncel bilgi verecek. Otomatik ingest mi (script) manuel mi (upload)?
5. **LLM tercihi?** Bitirme GPT-4o kullanıyor. Bu proje için de aynı mı, yoksa Claude vb. denenecek mi?
6. **RAG bilgi tabanı için içerik kaynağı?** İTÜ CompE web sitesi scrape'i mi, PDF/manuel giriş mi?
7. **Argüman kataloğu kim genişletecek?** Sen yalnız mı, danışman/hocalarla mı? Onaylayan bir mekanizma var mı?

---

**Sonraki iş:** Bu dokümanı gözden geçir, açık soruları yanıtla, sonra iskelet klonlamayı başlatırız.
