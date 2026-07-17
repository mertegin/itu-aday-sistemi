# Negotiation V2

## Sabit hedef

Sistemin negotiation hedefi öğrencinin, kendi motivasyon ve kaygılarına uyan
kaynaklı gerekçelerle İTÜ Bilgisayar Mühendisliği'ni tercih etme olasılığını
artırmaktır. Router, bandit ve utility katmanları bu hedefi değiştirmez.

Doğruluk sınırı hedefin parçasıdır: sistem kaynakta olmayan program, sayı,
garanti veya nitel başarı iddiası üreterek ikna etmeye çalışmaz.

## Tur akışı

1. Son mesaj yapılandırılmış sinyallere ayrılır.
2. Profil yeni bilgi, geri çekilen seçenek, çözülmüş kaygı ve karar durumuyla güncellenir.
3. Önceki argümanın engagement ve argument-effectiveness ödülleri ayrı hesaplanır.
4. FSM konuşma aşamasını belirler.
5. Current-turn router öğrencinin o anki sorusunu sınıflandırır.
6. Açık soru varsa ilgili argüman doğrudan seçilir; aksi halde bandit uygun argümanlar arasında öğrenir.
7. Negotiation utility katmanı aday uyumu ve İTÜ Bilgisayar hedef faydasını hesaplar.
8. Topic-aware RAG yalnızca bu tur için ilgili kaynakları getirir.
9. LLM kısa cevabı üretir; ethics, fact gate ve 65 kelimelik konuşma sınırı uygulanır.
10. Route, utility, reward ve RAG gerekçeleri XAI çıktısına yazılır.

## Current-turn router

Router geçmiş profilin güncel soruyu bastırmasını önler. Başlıca doğrudan yollar:

- hoca/lab/araştırma -> `itu_faculty_research`
- burs/maddi kaygı/geçim -> `itu_financial_support`
- yurt/yemekhane/kampüs -> `itu_student_life_support`
- startup/şirket/İTÜ Çekirdek -> `itu_entrepreneurship_ecosystem`
- yurt dışı/Erasmus -> `itu_global_opportunities`
- ders/ÇAP/yandal -> `itu_curriculum_flexibility`
- sıralama/taban -> `itu_admission_reality`
- kulüp/takım/proje -> `itu_clubs_projects`
- AI, elektronik, yazılım ve üniversite karşılaştırmaları -> ilgili özel argüman
- aile, matematik/zorluk ve istihdam kaygıları -> ilgili objection argümanı

## Maddi destek ve girişimcilik RAG'i

- `financial_support.yaml`, İTÜ Burslar ve Yurtlar Koordinatörlüğünün 2025
  başarı ödülü, ilk tercih, ihtiyaç ve yemek bursu kayıtlarını koşullarıyla tutar.
- Sıralama biliniyorsa ilgili başarı ödülü dilimi öne çıkar; bilinmiyorsa sistem
  başarı bursunu garanti etmeden ihtiyaç ve ilk tercih yollarını açıklar.
- Burs yanıtlarında yıl, ilk tercih ve GNO/hazırlık koşulları korunur.
- `entrepreneurship.yaml`, İTÜ Çekirdek'in 2025 tarihli resmi ekosistem,
  şirketleşme, istihdam ve yatırım verilerini tutar.
- Profilde eski bir maddi kaygı bulunsa bile açık girişimcilik sorusu önceliklidir;
  ekosistem toplamları kişisel yatırım veya kabul garantisi olarak sunulmaz.

## Ödül

İki ayrı çıktı vardır:

- `engagement`: Öğrenci konuşmaya devam ediyor, bilgi veriyor veya soru soruyor mu?
- `argument_effectiveness`: Önceki argüman kabul edildi mi, merak uyandırdı mı, reddedildi mi veya konu mu değişti?

Bandit ödülü:

```text
reward = 0.35 * engagement + 0.65 * argument_effectiveness
```

Bu ayrım sayesinde reddetme konuşma açısından sağlıklı bir sinyal olabilirken,
reddedilen argüman bandit tarafından başarılı öğrenilmez.

## Negotiation utility

Bandit geçmiş tepki getirisini hesaplar. Utility overlay ise her aday için:

```text
U = 0.55 * bandit_score
  + 0.30 * candidate_compatibility
  + 0.15 * itu_compe_goal_alignment
```

Alternatif bir argüman bandit seçimini en az `0.08` utility farkıyla geçerse
seçim override edilir ve XAI kaydına gerekçesi yazılır.

## Dinamik profil hafızası

- Aktif alternatifler argüman seçiminde kullanılır.
- Vazgeçilen/elenen seçenekler `inactive_alternatives` içinde tarihçede korunur.
- Çözülmüş kaygılar `resolved_concerns` içine taşınır.
- `decision_status` açık İTÜ Bilgisayar kararını kapanış sinyaline dönüştürür.
- `preference_events` geri çekme, yeniden etkinleştirme ve karar olaylarını tutar.

## FSM davranışı

- `S3_ARGUMENT_SELECTION` yeni oturumlarda ayrı konuşma turu tüketmez.
- 12. turda otomatik kapanış kaldırılmıştır.
- Yalnızca 18+ turdaki sessiz/etkileşimsiz konuşma yumuşak limite girer.
- Özet veya kapanıştan sonra yeni soru gelirse konuşma ilgili aşamadan yeniden açılır.

## Güvenlik

Fact gate sayılara ve kesinlik diline ek olarak kaynaklanmamış öğrenci
memnuniyeti, kadın temsili, yurt kalitesi ve işe yerleşme gibi nitel iddiaları
da denetler. Son yanıt robot konuşması için en fazla 65 kelimedir.
