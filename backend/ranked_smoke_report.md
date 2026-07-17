# Sıralama Duyarlı Uzun Senaryo Raporu

- Ekli aday soru havuzu: 451 soru
- Gerçek API konuşması: 1
- Toplam tur: 12
- Mekanik olarak sorunsuz tur: 12
- Model/API fallback: 0
- Sıralama gerçekliği müdahalesi: 0
- Fact gate müdahalesi: 0
- Alaka müdahalesi: 2
- Uyarılar: `{}`

Mekanik `OK`, cevabın insan değerlendirmesinde kusursuz olduğu anlamına gelmez; tam konuşmalar aşağıdadır.

## rank_0005_ai_girisim - SAY 5 profili

Session: `sess_2cc61f113cbf`

**Tur 1 [Açılış]** `active_listening` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği`
- Aday: Merhaba, ben Defne. SAY sıralamam 5 geldi; yapay zekâ ve girişimcilikle ilgileniyorum, İTÜ Bilgisayar'ı değerlendiriyorum.
- Neco: İTÜ Bilgisayar 2025'te 1.435 ile kapattı; 5 sıralaman geçen yılki tabanın önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem.

**Tur 2 [Özel sıralama kontrolü]** `itu_financial_support` RAG: `scholarship_rank_1_10` / `İlk 10 başarı ödülü`
- Aday: Sıralamam 5 olduğuna göre İTÜ'nün başarı ödülü ve bursları bana ne sağlar?
- Neco: Koç Bilgisayar Mühendisliği %100 burslu genel kontenjanı 2025'te 18, taban SAY başarı sırası 113'tü. Örneğin 435 sıralama, geçen yılın %100 burslu tabanının gerisindedir; ücretli veya %50 indirimli kontenjanlar ayrı değerlendirilmelidir. Maddi tarafta senin için aylık burs mu, yoksa yurt desteği mi daha kritik?

**Tur 3 [Özel sıralama kontrolü]** `itu_financial_support` RAG: `admission_koc_compe_full_2025_direct` / `Koç Bilgisayar %100 burslu 2025 kabul gerçekliği`
- Aday: Koç Bilgisayar %100 burslu ile İTÜ Bilgisayar arasında kabul ve maliyet açısından durumum ne?
- Neco: 2025'te Koç Bilgisayar %100 burslu 113, İTÜ Bilgisayar 1.435 ile kapattı; 5 sıralaman iki tabanın da önünde, fakat yeni yıl için ikisi de garanti değil. İTÜ devlet üniversitesi olduğu için eğitim ücretsiz; ilk-10 paketinde tek seferlik 100.000 TL ve başarı koşullarına bağlı düzenli ödül var. Koç'un net toplam teklifini bu paketle karşılaştırmak gerekir.

**Tur 4 [Özel sıralama kontrolü]** `itu_faculty_research` RAG: `ai_faculty_lab_answer_card` / `Yapay zekâ için hoca ve laboratuvar örnekleri`
- Aday: Yapay zekâ alanında çalışabileceğim hoca ve laboratuvarlardan somut örnek verir misin?
- Neco: Bizim yapay zekâ-veri hattımızda Burak Berk Üstündağ, Hazım Kemal Ekenel ve Ayşe Tosun Kühn somut hoca örnekleri. Fakültedeki 18 araştırma laboratuvarı arasında AI Sistemleri, Veri Analitiği ve Görsel Zekâ başlıkları bulunuyor; lisans öğrencisi ilgili hocayla proje uyumunu konuşarak bu çalışmalara katılabiliyor.

**Tur 5 [Kariyer ve mezuniyet sonrası]** `itu_entrepreneurship_ecosystem` RAG: `itu_cekirdek_impact_2025` / `İTÜ Çekirdek'in 14 yıllık girişim desteği`
- Aday: Girişimcilik için okuldan destek alabilir miyim?
- Neco: İTÜ Çekirdek, girişimciliği destekleyen güçlü bir ekosistem sunuyor. 2025'te 5.000'den fazla teknoloji girişimi desteklendi ve 2.000'den fazla girişim şirketleşti. Ayrıca, her yıl ortalama 500 startup'a destek sağlanıyor. Bu, girişimcilik yolculuğunda sana önemli bir avantaj sunar.

**Tur 6 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `itu_compe_differentiators` RAG: `differentiator_qs_abet_faculty_card` / ``
- Aday: İTÜ’nün eğitimi diğer üniversitelere göre daha mı zor?
- Neco: İTÜ, QS 2026 Mühendislik ve Teknoloji'de dünya 91.'si; Bilgisayar Mühendisliği ABET akrediteli. Yapay zekâ çalışan Prof. Dr. Burak Berk Üstündağ'ın, öğrenci geri bildirimlerinde birebir ve e-posta yoluyla yardımcı olduğu aktarılıyor. Kararında eğitim, kampüs, maliyet ve kariyerden hangisi daha ağır basıyor?

**Tur 7 [Projeler ve araştırma imkânları]** `itu_research_projects` RAG: `project_competition_honesty_card` / `Ders projeleri ve yarışmaya dönüşen takım projeleri`
- Aday: Projeler yarışmalara gönderiliyor mu?
- Neco: Ders projeleri otomatik olarak yarışmaya gönderilmiyor; bunun bölüm genelinde yayımlanmış bir oranı da yok. Yarışma hedefleyen öğrenci projeyi danışman veya takımla büyütebilir: güncel öğrenci deneyiminde 19 üyeli İTÜNOM İHA, 2 roket ve 3 uydu geliştiren UZAYTEK ile TEKNOFEST'te yarışan İTÜ Sungur somut örnekler.

**Tur 8 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `university_comparison_general` RAG: `comparison_bilkent_honesty_card` / `Bilkent-İTÜ karşılaştırmasında kaynak sınırı`
- Aday: İTÜ mü Bilkent mi daha iyi?
- Neco: Bilkent de güçlü bir üniversite, ancak İTÜ'nün QS 2026 Mühendislik ve Teknoloji sıralaması 91. ve ABET akrediteli bir program sunuyor. Ayrıca, İTÜ'nün 18 laboratuvarı ve 37 öğretim üyesiyle geniş bir araştırma imkanı var. Eğitim maliyeti açısından devlet üniversitesi olması da büyük bir avantaj.

**Tur 9 [Kariyer ve mezuniyet sonrası]** `future_of_compe` RAG: `future_salary_ai_honesty_card` / `Yapay zekâ çağında iş ve maaş görünümü`
- Aday: Bilgisayar mühendislerinin maaşları gelecekte düşer mi?
- Neco: Bilgisayar mühendislerinin Türkiye'deki maaşlarının kesin düşeceğini veya artacağını gösteren bölüm özelinde güvenilir bir seri yok. Elde olan somut yön sinyali, ABD BLS'nin yazılım geliştirici istihdamında 2023-2033 için %17,9 büyüme projeksiyonu; rutin kodlama dönüşürken sistem tasarımı, güvenlik, veri ve yapay zekâ kurma becerileri önem kazanıyor.

**Tur 10 [Projeler ve araştırma imkânları]** `itu_curriculum_details` RAG: `curriculum_capstone_process_card` / `Bitirme projesinin yapısı ve danışman süreci`
- Aday: Bitirme projesi nasıl seçiliyor?
- Neco: Bitirme projeleri, 7. yarıyıldaki BLG 4901E Tasarım I dersiyle başlar. Öğrenciler, danışmanlarıyla yapılan düzenli toplantılarla proje konularını belirler. Proje, yazılım veya donanım olabilir ve genellikle 2-3 kişilik gruplar halinde yürütülür. Bu süreç, teoriyi uygulamaya dökme fırsatı sunar. Şimdiden en çok yazılım, yapay zekâ, donanım veya siber güvenlikten hangisi ilgini çekiyor?

**Tur 11 [Projeler ve araştırma imkânları]** `itu_clubs_teams` RAG: `insider_current_tech_teams_card` / `İHA, uydu ve TEKNOFEST takımları`
- Aday: Teknofest takımları aktif mi?
- Neco: Evet, Teknofest takımları oldukça aktif. Örneğin, İTÜNOM İHA, 19 üyesiyle insansız hava aracı geliştirme projeleri üzerinde çalışıyor. Ayrıca, UZAYTEK takımı roket, uydu ve İHA projeleri geliştiriyor; bu da mühendislik becerilerini uygulama fırsatı sunuyor.

**Tur 12 [Kariyer ve mezuniyet sonrası]** `money_motivated_data` RAG: `career_employment_companies_card` / ``
- Aday: İTÜ diploması iş görüşmelerinde avantaj sağlar mı?
- Neco: İTÜ diploması, iş görüşmelerinde önemli bir avantaj sağlar. Mezunlarımızın %54'ü mezun olmadan işe başlıyor ve Kariyer.net analizinde bölümümüz 79,2 puanla birinci.

---
