# RAG v1 Notu

Bu projede RAG v1 embedding'siz, topic tabanlı çalışır.

Akış:

1. Kullanıcı mesajı, profil ve seçilen argüman `retrieve_facts(...)` fonksiyonuna gider.
2. `backend/app/kb/facts.yaml` ve `backend/app/kb/data/*.yaml` içinden ilgili topic/tag'lere sahip 3-6 fact seçilir.
3. LLM'e bütün bilgi tabanı değil, sadece bu seçilen fact'ler verilir.
4. Yanıt üretildikten sonra `fact_gate` kaynak dışı sayı, garanti, bölüm/program ve çift anadal gibi riskli iddiaları kontrol eder.
5. XAI paneli kullanılan topic'leri ve fact id'lerini gösterir.

Yeni bilgi ekleme:

- Sıralama bilgisi: `topic: ranking`
- Ders/müfredat: `topic: curriculum`
- Hocalar/akademik kadro: `topic: faculty`
- Laboratuvar/araştırma: `topic: labs`
- Yurt/barınma: `topic: housing`
- Burs/maliyet: `topic: scholarship`
- Kariyer/maaş: `topic: career`
- Girişimcilik/Çekirdek: `topic: entrepreneurship`
- Oyun geliştirme: `topic: gamedev`
- Tıp/sağlık teknolojisi: `topic: healthtech`

Kaynak dosyaları:

- Genel kısa fact'ler: `backend/app/kb/facts.yaml`
- Büyük/okunabilir yapılandırılmış kaynaklar: `backend/app/kb/data/`
- İTÜ Bilgisayar öğretim üyesi listesi: `backend/app/kb/data/faculty_members.yaml`

Kural: RAG'de olmayan kesin bilgiyi bot söylememeli. Özellikle hoca adı, lisans bölümü, yurt garantisi, aylık burs, çift anadal şartı ve dersin hangi sınıfta verildiği gibi bilgiler kaynaklı fact olarak eklenmeden kesin ifade edilmez.

Alan/hoca sorularında davranış: RAG içinde kişi adı ve araştırma alanı varsa cevap 1-2 hoca örneğiyle desteklenir. Örneğin yapay zeka sorularında ilgili resmi hoca fact'leri genel laboratuvar bilgisinin önüne alınır; isim yoksa hoca adı uydurulmaz.
