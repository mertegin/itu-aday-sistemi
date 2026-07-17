# Sıralama Duyarlı Uzun Senaryo Raporu

- Ekli aday soru havuzu: 451 soru
- Gerçek API konuşması: 1
- Toplam tur: 7
- Mekanik olarak sorunsuz tur: 7
- Model/API fallback: 0
- Sıralama gerçekliği müdahalesi: 0
- Fact gate müdahalesi: 0
- Alaka müdahalesi: 1
- Uyarılar: `{}`

Mekanik `OK`, cevabın insan değerlendirmesinde kusursuz olduğu anlamına gelmez; tam konuşmalar aşağıdadır.

## rank_0005_ai_girisim - SAY 5 profili

Session: `sess_266365605b03`

**Tur 1 [Açılış]** `ai_vs_compe_foundation` RAG: `admission_itu_ai_data_2025_direct` / `İTÜ Yapay Zekâ ve Veri 2025 kabul gerçekliği`
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

**Tur 5 [Projeler ve araştırma imkânları]** `itu_research_projects` RAG: `project_competition_honesty_card` / `Ders projeleri ve yarışmaya dönüşen takım projeleri`
- Aday: Projeler yarışmalara gönderiliyor mu?
- Neco: Ders projeleri otomatik olarak yarışmaya gönderilmiyor; bunun bölüm genelinde yayımlanmış bir oranı da yok. Yarışma hedefleyen öğrenci projeyi danışman veya takımla büyütebilir: güncel öğrenci deneyiminde 19 üyeli İTÜNOM İHA, 2 roket ve 3 uydu geliştiren UZAYTEK ile TEKNOFEST'te yarışan İTÜ Sungur somut örnekler.

**Tur 6 [Kariyer ve mezuniyet sonrası]** `future_of_compe` RAG: `future_salary_ai_honesty_card` / `Yapay zekâ çağında iş ve maaş görünümü`
- Aday: Bilgisayar mühendislerinin maaşları gelecekte düşer mi?
- Neco: Maaşların kesin ne olacağını söylemek zor, ama ABD Çalışma İstatistikleri Bürosu 2023-2033 için yazılım istihdamında %17,9 büyüme öngörüyor. Rutin kodlama otomatikleşirken, sistem tasarımı, güvenlik ve yapay zekâ kurma becerileri daha fazla değer kazanacak.

**Tur 7 [İTÜ’nün diğer üniversitelerle karşılaştırılması]** `itu_compe_differentiators` RAG: `comparison_difficulty_honesty_card` / `İTÜ eğitiminin zorluğunu dürüst karşılaştırma`
- Aday: İTÜ’nün eğitimi diğer üniversitelere göre daha mı zor?
- Neco: İTÜ'nün eğitim programı, her yarıyılda 30 AKTS ile yoğun bir çalışma gerektiriyor; örneğin, BLG 312E'de 3 programlama ödevi ve BLG 335E'de 3 proje var. Öğrenci geri bildirimlerine göre, düzenli çalışma ve disiplin istiyor. Kararında eğitim, kampüs, maliyet ve kariyerden hangisi daha ağır basıyor?

---
