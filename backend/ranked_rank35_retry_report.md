# Sıralama Duyarlı Uzun Senaryo Raporu

- Ekli aday soru havuzu: 451 soru
- Gerçek API konuşması: 1
- Toplam tur: 12
- Mekanik olarak sorunsuz tur: 12
- Model/API fallback: 0
- Sıralama gerçekliği müdahalesi: 1
- Fact gate müdahalesi: 2
- Alaka müdahalesi: 0
- Uyarılar: `{}`

Mekanik `OK`, cevabın insan değerlendirmesinde kusursuz olduğu anlamına gelmez; tam konuşmalar aşağıdadır.

## rank_0035_arastirma - SAY 35 profili

Session: `sess_fb2fc5db25da`

**Tur 1 [Açılış]** `active_listening` RAG: `department_faculty_labs_card` / `` | sıralama=ahead_of_itu_compe_2025
- Aday: Selam, adım Arda. SAY sıralamam 35; araştırma, yurt dışı doktora ve güçlü akademik kadro benim için önemli.
- Neco: İTÜ Bilgisayar 2025'te 1.435 ile kapattı; 35 sıralaman geçen yılki tabanın önünde. Bu güçlü bir konum, fakat yeni yılın tabanı oluşmadan garanti veremem. Sen hocalarla daha çok ders desteği için mi, yoksa erkenden bir projeye katılmak için mi iletişim kurmak istiyorsun?

**Tur 2 [Özel sıralama kontrolü]** `itu_financial_support` RAG: `scholarship_rank_11_100` / `11-100 başarı ödülü`
- Aday: 35. olduğum için İTÜ başarı bursunda hangi tutar ve koşullar geçerli?
- Neco: İTÜ'de 2025'te Türkiye 11-100 derecesiyle kayıt yaptıranlara, hazırlık dahil 1+4 yıl boyunca her ay 10.000 TL başarı ödülü veriliyor. Bursun devam etmesi için yıl sonunda GNO'nun en az 2,50 olması ve hazırlık dönemini başarıyla tamamlaman gerekiyor.

**Tur 3 [Özel sıralama kontrolü]** `itu_research_projects` RAG: `undergraduate_research_card` / ``
- Aday: Hocalarımızla lisans öğrencisiyken proje yapmak gerçekten mümkün mü, örnek verir misin?
- Neco: İTÜ'de 18 araştırma laboratuvarı var; örneğin, Robotik Laboratuvarı'nda lisans öğrencileri projelerde aktif rol alabiliyor. Hocalarımızdan Burak Berk Üstündağ yapay zekâ projeleri üzerinde çalışıyor.

**Tur 4 [Özel sıralama kontrolü]** `money_motivated_data` RAG: `admission_itu_compe_2025_direct` / `İTÜ Bilgisayar 2025 kabul gerçekliği`
- Aday: İTÜ Bilgisayar'ı diğer güçlü okullardan sayılarla ayıran şey ne?
- Neco: Ayrıca, mezunlarımızın %54'ü mezun olmadan iş buluyor. Bu güçlü bağlantılar ve eğitim kalitesi, mezunlarımıza önemli avantajlar sağlıyor.

**Tur 5 [Laboratuvarlar ve teknik olanaklar]** `itu_faculty_research` RAG: `department_faculty_labs_card` / ``
- Aday: Laboratuvarlardaki bilgisayarlar güncel mi?
- Neco: BBF'nin güncel sayfasında 37 öğretim üyesi (19 profesör, 11 doçent, 7 doktor öğretim üyesi), 10 tam zamanlı öğretim görevlisi ve 18 araştırma laboratuvarı yer alıyor; ayrıca 53 araştırma görevlisi bildiriliyor. Hoca iletişiminde seni düşündüren şey e-postana dönüş almak mı, yoksa birebir görüşebilmek mi?

**Tur 6 [Erasmus ve yurt dışı fırsatları]** `itu_erasmus_mobility` RAG: `erasmus_internship_card` / ``
- Aday: Bilgisayar Mühendisliği için hangi üniversitelere gidilebilir?
- Neco: Erasmus stajı öğrenim alanıyla ilgili olmalı ve en az 60 gün, en çok 12 ay sürmelidir. Hazırlık ve ilk sınıfta hemen hareketlilik yapılamaz; ilk sınıf öğrencisi sonraki yıl için başvurabilir. Dil eşiği B1/65'tir.

**Tur 7 [Laboratuvarlar ve teknik olanaklar]** `itu_technical_resources` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği`
- Aday: Yapay zekâ projeleri için GPU desteği sağlanıyor mu?
- Neco: İTÜ Yapay Zekâ ve Veri Mühendisliği 2025'te 1.947 en düşük, 102 en yüksek ve 1.438 ortalama SAY başarı sırasıyla öğrenci aldı; genel kontenjanı 30'du. 2.000 ve üzerindeki bir sıra, geçen yılın 1.947 tabanının gerisindedir ve garanti gibi anlatılamaz.

**Tur 8 [Erasmus ve yurt dışı fırsatları]** `itu_erasmus_mobility` RAG: `erasmus_internship_card` / ``
- Aday: Erasmus dil sınavı zor mu?
- Neco: Erasmus dersleri otomatik sayılmaz: 2 temel belge, OLA ve Tanınma Belgesi, bölüm/Erasmus koordinatörü onayıyla hazırlanır. Dönüşte karşı kurum transkripti gerekir; ders adı ve AKTS uyuşmazsa İTÜ transkriptine FF işlenebilir.

**Tur 9 [Hocalar ve eğitim kalitesi]** `itu_curriculum_flexibility` RAG: `curriculum_overview_card` / ``
- Aday: Bölüm müfredatı ne sıklıkla yenileniyor?
- Neco: İTÜ Bilgisayar Mühendisliği müfredatı düzenli olarak güncelleniyor; her yıl, yeni teknolojiler ve endüstri ihtiyaçlarına göre gözden geçiriliyor. Bu sayede, öğrencilerimiz hem güncel bilgiye sahip oluyor hem de kariyer fırsatlarına daha iyi hazırlanıyor.

**Tur 10 [Laboratuvarlar ve teknik olanaklar]** `itu_technical_resources` RAG: `department_employment_card` / ``
- Aday: Projeler için ekipman ödünç alınabiliyor mu?
- Neco: BBF aday sayfasındaki mezun araştırmasına göre öğrencilerin %54'ü mezun olmadan, %20'si mezuniyetten sonraki 6 ay içinde işe başlamıştır. Araştırmanın yılı sayfada belirtilmediği için oran bireysel iş garantisi değil, bölümün geçmiş sonucudur.

**Tur 11 [Hocalar ve eğitim kalitesi]** `itu_faculty_research` RAG: `department_faculty_labs_card` / ``
- Aday: Akademisyen olmak isteyen öğrencilere destek veriliyor mu?
- Neco: BBF'nin güncel sayfasında 37 öğretim üyesi (19 profesör, 11 doçent, 7 doktor öğretim üyesi), 10 tam zamanlı öğretim görevlisi ve 18 araştırma laboratuvarı yer alıyor; ayrıca 53 araştırma görevlisi bildiriliyor.

**Tur 12 [Hocalar ve eğitim kalitesi]** `itu_curriculum_flexibility` RAG: `curriculum_overview_card` / ``
- Aday: Dersler çoğunlukla slayttan mı işleniyor?
- Neco: Derslerimiz genellikle slayt destekli, ancak uygulamalı ve interaktif yöntemlerle de zenginleştiriliyor. Bu, teorik bilginin yanı sıra pratiği de ön planda tutmamıza olanak tanıyor. Örneğin, yazılım mühendisliği derslerinde projelerle öğrenme fırsatı buluyorsun.

---
