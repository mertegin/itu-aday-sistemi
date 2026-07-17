# Sıralama Duyarlı Uzun Senaryo Raporu

- Ekli aday soru havuzu: 451 soru
- Gerçek API konuşması: 9
- Toplam tur: 127
- Mekanik olarak sorunsuz tur: 122
- Model/API fallback: 0
- Sıralama gerçekliği müdahalesi: 27
- Fact gate müdahalesi: 14
- Alaka müdahalesi: 7
- Uyarılar: `{"near_duplicate": 5}`

Mekanik `OK`, cevabın insan değerlendirmesinde kusursuz olduğu anlamına gelmez; tam konuşmalar aşağıdadır.

## rank_0005_ai_girisim - SAY 5 profili

Session: `sess_f328abe7fefc`

**Tur 1 [Açılış]** `ai_vs_compe_foundation` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği` | sıralama=ahead_of_itu_compe_2025
- Aday: Merhaba, ben Defne. SAY sıralamam 5 geldi; yapay zekâ ve girişimcilikle ilgileniyorum, İTÜ Bilgisayar'ı değerlendiriyorum.
- Neco: İTÜ Bilgisayar 2025'te 1.435 ile kapattı; 5 sıralaman geçen yılki tabanın önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem.

**Tur 2 [Özel sıralama kontrolü]** `itu_financial_support` RAG: `scholarship_rank_1_10` / `İlk 10 başarı ödülü`
- Aday: Sıralamam 5 olduğuna göre İTÜ'nün başarı ödülü ve bursları bana ne sağlar?
- Neco: Sıralaman 5 olduğu için İTÜ'deki başarı ödüllerinden faydalanabilirsin. Türkiye 1-10 arasında yer alan öğrenciler, tek seferlik 100.000 TL başarı desteği ve yılda 9 ay boyunca ayda 10.000 TL burs alıyor. Bu burs, maddi yükünü hafifletir ve eğitimine daha çok odaklanmanı sağlar. Maddi tarafta senin için aylık burs mu, yoksa yurt desteği mi daha kritik?

**Tur 3 [Özel sıralama kontrolü]** `itu_financial_support` RAG: `admission_koc_compe_full_2025_direct` / `Koç Bilgisayar %100 burslu 2025 kabul gerçekliği` | sıralama=koc_full_scholarship_rank_context
- Aday: Koç Bilgisayar %100 burslu ile İTÜ Bilgisayar arasında kabul ve maliyet açısından durumum ne?
- Neco: 2025'te Koç Bilgisayar %100 burslu 113, İTÜ Bilgisayar 1.435 ile kapattı; 5 sıralaman iki tabanın da önünde, fakat yeni yıl için ikisi de garanti değil. İTÜ devlet üniversitesi olduğu için eğitim ücretsiz; ilk-10 paketinde tek seferlik 100.000 TL ve başarı koşullarına bağlı düzenli ödül var. Koç'un net toplam teklifini bu paketle karşılaştırmak gerekir.

**Tur 4 [Özel sıralama kontrolü]** `itu_faculty_research` RAG: `ai_faculty_lab_answer_card` / `Yapay zekâ için hoca ve laboratuvar örnekleri`
- Aday: Yapay zekâ alanında çalışabileceğim hoca ve laboratuvarlardan somut örnek verir misin?
- Neco: Bizim yapay zekâ-veri hattımızda Burak Berk Üstündağ, Hazım Kemal Ekenel ve Ayşe Tosun Kühn somut hoca örnekleri. Fakültedeki 18 araştırma laboratuvarı arasında AI Sistemleri, Veri Analitiği ve Görsel Zekâ başlıkları bulunuyor; lisans öğrencisi ilgili hocayla proje uyumunu konuşarak bu çalışmalara katılabiliyor.

**Tur 5 [Kariyer ve mezuniyet sonrası]** `itu_entrepreneurship_ecosystem` RAG: `itu_cekirdek_impact_2025` / `İTÜ Çekirdek'in 14 yıllık girişim desteği`
- Aday: Girişimcilik için okuldan destek alabilir miyim?
- Neco: İTÜ'de girişimcilik için İTÜ Çekirdek'ten faydalanabilirsin. 2025 itibarıyla 5.000'den fazla teknoloji girişimi desteklendi, 2.000 girişim şirketleşti. Yıllık ortalama 500 startup'a destek sağlanıyor; bu, fikirlerini hayata geçirirken rehberlik ve finansman fırsatları sunar.

**Tur 6 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `itu_compe_differentiators` RAG: `comparison_difficulty_honesty_card` / `İTÜ eğitiminin zorluğunu dürüst karşılaştırma`
- Aday: İTÜ’nün eğitimi diğer üniversitelere göre daha mı zor?
- Neco: İTÜ'nün eğitim programı, düzenli çalışma ve disiplin gerektiren bir yapıya sahip; her yarıyılda 30 AKTS alıyorsun. Örneğin, BLG 312E'de 3 programlama ödevi, BLG 335E'de 3 proje ve sistem-laboratuvar dersleri var. Ancak, diğer üniversitelerle kıyaslayarak "daha zor" demek için kesin bir ölçüm yok. Kararında eğitim, kampüs, maliyet ve kariyerden hangisi daha ağır basıyor?

**Tur 7 [Projeler ve araştırma imkânları]** `itu_research_projects` RAG: `project_competition_honesty_card` / `Ders projeleri ve yarışmaya dönüşen takım projeleri`
- Aday: Projeler yarışmalara gönderiliyor mu?
- Neco: Ders projeleri otomatik olarak yarışmaya gönderilmiyor; bunun bölüm genelinde yayımlanmış bir oranı da yok. Yarışma hedefleyen öğrenci projeyi danışman veya takımla büyütebilir: güncel öğrenci deneyiminde 19 üyeli İTÜNOM İHA, 2 roket ve 3 uydu geliştiren UZAYTEK ile TEKNOFEST'te yarışan İTÜ Sungur somut örnekler.

**Tur 8 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `university_comparison_general` RAG: `comparison_bilkent_honesty_card` / `Bilkent-İTÜ karşılaştırmasında kaynak sınırı`
- Aday: İTÜ mü Bilkent mi daha iyi?
- Neco: Bilkent de güçlü bir üniversite; ancak İTÜ'nün QS 2026 Mühendislik ve Teknoloji sıralamasında dünya 91'inciliği, 18 araştırma laboratuvarı ve ABET akreditasyonu var. İTÜ devlet üniversitesi olarak ücretsiz eğitim sunuyor, %100 İngilizce müfredatla sektöre hazırlıyor.

**Tur 9 [Kariyer ve mezuniyet sonrası]** `future_of_compe` RAG: `future_salary_ai_honesty_card` / `Yapay zekâ çağında iş ve maaş görünümü`
- Aday: Bilgisayar mühendislerinin maaşları gelecekte düşer mi?
- Neco: Bilgisayar mühendislerinin Türkiye'deki maaşlarının kesin düşeceğini veya artacağını gösteren bölüm özelinde güvenilir bir seri yok. Elde olan somut yön sinyali, ABD BLS'nin yazılım geliştirici istihdamında 2023-2033 için %17,9 büyüme projeksiyonu; rutin kodlama dönüşürken sistem tasarımı, güvenlik, veri ve yapay zekâ kurma becerileri önem kazanıyor.

**Tur 10 [Projeler ve araştırma imkânları]** `itu_curriculum_details` RAG: `curriculum_capstone_process_card` / `Bitirme projesinin yapısı ve danışman süreci`
- Aday: Bitirme projesi nasıl seçiliyor?
- Neco: Bitirme projesi, 7. yarıyıldaki BLG 4901E Tasarım I ve 8. yarıyıldaki BLG 4902E Tasarım II derslerinde belirleniyor. Öğrenciler, danışmanlarıyla düzenli toplantılar yaparak projelerini şekillendiriyor. Proje, yazılım veya donanım olabilir; genellikle grup halinde 2-3 kişiyle çalışılıyor. Şimdiden en çok yazılım, yapay zekâ, donanım veya siber güvenlikten hangisi ilgini çekiyor?

**Tur 11 [Projeler ve araştırma imkânları]** `itu_clubs_teams` RAG: `insider_current_tech_teams_card` / `İHA, uydu ve TEKNOFEST takımları`
- Aday: Teknofest takımları aktif mi?
- Neco: Okulumuzun güncel takımlarında 19 üyeli İTÜNOM İHA, 2 roket, 3 uydu ve 1 İHA geliştiren UZAYTEK ile TEKNOFEST'te yarışan İTÜ Sungur bulunuyor. Fakültemizde ayrıca ITU W-TECH, DATABEES ve VCAMP var.

**Tur 12 [Kariyer ve mezuniyet sonrası]** `money_motivated_data` RAG: `career_employment_companies_card` / ``
- Aday: İTÜ diploması iş görüşmelerinde avantaj sağlar mı?
- Neco: İTÜ diploması, iş görüşmelerinde belirli bir avantaj sağlayabilir. Mezunlarımızın %54'ü mezun olmadan işe girmeyi başarmış. Ayrıca, Kariyer.net'in 2024 analizine göre İTÜ Bilgisayar, işveren ilgisi ve hızlı işe girişte birinci sırada.

---

## rank_0035_arastirma - SAY 35 profili

Session: `sess_c243b78e262f`

**Tur 1 [Açılış]** `active_listening` RAG: `department_faculty_labs_card` / `` | sıralama=ahead_of_itu_compe_2025
- Aday: Selam, adım Arda. SAY sıralamam 35; araştırma, yurt dışı doktora ve güçlü akademik kadro benim için önemli.
- Neco: İTÜ Bilgisayar 2025'te 1.435 ile kapattı; 35 sıralaman geçen yılki tabanın önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem. Sen hocalarla daha çok ders desteği için mi, yoksa erkenden bir projeye katılmak için mi iletişim kurmak istiyorsun?

**Tur 2 [Özel sıralama kontrolü]** `itu_financial_support` RAG: `scholarship_rank_11_100` / `11-100 başarı ödülü`
- Aday: 35. olduğum için İTÜ başarı bursunda hangi tutar ve koşullar geçerli?
- Neco: 2025 YKS'de Türkiye 11-100 derecesiyle yerleşenler için İTÜ'de hazırlık dahil 1+4 yıl boyunca yılda 9 ay, aylık 10.000 TL başarı ödülü var. Bursun devamı için yıl sonunda GNO’nun en az 2,50 olması ve hazırlık dönemini başarıyla tamamlaman gerekiyor.

**Tur 3 [Özel sıralama kontrolü]** `itu_research_projects` RAG: `undergraduate_research_card` / ``
- Aday: Hocalarımızla lisans öğrencisiyken proje yapmak gerçekten mümkün mü, örnek verir misin?
- Neco: Lisans öğrencisi araştırmaya yalnız izleyici olarak katılmaz: İTÜ BAP'ın LÖKAP türünde danışman, öğrenciyi araştırma projesine dahil ederek başvurur. Bölümdeki 18 laboratuvar; AI, NLP, robotik, siber güvenlik ve sağlık bilişimi gibi alanlar sunar.

**Tur 4 [Özel sıralama kontrolü]** `science_motivated_labs` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği`
- Aday: İTÜ Bilgisayar'ı diğer güçlü okullardan sayılarla ayıran şey ne?
- Neco: Ayrıca, ABET akreditasyonu ile %100 İngilizce eğitim sunuyor. 37 öğretim üyesi ve 53 araştırma görevlisiyle güçlü bir akademik kadroya sahibiz.

**Tur 5 [Hocalar ve eğitim kalitesi]** `itu_faculty_research` RAG: `faculty_area_ai_data` / `Yapay zekâ ve veri alanında çalışan hocalarımız`
- Aday: Hocalar sektörel deneyime sahip mi?
- Neco: İTÜ Bilgisayar Mühendisliği resmi öğretim üyesi sayfasında yapay zeka, makine öğrenmesi, derin öğrenme, veri bilimi veya veri analitiğiyle ilişkili görünen isimler arasında Burak Berk Üstündağ, Hazım Kemal Ekenel, Mehmet Keskinöz, Nizamettin Aydın, Ali Çakmak, Ayşe Tosun Kühn, Mehmet Baysan, Yusuf Yaslan ve Muhammet Alkan yer alır. Hoca iletişiminde seni düşündüren şey e-postana dönüş almak mı, yoksa birebir görüşebilmek mi?

**Tur 6 [Hocalar ve eğitim kalitesi]** `itu_faculty_research` RAG: `department_faculty_labs_card` / ``
- Aday: Ders içerikleri güncel mi?
- Neco: BBF'nin güncel sayfasında 37 öğretim üyesi (19 profesör, 11 doçent, 7 doktor öğretim üyesi), 10 tam zamanlı öğretim görevlisi ve 18 araştırma laboratuvarı yer alıyor; ayrıca 53 araştırma görevlisi bildiriliyor.

**Tur 7 [Erasmus ve yurt dışı fırsatları]** `itu_erasmus_mobility` RAG: `erasmus_internship_card` / ``
- Aday: Erasmus bursu yeterli oluyor mu?
- Neco: Erasmus stajı öğrenim alanıyla ilgili olmalı ve en az 60 gün, en çok 12 ay sürmelidir. Hazırlık ve ilk sınıfta hemen hareketlilik yapılamaz; ilk sınıf öğrencisi sonraki yıl için başvurabilir. Dil eşiği B1/65'tir.

**Tur 8 [Laboratuvarlar ve teknik olanaklar]** `itu_financial_support` RAG: `scholarship_rank_11_100` / `11-100 başarı ödülü`
- Aday: Öğrencilere ücretsiz yazılım lisansları veriliyor mu?
- Neco: 2025 YKS'de Türkiye 11-100 derecesiyle bir İTÜ lisans programına kayıt yaptıranlara hazırlık dahil 1+4 yıl boyunca yılda 9 ay, resmi sayfada 'ayda 10.000 TL + 10.000 TL' olarak listelenen başarı ödülü verilir. Bursun sürmesi için yıl sonu GNO en az 2,50 olmalı ve hazırlık ilk yılda başarıyla tamamlanmalıdır. Maddi tarafta senin için aylık burs mu, yoksa yurt desteği mi daha kritik?

**Tur 9 [Laboratuvarlar ve teknik olanaklar]** `itu_faculty_research` RAG: `faculty_area_ai_data` / `Yapay zekâ ve veri alanında çalışan hocalarımız`
- Aday: Öğrencilerin kullanabileceği robotik laboratuvarı var mı?
- Neco: İTÜ Bilgisayar Mühendisliği resmi öğretim üyesi sayfasında yapay zeka, makine öğrenmesi, derin öğrenme, veri bilimi veya veri analitiğiyle ilişkili görünen isimler arasında Burak Berk Üstündağ, Hazım Kemal Ekenel, Mehmet Keskinöz, Nizamettin Aydın, Ali Çakmak, Ayşe Tosun Kühn, Mehmet Baysan, Yusuf Yaslan ve Muhammet Alkan yer alır.


**Tur 10 [Erasmus ve yurt dışı fırsatları]** `itu_erasmus_mobility` RAG: `erasmus_internship_card` / `` | UYARI, tekrar=1.0
- Aday: Amerika’da değişim programı var mı?
- Neco: Erasmus stajı öğrenim alanıyla ilgili olmalı ve en az 60 gün, en çok 12 ay sürmelidir. Hazırlık ve ilk sınıfta hemen hareketlilik yapılamaz; ilk sınıf öğrencisi sonraki yıl için başvurabilir. Dil eşiği B1/65'tir.

**Tur 11 [Hocalar ve eğitim kalitesi]** `itu_faculty_research` RAG: `faculty_area_ai_data` / `Yapay zekâ ve veri alanında çalışan hocalarımız` | UYARI, tekrar=1.0
- Aday: Hocalar dersleri anlaşılır anlatıyor mu?
- Neco: İTÜ Bilgisayar Mühendisliği resmi öğretim üyesi sayfasında yapay zeka, makine öğrenmesi, derin öğrenme, veri bilimi veya veri analitiğiyle ilişkili görünen isimler arasında Burak Berk Üstündağ, Hazım Kemal Ekenel, Mehmet Keskinöz, Nizamettin Aydın, Ali Çakmak, Ayşe Tosun Kühn, Mehmet Baysan, Yusuf Yaslan ve Muhammet Alkan yer alır.


**Tur 12 [Laboratuvarlar ve teknik olanaklar]** `itu_faculty_research` RAG: `faculty_area_ai_data` / `Yapay zekâ ve veri alanında çalışan hocalarımız`
- Aday: Elektronik ve gömülü sistem laboratuvarları bulunuyor mu?
- Neco: 18 laboratuvar; AI Sistemleri, NLP, Görsel Zekâ, Robotik, Oyun, IoT-Gömülü Sistemler, Siber Güvenlik ve Gizlilik, Sağlık Bilişimi, Biyoinformatik, Veri Analitiği, Yazılım Mühendisliği ve HPC-Bulut gibi alanları kapsıyor.

---

## rank_0435_koc_karsilastirma - SAY 435 profili

Session: `sess_b3ad0a45b91a`

**Tur 1 [Açılış]** `koc_vs_itu_value` RAG: `admission_koc_compe_full_2025_direct` / `Koç Bilgisayar %100 burslu 2025 kabul gerçekliği` | sıralama=koc_full_scholarship_rank_context
- Aday: Merhaba, ben Selin. SAY sıralamam 435; İTÜ Bilgisayar ile Koç Bilgisayar arasında karar vermeye çalışıyorum.
- Neco: 2025'te Koç Bilgisayar %100 burslu 113, İTÜ Bilgisayar 1.435 ile kapattı. 435 sıralamanla Koç'un %100 burslu kontenjanı geçen yıl gerçekçi değildi; bizim İTÜ Bilgisayar tabanının ise önündesin. İTÜ'de eğitim ücretsiz; 101-500 paketinde yılda 9 ay aylık 8.500 TL başarı ödülü var. Yeni yıl garantisi veremem. Kararında eğitim, kampüs, maliyet ve kariyerden hangisi daha ağır basıyor?

**Tur 2 [Özel sıralama kontrolü]** `itu_financial_support` RAG: `admission_koc_compe_full_2025_direct` / `Koç Bilgisayar %100 burslu 2025 kabul gerçekliği` | sıralama=koc_full_scholarship_rank_context
- Aday: 435 sıralamayla Koç Bilgisayar %100 burslu gelir mi, İTÜ Bilgisayar için durumum ne?
- Neco: 2025'te Koç Bilgisayar %100 burslu 113, İTÜ Bilgisayar 1.435 ile kapattı; 100 sıralaman iki tabanın da önünde, fakat yeni yıl için ikisi de garanti değil. İTÜ devlet üniversitesi olduğu için eğitim ücretsiz; 11-100 paketinde başarı koşullarına bağlı, yılda 9 ay düzenli ödül var. Koç'un net toplam teklifini bu paketle karşılaştırmak gerekir.

**Tur 3 [Özel sıralama kontrolü]** `itu_compe_differentiators` RAG: `admission_koc_compe_full_2025_direct` / `Koç Bilgisayar %100 burslu 2025 kabul gerçekliği` | sıralama=koc_full_scholarship_rank_context
- Aday: İTÜ'yü seçersem Koç'a göre somut olarak ne kazanırım?
- Neco: İTÜ'nün ölçeği somut: 1773'ten beri, 37.210 aktif öğrenci ve 250.000+ mezun; Bilgisayar tarafında ABET, %100 İngilizce ve 18 laboratuvar var. Karşılaştırmada 'daha iyi' sonucu maliyet, kampüs ve hedef alana göre kurulmalıdır.

**Tur 4 [Özel sıralama kontrolü]** `itu_career_evidence` RAG: `career_employment_companies_card` / ``
- Aday: Kariyer Zirvesi'ne gelen şirketlerden örnek vererek anlatır mısın?
- Neco: 2026 Kariyer Zirvesi'nde Turkcell, THY, Siemens, ASELSAN ve Bosch gibi büyük şirketler yer aldı. Bu etkinlik, İTÜ Bilgisayar öğrencilerine staj ve iş fırsatları sağlıyor. Öğrenciler, bu şirketlerle doğrudan iletişim kurarak portföylerini geliştirme ve profesyonel bağlantılar kurma şansı buluyor. Kariyerde hedefin büyük bir teknoloji şirketi mi, girişim mi, yoksa araştırma tarafı mı?

**Tur 5 [Kariyer ve mezuniyet sonrası]** `future_of_compe` RAG: `career_employment_companies_card` / ``
- Aday: Bilgisayar mühendisliği geleceği olan bir bölüm mü?
- Neco: Bilgisayar mühendisliği geleceği parlak bir alan. ABD Çalışma İstatistikleri Bürosu'nun 2023-2033 projeksiyonuna göre yazılım istihdamında %17,9'luk bir büyüme bekleniyor.

**Tur 6 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `university_comparison_general` RAG: `scholarship_rank_11_100` / `11-100 başarı ödülü`
- Aday: İTÜ’nün kampüs hayatı diğer üniversitelerden nasıl farklı?
- Neco: 2025 YKS'de Türkiye 11-100 derecesiyle bir İTÜ lisans programına kayıt yaptıranlara hazırlık dahil 1+4 yıl boyunca yılda 9 ay, resmi sayfada 'ayda 10.000 TL + 10.000 TL' olarak listelenen başarı ödülü verilir. Bursun sürmesi için yıl sonu GNO en az 2,50 olmalı ve hazırlık ilk yılda başarıyla tamamlanmalıdır.

**Tur 7 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `university_comparison_general` RAG: `comparison_bilkent_honesty_card` / `Bilkent-İTÜ karşılaştırmasında kaynak sınırı`
- Aday: İTÜ mü Bilkent mi daha iyi?
- Neco: Bilkent de güçlü bir üniversite, ancak İTÜ'nün QS 2026 Mühendislik ve Teknoloji dünya sıralamasındaki yeri 91. ve ABET akreditasyonuyla eğitim veriyor. İTÜ ayrıca %100 İngilizce eğitimi, 18 laboratuvar ve güçlü sektör bağlantıları sunuyor.

**Tur 8 [Kariyer ve mezuniyet sonrası]** `money_motivated_data` RAG: `career_employment_companies_card` / ``
- Aday: Google, Microsoft veya Amazon gibi şirketlere giren mezunlar var mı?
- Neco: Evet, İTÜ Bilgisayar mezunları Google, Microsoft ve Amazon gibi büyük teknoloji şirketlerinde çalışıyor. Mezunlarımızın %54'ü mezun olmadan iş bulabiliyor. Bu da İTÜ'nün sektörle olan güçlü bağlantılarının bir göstergesi.

**Tur 9 [Kampüs hayatı]** `itu_dining` RAG: `scholarship_rank_11_100` / `11-100 başarı ödülü`
- Aday: Yemekhane yemekleri nasıl?
- Neco: İTÜ yemekhanelerinde 15 Eylül 2025 tarifesine göre öğle ve akşam yemeği ücreti 47,50 TL. Menüde tantuni, et döner, köfte gibi doyurucu seçenekler yer alıyor. Ayrıca vejetaryen alternatifler de mevcut. Eğer yemek bursu alırsan, günde bir öğün öğle yemeği ücretsiz oluyor.

**Tur 10 [Kampüs hayatı]** `itu_technical_resources` RAG: `department_faculty_labs_card` / ``
- Aday: Kampüste çalışabileceğimiz sessiz alanlar var mı?
- Neco: BBF'nin güncel sayfasında 37 öğretim üyesi (19 profesör, 11 doçent, 7 doktor öğretim üyesi), 10 tam zamanlı öğretim görevlisi ve 18 araştırma laboratuvarı yer alıyor; ayrıca 53 araştırma görevlisi bildiriliyor.

**Tur 11 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `itu_compe_differentiators` RAG: `differentiator_qs_abet_faculty_card` / ``
- Aday: İstanbul’da okumak Ankara’da okumaktan daha avantajlı mı?
- Neco: İTÜ, QS 2026 Mühendislik ve Teknoloji'de dünya 91.'si; Bilgisayar Mühendisliği ABET akrediteli. Yapay zekâ çalışan Prof. Dr. Burak Berk Üstündağ'ın, öğrenci geri bildirimlerinde birebir ve e-posta yoluyla yardımcı olduğu aktarılıyor.

**Tur 12 [Kariyer ve mezuniyet sonrası]** `itu_faculty_research` RAG: `faculty_area_ai_data` / `Yapay zekâ ve veri alanında çalışan hocalarımız`
- Aday: Yapay zekâ yazılımcıların işini elinden alır mı?
- Neco: İTÜ Bilgisayar Mühendisliği resmi öğretim üyesi sayfasında yapay zeka, makine öğrenmesi, derin öğrenme, veri bilimi veya veri analitiğiyle ilişkili görünen isimler arasında Burak Berk Üstündağ, Hazım Kemal Ekenel, Mehmet Keskinöz, Nizamettin Aydın, Ali Çakmak, Ayşe Tosun Kühn, Mehmet Baysan, Yusuf Yaslan ve Muhammet Alkan yer alır. Sen hocalarla daha çok ders desteği için mi, yoksa erkenden bir projeye katılmak için mi iletişim kurmak istiyorsun?

---

## rank_0950_maddi_yurt - SAY 950 profili

Session: `sess_2d933d940835`

**Tur 1 [Açılış]** `active_listening` RAG: `scholarship_rank_501_1000` / `501-1000 başarı ödülü`
- Aday: Merhaba, ben Mert. SAY sıralamam 950; ailemin bütçesi sınırlı, burs ve yurtta kalma imkânı kararımı çok etkiliyor.
- Neco: Merhaba Mert! Sıralaman 950, bu İTÜ Bilgisayar Mühendisliği için güvenli bir alan. Burs ve yurt seçenekleri de önemli bir konu. İTÜ'de 501-1000 sıralamasında yerleşen öğrencilere, 1. tercihiyle gelenler için yılda 9 ay boyunca 6.750 TL başarı ödülü veriliyor. Maddi tarafta senin için aylık burs mu, yoksa yurt desteği mi daha kritik?

**Tur 2 [Özel sıralama kontrolü]** `itu_admission_reality` RAG: `scholarship_rank_501_1000` / `501-1000 başarı ödülü`
- Aday: 950 sıralamayla alabileceğim İTÜ başarı ödülünün tutarı ve ilk tercih koşulu nedir?
- Neco: 950 sıralamayla İTÜ'ye 1. tercihinle yerleştiğinde, yıllık toplam 60.750 TL olan başarı ödülünden yararlanabilirsin. Bu bursun devamı için yıl sonunda GNO’nun en az 2,50 olması ve hazırlık dönemini başarıyla tamamlaman gerekiyor.

**Tur 3 [Özel sıralama kontrolü]** `itu_housing_details` RAG: `housing_application_path_card` / `Yeni öğrenciler için yurt başvurusu`
- Aday: Yurt başvurusu nasıl yapılır, oda, mutfak ve internet imkânları nedir?
- Neco: Kalacak yer için izleyeceğin yol şu: İTÜ'ye yerleştikten sonra Yurt ve Burslar Ofisinin ilan ettiği tarihlerde çevrimiçi sistemden belgelerini yükleyip başvuruyorsun; sonucu İTÜ Portal üzerinden izliyorsun. Yerleştirme tercih ve kontenjana bağlı, sonuç açıklanmadan garanti değil. 2026 yeni kayıt takvimi yayımlandığında güncel tarihi ayrıca kontrol etmek gerekiyor.

**Tur 4 [Özel sıralama kontrolü]** `itu_financial_support` RAG: `campus_food_shopping_official_card` / `Ayazağa'da yemek, pizza ve market seçenekleri`
- Aday: Kampüste uygun fiyatlı yemek ve market seçeneklerini isimleriyle söyler misin?
- Neco: Kampüsümüzde uygun fiyatlı yemek seçenekleri olarak Big Slice Pizza, Selfiş, Tarihi Unkapanı Pilavcısı, Küçük Ev, Tost Akademisi ve EspressoLab gibi yerler var. Ayrıca Migros, A101 ve Şok marketleri de kampüs içinde günlük ihtiyaçlarını karşılamak için tercih edebileceğin marketler.

**Tur 5 [Kampüs hayatı]** `itu_dining` RAG: `scholarship_rank_501_1000` / `501-1000 başarı ödülü`
- Aday: Yemek fiyatları uygun mu?
- Neco: Evet, yemek fiyatları oldukça uygun. 15 Eylül 2025 tarifesinde öğle ve akşam yemeği ücreti 47,50 TL. Yemekhanemizde dört kaplık menü sunuluyor; bu menüde tantuni, Adana dürüm, et döner, hamburger, köfte ve balık gibi doyurucu seçenekler yer alıyor.

**Tur 6 [İstanbul’da öğrenci olmak]** `itu_istanbul_life` RAG: `istanbul_transport_card` / `` | sıralama=ahead_of_itu_compe_2025
- Aday: Aileden uzakta yaşamak zor olur mu?
- Neco: İTÜ Bilgisayar 2025'te 1.435 ile kapattı; 950 sıralaman geçen yılki tabanın önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem.

**Tur 7 [Yurt ve barınma]** `itu_student_life_support` RAG: `scholarship_rank_501_1000` / `501-1000 başarı ödülü`
- Aday: İTÜ’nün kendi yurtları var mı?
- Neco: Evet, İTÜ'nün kampüsünde toplam 13 yurt bulunuyor. Bu yurtlar, öğrencilerin ihtiyaçlarına göre farklı konaklama seçenekleri sunuyor. Başarı bursu kapsamında, erkek öğrenciler için üç kişilik standart yurtta yüzde 50 indirimli konaklama imkanı var.

**Tur 8 [Yurt ve barınma]** `itu_student_life_support` RAG: `scholarship_merit_benefits_501_1000` / ``
- Aday: Yurt odaları kaç kişilik?
- Neco: İTÜ yurtlarında genellikle üç kişilik ve dört kişilik odalar mevcut. Bu odalar, öğrencilere rahat bir yaşam alanı sağlamak için tasarlanmış.

**Tur 9 [Kampüs hayatı]** `itu_dining` RAG: `campus_food_shopping_official_card` / `Ayazağa'da yemek, pizza ve market seçenekleri`
- Aday: Kampüste yemek seçenekleri yeterli mi?
- Neco: Kampüsümüzde yemek seçenekleri oldukça yeterli. Yemekhane dışında Big Slice Pizza, Selfiş, Tarihi Unkapanı Pilavcısı gibi çeşitli yerler var. Ayrıca, Migros, A101 ve Şok marketleri de günlük ihtiyaçlarını karşılamak için kolaylık sağlıyor.

**Tur 10 [İstanbul’da öğrenci olmak]** `itu_clubs_projects` RAG: `department_clubs_teams_card` / `Bölüm kulüpleri ve öğrenci takımları`
- Aday: İstanbul’da sosyal hayata para yetiştirmek zor mu?
- Neco: BBF'nin resmî sayfasında 5 bölüm kulübü sayılıyor: Yapay Zekâ, Blockchain Technologies, Oyun Tasarlama ve Geliştirme, İTÜ ACM ve GDG on Campus. Ayrıca W-TECH, DATABEES ve VCAMP adlı 3 öğrenci takımı tanıtılıyor.

**Tur 11 [Kampüs hayatı]** `itu_campus_life` RAG: `campus_compe_ayazaga_card` / ``
- Aday: Ayazağa Kampüsü büyük mü?
- Neco: Bilgisayar Mühendisliği 1.600.000 m²'lik Ayazağa Kampüsü'nde; 7/24 Mustafa İnan Kütüphanesi, 5.100 kişilik stadyum, olimpik havuz ve metro var. 2026 öğrenci deneyiminde Selfish ile Med Çim öne çıkıyor; Bestra, Küçük Ev ve Unkapanı Pilavcısı yemek seçeneklerinden. Kampüste senin için sosyal ortam mı, spor imkânı mı daha belirleyici?

**Tur 12 [Yurt ve barınma]** `itu_housing_details` RAG: `insider_dorm_life_card` / `Yurtlarda oda, mutfak ve internet`
- Aday: Yurtlarda internet iyi mi?
- Neco: İTÜ yurtlarında internet hızı genellikle 1.000 Mbps seviyesinde. Ancak, bu hız her bina ve bağlantıda garanti değil. Öğrenci deneyiminde internetin yeterli olduğu geri bildirimi alıyoruz. Yani, online dersler ve projeler için uygun bir altyapı sunuluyor. Senin için internet hızı ne kadar önemli?

---

## rank_1400_sinir_ders - SAY 1400 profili

Session: `sess_8e3716219e36`

**Tur 1 [Açılış]** `concern_math_difficulty` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği` | sıralama=ahead_of_itu_compe_2025
- Aday: Selam, ben Ece. SAY sıralamam 1400; İTÜ Bilgisayar istiyorum ama tabana yakın olmam ve derslerin zorluğu beni düşündürüyor.
- Neco: İTÜ Bilgisayar 2025'te 1.435 ile kapattı; 1.400 sıralaman geçen yılki tabanın çok yakın biçimde önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem. Seni daha çok kod yazmak mı, yoksa matematiksel analiz kısmı mı düşündürüyor?

**Tur 2 [Özel sıralama kontrolü]** `concern_math_difficulty` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği` | sıralama=ahead_of_itu_compe_2025
- Aday: 1400 sıralamayla İTÜ Bilgisayar gelir mi, dürüstçe söyler misin?
- Neco: İTÜ Bilgisayar 2025'te 1.435 ile kapattı; 1.400 sıralaman geçen yılki tabanın çok yakın biçimde önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem.

**Tur 3 [Özel sıralama kontrolü]** `concern_math_difficulty` RAG: `curriculum_workload_honesty_card` / `Ders yükü ve çalışma düzeni`
- Aday: Hazırlığı geçemezsem ne olur ve yeterliysem nasıl atlarım?
- Neco: Hazırlık döneminde yeterli seviyeye ulaşamazsan, yaz öğretiminde ders alabilirsin ve bu da mezuniyet için önemli bir fırsat. Bizim öğrencilerimiz genellikle hazırlık derslerini geçiyor ve bu süreçte destek mekanizmaları da mevcut; mentörlük ve çalışma grupları gibi.

**Tur 4 [Özel sıralama kontrolü]** `itu_academic_workload` RAG: `insider_exam_curve_card` / `Sınav takvimi ve çan sistemi`
- Aday: Sınavların aynı haftaya yığılması ve çan sistemi gerçekten nasıl?
- Neco: İTÜ yönetmeliğinde ders başarısı bağıl değerlendirmeyle belirleniyor. 2026 Bilgisayar öğrenci deneyiminde vizeler ve finaller aynı haftada yoğunlaşabilse de sınavlar arasında çoğu zaman yaklaşık 2 gün bırakılıyor; takvim ve çan dağılımı derse göre değişiyor.

**Tur 5 [İngilizce eğitim ve hazırlık]** `itu_curriculum_flexibility` RAG: `curriculum_overview_card` / ``
- Aday: Sınav cevaplarını İngilizce mi yazmak gerekiyor?
- Neco: Sınav cevapları genellikle dersin diline bağlıdır. Bilgisayar Mühendisliği’nde bazı dersler İngilizce, bazıları ise Türkçe olabilir. Ama çoğu teknik ders ve sınavda İngilizce yazmak bekleniyor. Bu, İngilizce terminolojiye aşina olmanı da sağlıyor. Başka merak ettiğin bir şey var mı?

**Tur 6 [İngilizce eğitim ve hazırlık]** `itu_curriculum_flexibility` RAG: `curriculum_overview_card` / ``
- Aday: Teknik İngilizceyi anlamak zor mu?
- Neco: Teknik İngilizce başlangıçta zorlayıcı olabilir, ama derslerde sıkça karşılaşacağın terimler zamanla daha aşina hale gelmeni sağlar. Bizim öğrencilerimiz genellikle derslerde ve projelerde bu terimlerle pratik yaparak kendilerini geliştiriyor.

**Tur 7 [Üniversiteye kabul ve tercih süreci]** `itu_admission_reality` RAG: `admission_compe_cutoff_card` / ``
- Aday: Ek kontenjanla girme ihtimali var mı?
- Neco: Ek kontenjan genellikle Yükseköğretim Kurulu tarafından belirleniyor ve her yıl farklılık gösterebiliyor. Geçtiğimiz yıllarda ek kontenjanlar açıldığı oldu, ama kesin bir bilgi vermek zor. Eğer İTÜ Bilgisayar'ı hedefliyorsan, alternatif bölümleri de göz önünde bulundurman iyi olabilir.

**Tur 8 [Üniversiteye kabul ve tercih süreci]** `itu_admission_reality` RAG: `admission_compe_cutoff_card` / `` | sıralama=ahead_of_itu_compe_2025
- Aday: Bölümün puanı neden bu kadar yüksek?
- Neco: İTÜ Bilgisayar 2025'te 1.435 ile kapattı; 1.400 sıralaman geçen yılki tabanın çok yakın biçimde önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem.

**Tur 9 [Derslerin zorluğu ve akademik hayat]** `itu_admission_reality` RAG: `curriculum_exam_coding_card` / `Sınavlarda kod yazma`
- Aday: Sınavlarda kod yazmamız isteniyor mu?
- Neco: Evet, sınavlarda kod yazmanız bekleniyor. Özellikle programlama ve veri yapıları derslerinde, sınavlarda kod okuma, yazma ve algoritma kurma soruları çıkıyor. Bu, gerçek dünya uygulamalarını anlamanızı pekiştiriyor. Başka bir şey merak eder misin?

**Tur 10 [Üniversiteye kabul ve tercih süreci]** `itu_admission_reality` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği`
- Aday: Okul birinciliği kontenjanı bulunuyor mu?
- Neco: İTÜ'de okul birinciliği kontenjanı bulunmuyor; bu nedenle, adayların puanları ve sıralamaları, genel kontenjan üzerinden değerlendiriliyor. Yine de, yüksek sıralamaya sahip olmak İTÜ Bilgisayar'a yerleşme şansını artırıyor.

**Tur 11 [Derslerin zorluğu ve akademik hayat]** `itu_faculty_research` RAG: `department_faculty_labs_card` / ``
- Aday: Hocalar zor soru soruyor mu?
- Neco: BBF'nin güncel sayfasında 37 öğretim üyesi (19 profesör, 11 doçent, 7 doktor öğretim üyesi), 10 tam zamanlı öğretim görevlisi ve 18 araştırma laboratuvarı yer alıyor; ayrıca 53 araştırma görevlisi bildiriliyor.

**Tur 12 [Derslerin zorluğu ve akademik hayat]** `itu_curriculum_flexibility` RAG: `curriculum_overview_card` / ``
- Aday: Derslere devam zorunluluğu var mı?
- Neco: Evet, derslere devam zorunluluğu var. Bu durum, öğrenci deneyimimizi pekiştiriyor. Başka bir konuda yardımcı olabilir miyim?

---

## rank_1500_ai_alternatif - SAY 1500 profili

Session: `sess_07c91a21b1ee`

**Tur 1 [Açılış]** `ideal_match_summary` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği` | sıralama=behind_compe_ahead_of_ai_2025
- Aday: Merhaba, ben Can. SAY sıralamam 1500; hedefim yapay zekâ ama ilk tercihim İTÜ Bilgisayar olsun istiyorum.
- Neco: İTÜ Bilgisayar'ın 2025 tabanı 1.435'ti; 1.500 sıralaman bunun gerisinde, bu yüzden Bilgisayar'ı gerçekçi ana seçenek gibi gösteremem. İTÜ Yapay Zekâ ve Veri 1.947'de kapattığı için geçen yılki veride daha gerçekçi İTÜ seçeneğiydi; gelecek yıl yine garanti değil.

**Tur 2 [Özel sıralama kontrolü]** `itu_admission_reality` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği` | sıralama=behind_compe_ahead_of_ai_2025
- Aday: 1500 sıralamayla İTÜ Bilgisayar gerçekten gelir mi?
- Neco: Tercih sırası istek sırasıdır: üstteki tercih tutmazsa alttaki yanmaz. İTÜ Bilgisayar'ın 2025 tabanı yaklaşık 1.435'ti; adayın kendi SAY sırası bilinmeden 'kesin gelir' denemez, hedef-risk-güvenli seçenekler birlikte yazılmalıdır.

**Tur 3 [Özel sıralama kontrolü]** `ai_vs_compe_foundation` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği` | sıralama=behind_compe_ahead_of_ai_2025
- Aday: Bilgisayar olmazsa İTÜ Yapay Zekâ ve Veri benim sıralamam için gerçekçi mi?
- Neco: İTÜ Yapay Zekâ ve Veri Mühendisliği 2025'te 1.947 en düşük, 102 en yüksek ve 1.438 ortalama SAY başarı sırasıyla öğrenci aldı; genel kontenjanı 30'du. 2.000 ve üzerindeki bir sıra, geçen yılın 1.947 tabanının gerisindedir ve garanti gibi anlatılamaz.

**Tur 4 [Özel sıralama kontrolü]** `university_comparison_general` RAG: `ai_faculty_lab_answer_card` / `Yapay zekâ için hoca ve laboratuvar örnekleri`
- Aday: Yapay zekâ alanında hoca, laboratuvar ve ders örnekleriyle iki yolu karşılaştırır mısın?
- Neco: İTÜ Bilgisayar'da yapay zeka alanında çalışan hocalarımızdan Burak Berk Üstündağ ve Hazım Kemal Ekenel var. Ayrıca, AI Sistemleri ve Veri Analitiği gibi 18 araştırma laboratuvarımız mevcut. İTÜ Yapay Zekâ ve Veri'de ise daha yoğun bir yapay zeka odaklı müfredat var. Kararında eğitim, kampüs, maliyet ve kariyerden hangisi daha ağır basıyor?

**Tur 5 [Bölümün içeriği hakkında]** `itu_curriculum_details` RAG: `curriculum_operating_systems_card` / ``
- Aday: Bölümde hangi programlama dilleri öğretiliyor?
- Neco: BLG 312E; süreç, iş parçacığı, senkronizasyon, kilitlenme, CPU zamanlama, sanal bellek ve dosya sistemlerini işler. Resmî katalogda Unix sistem çağrılarıyla 3 programlama ödevi bulunur; teori doğrudan uygulamaya bağlanır.

**Tur 6 [Bölümün içeriği hakkında]** `itu_curriculum_flexibility` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği`
- Aday: Yapay zekâ alanında hangi dersler var?
- Neco: İTÜ Bilgisayar Mühendisliği müfredatında yapay zeka alanında dersler arasında "Yapay Zekâ", "Makine Öğrenmesi" ve "Derin Öğrenme" yer alıyor. Ayrıca, seçmeli ders havuzunda "Bilgisayarla Görme" ve "Robotik" gibi güncel konular da bulunuyor.

**Tur 7 [Üniversiteye kabul ve tercih süreci]** `itu_admission_reality` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği`
- Aday: Okul birinciliği kontenjanı bulunuyor mu?
- Neco: Evet, İTÜ'de okul birincileri için özel bir kontenjan mevcut. Bu kontenjan, her bölüm için belirli bir sayıda öğrenci alımını içeriyor. Ancak, detaylar ve kesin sayılar her yıl değişebilir, bu yüzden güncel bilgiler için İTÜ'nün resmi web sitesini takip etmekte fayda var.

**Tur 8 [Uzmanlaşma alanları ve seçmeli dersler]** `itu_specialization` RAG: `curriculum_ai_security_electives_card` / ``
- Aday: Farklı bölümlerden seçmeli ders alabilir miyim?
- Neco: Güncel meslek seçmeli havuzunda Bilgisayarla Görme, Robotik, Bilgisayar Güvenliği, Güvenli Programlama, Ağ Güvenliği, AI Accelerators Lab ve AI Aided Computer Engineering var. Havuz 27 ders içerir; fiilî açılış dönem programına bağlıdır.

**Tur 9 [Üniversiteye kabul ve tercih süreci]** `itu_admission_reality` RAG: `admission_preference_strategy_card` / `` | sıralama=behind_compe_ahead_of_ai_2025
- Aday: Sıralamam bu bölüme yetebilir mi?
- Neco: İTÜ Bilgisayar'ın 2025 tabanı 1.435'ti; 1.500 sıralaman bunun gerisinde, bu yüzden Bilgisayar'ı gerçekçi ana seçenek gibi gösteremem. İTÜ Yapay Zekâ ve Veri 1.947'de kapattığı için geçen yılki veride daha gerçekçi İTÜ seçeneğiydi; gelecek yıl yine garanti değil.

**Tur 10 [Uzmanlaşma alanları ve seçmeli dersler]** `itu_specialization` RAG: `curriculum_ai_security_electives_card` / `` | UYARI, tekrar=1.0
- Aday: Hangi sınıfta alan seçmeye başlıyoruz?
- Neco: Güncel meslek seçmeli havuzunda Bilgisayarla Görme, Robotik, Bilgisayar Güvenliği, Güvenli Programlama, Ağ Güvenliği, AI Accelerators Lab ve AI Aided Computer Engineering var. Havuz 27 ders içerir; fiilî açılış dönem programına bağlıdır.

**Tur 11 [Uzmanlaşma alanları ve seçmeli dersler]** `itu_specialization` RAG: `curriculum_ai_security_electives_card` / ``
- Aday: Siber güvenliğe yönelmek için hangi dersleri almalıyım?
- Neco: 18 laboratuvar; AI Sistemleri, NLP, Görsel Zekâ, Robotik, Oyun, IoT-Gömülü Sistemler, Siber Güvenlik ve Gizlilik, Sağlık Bilişimi, Biyoinformatik, Veri Analitiği, Yazılım Mühendisliği ve HPC-Bulut gibi alanları kapsıyor.

**Tur 12 [Üniversiteye kabul ve tercih süreci]** `itu_curriculum_overview` RAG: `curriculum_overview_card` / ``
- Aday: Tanıtım günlerinde hangi bilgileri özellikle sormalıyım?
- Neco: Program C ve matematik temelinden veri yapıları, devreler, algoritmalar, veritabanı, mikroişlemci, mimari, işletim sistemi, yapay zekâ ve yazılım mühendisliğine ilerler; 8 yarıyıl, 130 yerel kredi ve 240 AKTS iki dönemlik tasarımla tamamlanır.

---

## rank_2000_itu_icinde - SAY 2000 profili

Session: `sess_e07b145a7e59`

**Tur 1 [Açılış]** `ai_vs_compe_foundation` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği` | sıralama=behind_compe_and_ai_2025
- Aday: Selam, ben Zeynep. SAY sıralamam 2000; yazılım ve yapay zekâ istiyorum, mümkünse İTÜ içinde kalmak istiyorum.
- Neco: 2.000 sıralaman, 2025'te İTÜ Bilgisayar'ın 1.435 ve Yapay Zekâ-Veri'nin 1.947 tabanının gerisinde; ikisini de gerçekçi ana seçenek gibi satmam doğru olmaz. İTÜ içinde Elektronik-Haberleşme 2.126 ile kapattığı için geçen yılki tabloya göre daha gerçekçi bir yoldu.

**Tur 2 [Özel sıralama kontrolü]** `ai_vs_compe_foundation` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği` | sıralama=behind_compe_and_ai_2025
- Aday: 2000 sıralamayla İTÜ Bilgisayar veya Yapay Zekâ ve Veri gelir mi?
- Neco: İTÜ Bilgisayar Mühendisliği resmi öğretim üyesi sayfasında yapay zeka, makine öğrenmesi, derin öğrenme, veri bilimi veya veri analitiğiyle ilişkili görünen isimler arasında Burak Berk Üstündağ, Hazım Kemal Ekenel, Mehmet Keskinöz, Nizamettin Aydın, Ali Çakmak, Ayşe Tosun Kühn, Mehmet Baysan, Yusuf Yaslan ve Muhammet Alkan yer alır.


**Tur 3 [Özel sıralama kontrolü]** `itu_admission_reality` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği` | sıralama=behind_compe_and_ai_2025
- Aday: Bu sıralamayla İTÜ içinde hangi bölüm geçen yıl daha gerçekçiydi?
- Neco: Koç Bilgisayar Mühendisliği %100 burslu genel kontenjanı 2025'te 18, taban SAY başarı sırası 113'tü. Örneğin 435 sıralama, geçen yılın %100 burslu tabanının gerisindedir; ücretli veya %50 indirimli kontenjanlar ayrı değerlendirilmelidir.

**Tur 4 [Özel sıralama kontrolü]** `itu_admission_reality` RAG: `admission_compe_cutoff_card` / `` | UYARI, tekrar=1.0, sıralama=behind_compe_and_ai_2025
- Aday: Başka İTÜ bölümünden Bilgisayar'a geçerim diye tercih yapmak ne kadar riskli?
- Neco: 2.000 sıralaman, 2025'te İTÜ Bilgisayar'ın 1.435 ve Yapay Zekâ-Veri'nin 1.947 tabanının gerisinde; ikisini de gerçekçi ana seçenek gibi satmam doğru olmaz. İTÜ içinde Elektronik-Haberleşme 2.126 ile kapattığı için geçen yılki tabloya göre daha gerçekçi bir yoldu.

**Tur 5 [Çift anadal, yandal ve bölüm değiştirme]** `itu_double_major_transfer` RAG: `double_major_minor_card` / ``
- Aday: Bilgisayar Mühendisliğinde çift anadal yapmak mümkün mü?
- Neco: Evet, Bilgisayar Mühendisliği öğrencileri çift anadal yapabilir. Bunun için 3. yarıyıldan itibaren başvuruda bulunmalısın; en az 3,00 GNO ve sınıfın üst %20'sinde olman gerekiyor. Çift anadal ile farklı bir bölümde daha derinlemesine bilgi sahibi olabilirsin, bu da kariyerine büyük katkı sağlar.

**Tur 6 [Üniversiteye kabul ve tercih süreci]** `ai_vs_compe_foundation` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği`
- Aday: Bilgisayar Mühendisliği yerine Yapay Zekâ ve Veri Mühendisliği yazmalı mıyım?
- Neco: Yapay Zekâ ve Veri Mühendisliği, bilgisayar mühendisliğinin güçlü bir alt kümesi ve AI alanına özel bir odaklanma sunuyor. Eğer AI'ya olan ilgin yüksekse ve 2025'teki taban sıralaman 1.947 ise, bu bölüm tercih edilebilir.

**Tur 7 [Çift anadal, yandal ve bölüm değiştirme]** `itu_double_major_transfer` RAG: `transfer_card` / ``
- Aday: Bölümü sevmezsem başka bölüme geçebilir miyim?
- Neco: İTÜ içinde yatay geçiş yapabilirsin, fakat belli koşullar var. En az 2,50 GNO ile 3. yarıyıldan itibaren başvuru yapman gerekiyor. Her yıl kontenjan açılıyor, ama bu kontenjanlar değişebiliyor. Eğer farklı bir bölüme geçiş yapmayı düşünüyorsan, bu süreçte GNO’nu yüksek tutmak önemli.

**Tur 8 [Doğal ve konuşma dilinde sorular]** `socratic_probe` RAG: `curriculum_operating_systems_card` / ``
- Aday: Sürekli ödev ve proje mi yapılıyor?
- Neco: Evet, Bilgisayar Mühendisliği'nde ödev ve projeler önemli bir yer tutuyor. Örneğin, işletim sistemleri dersi kapsamında uygulamalı projeler yaparak teorik bilgileri pratiğe dökme imkânı buluyorsun. Bu süreç, öğrenmeyi pekiştirmenin yanı sıra, ekip çalışması ve problem çözme becerilerini geliştirir.

**Tur 9 [Çift anadal, yandal ve bölüm değiştirme]** `itu_double_major_transfer` RAG: `transfer_card` / ``
- Aday: Başka bir bölümden Bilgisayar Mühendisliğine yatay geçiş mümkün mü?
- Neco: Evet, başka bir bölümden Bilgisayar Mühendisliği'ne yatay geçiş yapabilirsin. Bunun için en az 2,50 GNO ve başvuru koşullarını sağlaman gerekiyor. Yataydaki geçişler, her yıl belirlenen kontenjanlara bağlı olarak değişiyor.

**Tur 10 [Üniversiteye kabul ve tercih süreci]** `itu_admission_reality` RAG: `admission_compe_cutoff_card` / `` | sıralama=behind_compe_and_ai_2025
- Aday: Bilgisayar Mühendisliği kaç bin sıralamayla alıyor?
- Neco: 2.000 sıralaman, 2025'te İTÜ Bilgisayar'ın 1.435 ve Yapay Zekâ-Veri'nin 1.947 tabanının gerisinde; ikisini de gerçekçi ana seçenek gibi satmam doğru olmaz. İTÜ içinde Elektronik-Haberleşme 2.126 ile kapattığı için geçen yılki tabloya göre daha gerçekçi bir yoldu.

**Tur 11 [Doğal ve konuşma dilinde sorular]** `ideal_match_summary` RAG: `career_employment_companies_card` / ``
- Aday: Bu bölüm yaratıcı birine uygun mu?
- Neco: Bilgisayar Mühendisliği, yaratıcı düşünmeyi teşvik eden bir alan. Yazılım geliştirme, algoritma tasarımı veya proje bazlı çalışmalar gibi konular, yaratıcılığını kullanmanı gerektirecek. Özellikle, yeni çözümler bulmak ve yenilikçi projeler geliştirmek için özgün düşünme becerisi çok değerlidir.

**Tur 12 [Üniversiteye kabul ve tercih süreci]** `itu_admission_reality` RAG: `admission_compe_cutoff_card` / `` | sıralama=behind_compe_and_ai_2025
- Aday: Bölümün puanı neden bu kadar yüksek?
- Neco: İTÜ Yapay Zekâ ve Veri Mühendisliği 2025'te 1.947 en düşük, 102 en yüksek ve 1.438 ortalama SAY başarı sırasıyla öğrenci aldı; genel kontenjanı 30'du. 2.000 ve üzerindeki bir sıra, geçen yılın 1.947 tabanının gerisindedir ve garanti gibi anlatılamaz.

---

## rank_2500_itu_icinde - SAY 2500 profili

Session: `sess_45308e91b0e7`

**Tur 1 [Açılış]** `socratic_probe` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği` | sıralama=behind_compe_and_ai_2025
- Aday: Merhaba, ben Emir. SAY sıralamam 2500; bilgisayar ve yazılım ilgim var ama İTÜ'den de vazgeçmek istemiyorum.
- Neco: 2.500 sıralaman, 2025'te İTÜ Bilgisayar'ın 1.435 ve Yapay Zekâ-Veri'nin 1.947 tabanının gerisinde; ikisini de gerçekçi ana seçenek gibi satmam doğru olmaz. İTÜ içinde Matematik Mühendisliği 3.495 ile kapattığı için geçen yılki tabloya göre daha gerçekçi bir yoldu.

**Tur 2 [Özel sıralama kontrolü]** `itu_curriculum_overview` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği` | sıralama=behind_compe_and_ai_2025
- Aday: 2500 ile İTÜ Bilgisayar olur mu, boş umut vermeden anlatır mısın?
- Neco: 1. yarıyıl: Fizik I+Lab, Bilgi Sistemlerine Giriş, Bilgisayar Mühendisliğine Giriş ve Etik, Matematik I, Lineer Cebir, ING 100. 2. yarıyıl: Ayrık Matematik, C ile Programlamaya Giriş, Matematik II, Fizik II+Lab, ING 112A, DAN 102. Şimdiden en çok yazılım, yapay zekâ, donanım veya siber güvenlikten hangisi ilgini çekiyor?

**Tur 3 [Özel sıralama kontrolü]** `ai_vs_compe_foundation` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği` | sıralama=behind_compe_and_ai_2025
- Aday: İTÜ Yapay Zekâ ve Veri de olmazsa sıralamama uyan gerçekçi İTÜ yolu nedir?
- Neco: İTÜ Yapay Zekâ ve Veri Mühendisliği 2025'te 1.947 en düşük, 102 en yüksek ve 1.438 ortalama SAY başarı sırasıyla öğrenci aldı; genel kontenjanı 30'du. 2.000 ve üzerindeki bir sıra, geçen yılın 1.947 tabanının gerisindedir ve garanti gibi anlatılamaz.

**Tur 4 [Özel sıralama kontrolü]** `university_comparison_general` RAG: `admission_ytu_compe_2025_direct` / `YTÜ Bilgisayar 2025 kabul gerçekliği` | UYARI, tekrar=1.0, sıralama=behind_compe_and_ai_2025
- Aday: YTÜ Bilgisayar ile sıralamama uygun bir İTÜ bölümünü nasıl dürüstçe karşılaştırırsın?
- Neco: 2.500 sıralaman, 2025'te İTÜ Bilgisayar'ın 1.435 ve Yapay Zekâ-Veri'nin 1.947 tabanının gerisinde; ikisini de gerçekçi ana seçenek gibi satmam doğru olmaz. İTÜ içinde Matematik Mühendisliği 3.495 ile kapattığı için geçen yılki tabloya göre daha gerçekçi bir yoldu.

**Tur 5 [Üniversiteye kabul ve tercih süreci]** `ideal_match_summary` RAG: `career_employment_companies_card` / ``
- Aday: Bilgisayar mühendisliğini gerçekten sevip sevmediğimi nasıl anlarım?
- Neco: Bilgisayar mühendisliğine olan ilgin, problem çözme, yazılım geliştirme veya yeni teknolojileri keşfetme isteğinle belirginleşir. Ayrıca, algoritmalar, programlama dilleri veya veri analizi gibi konulara karşı duyduğun merak da önemli bir sinyal. Hangi konular seni daha çok heyecanlandırıyor?

**Tur 6 [Bölümün içeriği hakkında]** `concern_math_difficulty` RAG: `curriculum_algorithms_difficulty_card` / `Algoritma dersinin yapısı`
- Aday: Algoritma dersleri çok zor mu?
- Neco: Algoritma Analizi I kolay derslerden sayılmaz, ama düzenli problem çözerek yönetilebilir. BLG 335E asimptotik analiz, yinelemeler, sıralama ve ağaçları işliyor; resmî katalogda 3 proje var ve proje sorularından sınavlarda yararlanılabiliyor. Ezberden çok çözüm mantığı ve karmaşıklık analizi istiyor.

**Tur 7 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `itu_clubs_teams` RAG: `student_profile_honesty_card` / ``
- Aday: İTÜ’deki öğrenci profili nasıl?
- Neco: Bölümün resmî öğrenci kişilik dağılımı veya 'rekabetçi-dayanışmacı' oranı yayımlanmıyor. Somut temas kanalları ise 5 bölüm kulübü, 3 takım, danışman öğretim üyesi ve 18 araştırma laboratuvarıdır; sosyal uyum kişiden kişiye değişir.

**Tur 8 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `itu_compe_differentiators` RAG: `comparison_difficulty_honesty_card` / `İTÜ eğitiminin zorluğunu dürüst karşılaştırma`
- Aday: İTÜ’nün eğitimi diğer üniversitelere göre daha mı zor?
- Neco: İTÜ'nün eğitim programı zorluğu konusunda net bir kıyaslama yapmak zor; her üniversitenin ders yapısı farklı. Bizim programda her yarıyılda 30 AKTS, düzenli çalışma gerektiren projeler ve laboratuvar dersleri var. Kararında eğitim, kampüs, maliyet ve kariyerden hangisi daha ağır basıyor?

**Tur 9 [Üniversiteye kabul ve tercih süreci]** `itu_curriculum_overview` RAG: `curriculum_overview_card` / ``
- Aday: Tanıtım günlerinde hangi bilgileri özellikle sormalıyım?
- Neco: Program C ve matematik temelinden veri yapıları, devreler, algoritmalar, veritabanı, mikroişlemci, mimari, işletim sistemi, yapay zekâ ve yazılım mühendisliğine ilerler; 8 yarıyıl, 130 yerel kredi ve 240 AKTS iki dönemlik tasarımla tamamlanır.

**Tur 10 [Üniversiteye kabul ve tercih süreci]** `itu_admission_reality` RAG: `admission_compe_cutoff_card` / `` | sıralama=behind_compe_and_ai_2025
- Aday: Kontenjan artarsa taban sıralama nasıl değişir?
- Neco: 2.500 sıralaman, 2025'te İTÜ Bilgisayar'ın 1.435 ve Yapay Zekâ-Veri'nin 1.947 tabanının gerisinde; ikisini de gerçekçi ana seçenek gibi satmam doğru olmaz. İTÜ içinde Matematik Mühendisliği 3.495 ile kapattığı için geçen yılki tabloya göre daha gerçekçi bir yoldu.

**Tur 11 [Bölümün içeriği hakkında]** `itu_specialization` RAG: `curriculum_ai_security_electives_card` / ``
- Aday: Kuantum bilişim üzerine çalışma yapılıyor mu?
- Neco: Güncel meslek seçmeli havuzunda Bilgisayarla Görme, Robotik, Bilgisayar Güvenliği, Güvenli Programlama, Ağ Güvenliği, AI Accelerators Lab ve AI Aided Computer Engineering var. Havuz 27 ders içerir; fiilî açılış dönem programına bağlıdır.

**Tur 12 [Bölümün içeriği hakkında]** `electronics_vs_compe_overlap` RAG: `curriculum_balance_card` / ``
- Aday: Gömülü sistemlerle ilgili dersler var mı?
- Neco: Evet, İTÜ Bilgisayar Mühendisliği programında gömülü sistemlere yönelik dersler mevcut. Özellikle Sayısal Devreler, Mikroişlemci Sistemleri ve Bilgisayar Mimarisi gibi dersler, bu alanda sağlam bir temel sağlar. Ayrıca, gömülü sistemler ile ilgili projeler yaparak pratik deneyim kazanabilirsiniz.

---

## stress_rank_0950 - Tek oturumda tüm ana kategoriler

Session: `sess_7404388755d4`

**Tur 1 [Açılış]** `itu_admission_reality` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği` | sıralama=ahead_of_itu_compe_2025
- Aday: Merhaba, ben Ada. SAY sıralamam 950; İTÜ Bilgisayar'ı ciddi düşünüyorum ve karar vermeden önce çok ayrıntılı soru soracağım.
- Neco: İTÜ Bilgisayar 2025'te 1.435 ile kapattı; 950 sıralaman geçen yılki tabanın önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem.

**Tur 2 [Bölümün içeriği hakkında]** `itu_admission_reality` RAG: `curriculum_balance_card` / ``
- Aday: Devre tasarımı yapmamız gerekiyor mu?
- Neco: Evet, bizim bölümde devre tasarımı önemli bir yer tutuyor. Zorunlu dersler arasında Sayısal Devreler ve Elektronik var. Bu dersler, yazılım ve donanım arasındaki köprüyü kurmanı sağlar. Örneğin, Sayısal Devreler dersi sayesinde devreleri anlamak, sistem mühendisliği açısından büyük bir avantajdır.

**Tur 3 [Kodlama bilmeyen öğrencilerin kaygıları]** `concern_math_difficulty` RAG: `curriculum_workload_honesty_card` / `Ders yükü ve çalışma düzeni`
- Aday: Diğer öğrenciler benden daha ileride olursa ne yapabilirim?
- Neco: Bu kaygı oldukça anlaşılır, İTÜ zorlu bir okul. Ancak, bölümümüzde öğrencilere destek sağlayan birçok mekanizma var. Mentörlük programları, ders çalışma grupları ve tekrar dersi hakkı gibi imkanlarla birlikte, diğer öğrencilerle işbirliği yaparak ilerleyebilirsin. Seni daha çok kod yazmak mı, yoksa matematiksel analiz kısmı mı düşündürüyor?

**Tur 4 [Derslerin zorluğu ve akademik hayat]** `compe_priority_top1000` RAG: `department_employment_card` / ``
- Aday: Projeleri teslim etmek için yeterli süre veriliyor mu?
- Neco: Genellikle projeler için yeterli süre tanınıyor; hocalarımız, öğrencilerin yoğunluğunu göz önünde bulundurarak teslim tarihlerini belirliyor. Ayrıca, projelerde işbirliği yapma şansı da var, bu da süreci kolaylaştırıyor. Örneğin, mezuniyet projelerinde ekip çalışması sıkça tercih ediliyor.

**Tur 5 [İngilizce eğitim ve hazırlık]** `itu_curriculum_flexibility` RAG: `curriculum_overview_card` / ``
- Aday: Sunumları İngilizce mi yapıyoruz?
- Neco: Evet, bölümümüzde sunumlar genellikle İngilizce yapılıyor. Bu, hem uluslararası standartlara uyum sağlamak hem de İngilizce dil becerilerini geliştirmek için önemli bir fırsat. Hocalarımız, sunum becerilerini geliştirmek için öğrencilerimize rehberlik ediyor.

**Tur 6 [Hocalar ve eğitim kalitesi]** `itu_faculty_research` RAG: `differentiator_faculty_access_and_advising_2026` / `Hocalara ulaşım ve danışmanlık`
- Aday: Hocalara ulaşmak kolay mı?
- Neco: Evet, hocalarımıza ulaşmak genelde kolay. Bölüm web sitesinde e-posta adresleri açıkça yer alıyor ve öğrenci geri bildirimlerine göre, hocalarımız birebir görüşmelere de açıklar. Ayrıca, her öğrenciye danışman hoca atanıyor, bu sayede sürekli bir iletişim kanalı sağlanıyor. Sen hocalarla daha çok ders desteği için mi, yoksa erkenden bir projeye katılmak için mi iletişim kurmak istiyorsun?

**Tur 7 [Laboratuvarlar ve teknik olanaklar]** `itu_technical_resources` RAG: `department_employment_card` / ``
- Aday: Projeler için ekipman ödünç alınabiliyor mu?
- Neco: BBF aday sayfasındaki mezun araştırmasına göre öğrencilerin %54'ü mezun olmadan, %20'si mezuniyetten sonraki 6 ay içinde işe başlamıştır. Araştırmanın yılı sayfada belirtilmediği için oran bireysel iş garantisi değil, bölümün geçmiş sonucudur.

**Tur 8 [Staj ve iş deneyimi]** `itu_career_evidence` RAG: `career_employment_companies_card` / ``
- Aday: Okul staj yeri bulmaya yardımcı oluyor mu?
- Neco: İTÜ Bilgisayar aday sayfasındaki çalışmada mezunların %54'ü mezun olmadan işe başladı; 2026 Kariyer Zirvesi katılımcıları arasında Turkcell, THY, Siemens, ASELSAN ve Bosch vardı. Bu veri kişisel iş garantisi değildir.

**Tur 9 [Kariyer ve mezuniyet sonrası]** `itu_curriculum_flexibility` RAG: `erasmus_course_recognition_card` / ``
- Aday: Yurt dışında yüksek lisans yapmak kolay mı?
- Neco: Yurt dışında yüksek lisans yapmak için İTÜ Bilgisayar öğrencilerine önemli avantajlar sunuluyor. Programımız %100 İngilizce ve ABET akreditasyonuna sahip, bu da uluslararası kabul açısından fayda sağlıyor.

**Tur 10 [Projeler ve araştırma imkânları]** `compe_priority_top1000` RAG: `kalite_kanitlari__aday__kaliteli_mi___gercekten__1` / ``
- Aday: Açık kaynak projelere katkı yapılıyor mu?
- Neco: Evet, bölümümüzde açık kaynak projelere katkı yapmak teşvik ediliyor. Öğrenciler, çeşitli laboratuvarlar ve kulüpler aracılığıyla bu projelere dahil olabiliyorlar.

**Tur 11 [Uzmanlaşma alanları ve seçmeli dersler]** `concern_math_difficulty` RAG: `curriculum_workload_honesty_card` / `Ders yükü ve çalışma düzeni`
- Aday: Elektronik veya matematik bölümünden ders seçebilir miyim?
- Neco: Evet, İTÜ Bilgisayar öğrencileri, müfredatları dahilinde Elektronik veya Matematik bölümlerinden dersler alabiliyorlar. Bu esneklik, farklı disiplinlerden bilgi edinmene ve ilgi alanlarını genişletmene olanak tanıyor.

**Tur 12 [Çift anadal, yandal ve bölüm değiştirme]** `itu_double_major_transfer` RAG: `double_major_minor_card` / ``
- Aday: Elektronik ve Haberleşme ile çift anadal yapılabilir mi?
- Neco: ÇAP için en az 3,00 GNO, tüm derslerde başarı ve sınıfın üst %20'si gerekir; başvuru en erken 3., en geç 5. yarıyıldadır. Yandal eşiği 2,50'dir ve ikinci diploma değil sertifika verir.

**Tur 13 [Erasmus ve yurt dışı fırsatları]** `itu_graduation_requirements` RAG: `curriculum_overview_card` / ``
- Aday: Yurt dışında yaz okulu yapılabilir mi?
- Neco: Program C ve matematik temelinden veri yapıları, devreler, algoritmalar, veritabanı, mikroişlemci, mimari, işletim sistemi, yapay zekâ ve yazılım mühendisliğine ilerler; 8 yarıyıl, 130 yerel kredi ve 240 AKTS iki dönemlik tasarımla tamamlanır.

**Tur 14 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `itu_compe_differentiators` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği`
- Aday: İTÜ Bilgisayar Mühendisliğinin en güçlü yönü nedir?
- Neco: İTÜ Bilgisayar Mühendisliği'nin en güçlü yönlerinden biri, ABET akreditasyonu ve QS 2026 sıralamasında dünya 91.'si olması. Ayrıca, mezunlarımızın %54'ü mezun olmadan işe başlıyor, bu da sektördeki güçlü bağlantılarımızı gösteriyor. Kararında eğitim, kampüs, maliyet ve kariyerden hangisi daha ağır basıyor?

**Tur 15 [Kampüs hayatı]** `itu_compe_differentiators` RAG: `differentiator_qs_abet_faculty_card` / ``
- Aday: Kampüste kaybolmak kolay mı?
- Neco: İTÜ, QS 2026 Mühendislik ve Teknoloji'de dünya 91.'si; Bilgisayar Mühendisliği ABET akrediteli. Yapay zekâ çalışan Prof. Dr. Burak Berk Üstündağ'ın, öğrenci geri bildirimlerinde birebir ve e-posta yoluyla yardımcı olduğu aktarılıyor.

**Tur 16 [Kulüpler ve sosyal faaliyetler]** `itu_compe_differentiators` RAG: `ai_faculty_lab_answer_card` / `Yapay zekâ için hoca ve laboratuvar örnekleri`
- Aday: Yapay zekâ kulübüne katılabilir miyim?
- Neco: Bizim yapay zekâ-veri hattımızda Burak Berk Üstündağ, Hazım Kemal Ekenel ve Ayşe Tosun Kühn somut hoca örnekleri. Fakültedeki 18 araştırma laboratuvarı arasında AI Sistemleri, Veri Analitiği ve Görsel Zekâ başlıkları bulunuyor; lisans öğrencisi ilgili hocayla proje uyumunu konuşarak bu çalışmalara katılabiliyor.

**Tur 17 [Yurt ve barınma]** `itu_student_life_support` RAG: `scholarship_rank_501_1000` / `501-1000 başarı ödülü`
- Aday: Yurtlarda çalışma odası var mı?
- Neco: Evet, yurtlarımızda çalışma odası bulunuyor. Ayazağa Kampüsü'nde toplam 13 yurt var ve bu yurtlarda öğrenciler için çalışma alanları sunuluyor. Ayrıca, bursiyerler için standart yurtta %50 indirimli konaklama imkânı mevcut. Bu, ders çalışmak ve projeler üzerinde çalışmak için oldukça avantajlı.

**Tur 18 [İstanbul’da öğrenci olmak]** `itu_clubs_projects` RAG: `department_clubs_teams_card` / `Bölüm kulüpleri ve öğrenci takımları`
- Aday: İstanbul’da sosyal hayata para yetiştirmek zor mu?
- Neco: BBF'nin resmî sayfasında 5 bölüm kulübü sayılıyor: Yapay Zekâ, Blockchain Technologies, Oyun Tasarlama ve Geliştirme, İTÜ ACM ve GDG on Campus. Ayrıca W-TECH, DATABEES ve VCAMP adlı 3 öğrenci takımı tanıtılıyor.

**Tur 19 [Sosyal ortam ve öğrenci profili]** `itu_clubs_teams` RAG: `campus_student_social_food_spots_2026` / `Ayazağa'da sosyalleşme ve günlük yaşam`
- Aday: Hazırlıkta arkadaş edinmek kolay mı?
- Neco: 2026 öğrenci deneyiminde Ayazağa'da Selfish ve öğrencilerin çimlerde oturduğu Med Çim öne çıkıyor; tenis kortları da kullanılıyor. Bölüm tarafında Oyun Tasarlama ve Geliştirme ile İTÜ ACM'nin de bulunduğu 5 kulüp, ayrıca 3 öğrenci takımı var; daha sakin başlayan biri için tekrar eden etkinlikler tanışmayı kolaylaştırabilir.

**Tur 20 [Psikolojik kaygılar ve öğrenci desteği]** `itu_faculty_research` RAG: `differentiator_faculty_access_and_advising_2026` / `Hocalara ulaşım ve danışmanlık`
- Aday: Akademik danışmanlar öğrencilere yardımcı oluyor mu?
- Neco: Evet, akademik danışmanlar öğrencilere oldukça yardımcı oluyor. Her öğrenciye danışman hoca atanıyor ve bu hocalara ulaşmak genelde kolay. Öğrenci geri bildirimlerine göre, Burak Berk Üstündağ gibi hocalar, e-posta ve birebir görüşmelerle destek sağlıyor. Hoca iletişiminde seni düşündüren şey e-postana dönüş almak mı, yoksa birebir görüşebilmek mi?

**Tur 21 [Üniversiteye kabul ve tercih süreci]** `ideal_match_summary` RAG: `career_employment_companies_card` / ``
- Aday: Bilgisayar mühendisliğini gerçekten sevip sevmediğimi nasıl anlarım?
- Neco: Anladığım kadarıyla bilgisayar mühendisliğine ilgin var, ama tam olarak ne hissettiğini keşfetmek istiyorsun. Bu alanda projeler yaparak, yazılım dilleri öğrenerek veya topluluk etkinliklerine katılarak ilginin derinliğini ölçebilirsin.

**Tur 22 [Mezuniyet şartları]** `itu_graduation_requirements` RAG: `curriculum_overview_card` / ``
- Aday: Bölümü dört yılda bitirmek zor mu?
- Neco: Program C ve matematik temelinden veri yapıları, devreler, algoritmalar, veritabanı, mikroişlemci, mimari, işletim sistemi, yapay zekâ ve yazılım mühendisliğine ilerler; 8 yarıyıl, 130 yerel kredi ve 240 AKTS iki dönemlik tasarımla tamamlanır.

**Tur 23 [Doğal ve konuşma dilinde sorular]** `concern_math_difficulty` RAG: `faculty_area_ai_data` / `Yapay zekâ ve veri alanında çalışan hocalarımız`
- Aday: Hocalar öğrencileri çok zorluyor mu?
- Neco: Kaygın anlaşılır, İTÜ zorlayıcı bir okul. Ancak hocalarımız, genellikle öğrencilerin desteklenmesi için mentörlük yapıyorlar. Ayrıca, ders çalışma grupları ve tekrar dersi gibi destek mekanizmaları var.

**Tur 24 [Özel sosyal yaşam]** `itu_social_venues` RAG: `campus_cinema_match_viewing_card` / `Sinema ve toplu maç izleme deneyimi`
- Aday: Kampüste sinema kulübü veya topluca maç izleyebileceğimiz bir yer var mı?
- Neco: Evet, kampüste İTÜ Sinema Kulübü var ve çevrim içi olarak etkinlikler düzenliyor. Ayrıca, Dünya Kupası döneminde maçların topluca izlendiği Bestra'daki TV ekranı da kullanılıyor. Bu tür etkinlikler, sosyal hayatı canlandırmak için harika bir fırsat sunuyor!

**Tur 25 [Özel sosyal yaşam]** `itu_social_venues` RAG: `campus_food_shopping_official_card` / `Ayazağa'da yemek, pizza ve market seçenekleri`
- Aday: Pizza yiyebileceğim yer, gölet, stadyum ve marketlerden somut örnek verir misin?
- Neco: Kampüsümüzde Big Slice Pizza, Tarihi Unkapanı Pilavcısı ve EspressoLab gibi yerler bulunuyor. Ayrıca, yapay gölet ve 5.100 kişilik stadyum da kampüs alanında yer alıyor. Market olarak ise Migros, A101 ve Şok gibi seçenekler mevcut. Bu çeşitlilik, günlük yaşamını oldukça kolaylaştırır!

**Tur 26 [Özel açık ihtiyaç]** `itu_worship_facilities` RAG: `campus_worship_facilities_card` / `Ayazağa'da cami ve fakültede mescit`
- Aday: Kampüste cami ve fakültede mescit var mı?
- Neco: Evet, kampüsümüzde İTÜ Abdülhakim Sancak Camii bulunuyor. Ayrıca, Bilgisayar ve Bilişim Fakültesi içinde de bir mescit var. Bu alanlar, ibadet etmek isteyen öğrenciler için kullanılabilir. Erişim ayrıntılarını bina görevlilerinden öğrenebilirsin.

**Tur 27 [Özel açık ihtiyaç]** `itu_worship_facilities` RAG: `campus_worship_facilities_card` / `Ayazağa'da cami ve fakültede mescit`
- Aday: Ramazan ayında sınav sırasında namaz izni kesin veriliyor mu?
- Neco: Bu konuda net bir kural bulunmuyor, sınavlarda namaz izni uygulaması dersin hoca veya sınav komitesinin takdirine bağlı. Ramazan ayında ibadet etmek isteyen öğrencilerin, sınav tarihini ve saatlerini önceden planlayarak hocalarıyla iletişime geçmeleri faydalı olacaktır.

**Tur 28 [Özel tekrar]** `itu_faculty_research` RAG: `faculty_area_ai_data` / `Yapay zekâ ve veri alanında çalışan hocalarımız`
- Aday: Hocalara ulaşmak gerçekten kolay mı?
- Neco: Evet, hocalara ulaşmak genelde oldukça kolay. Her öğretim üyesinin kurumsal e-posta adresi bölüm sitesinde açıkça yer alıyor. Örneğin, Burak Berk Üstündağ, öğrencilerin e-posta yoluyla ve birebir görüşmelerle destek aldığı örneklerden biri.

**Tur 29 [Özel tekrar]** `itu_faculty_research` RAG: `differentiator_faculty_access_and_advising_2026` / `Hocalara ulaşım ve danışmanlık`
- Aday: Hocalarla e-posta veya birebir iletişim kurabilir miyim?
- Neco: hocalarla e-posta veya birebir iletişim kurmak mümkün. Her öğretim üyesinin e-posta adresi bölüm sitesinde bulunuyor ve genellikle sorularınızı yanıtlamaktan memnuniyet duyuyorlar. Ayrıca, her öğrenciye atanmış danışman hoca sayesinde, ders saatleri dışında da iletişim kurma şansınız var.

**Tur 30 [Özel sıralama]** `itu_financial_support` RAG: `admission_koc_compe_full_2025_direct` / `Koç Bilgisayar %100 burslu 2025 kabul gerçekliği` | sıralama=koc_full_scholarship_rank_context
- Aday: 950 sıralamayla Koç Bilgisayar tam burslu ve İTÜ Bilgisayar için durumum ne?
- Neco: 2025'te Koç Bilgisayar %100 burslu 113, İTÜ Bilgisayar 1.435 ile kapattı. 950 sıralamanla Koç'un %100 burslu kontenjanı geçen yıl gerçekçi değildi; bizim İTÜ Bilgisayar tabanının ise önündesin. İTÜ'de eğitim ücretsiz; 501-1000 paketinde ilk tercih koşuluyla yılda 9 ay aylık 6.750 TL başarı ödülü var. Yeni yıl garantisi veremem. Maddi tarafta senin için aylık burs mu, yoksa yurt desteği mi daha kritik?

**Tur 31 [Özel sıralama]** `itu_financial_support` RAG: `scholarship_rank_501_1000` / `501-1000 başarı ödülü`
- Aday: 950 sıralamaya göre İTÜ burs tutarım ve koşullarım ne?
- Neco: 950 sıralamanla İTÜ'de 2025'te ilk tercihinle yerleşirsen, yılda 9 ay boyunca aylık 6.750 TL başarı bursu alabilirsin. Bu bursun devamı için yılsonu Genel Not Ortalamanın (GNO) en az 2,50 olması ve hazırlık dönemini başarıyla tamamlaman gerekiyor.

---
