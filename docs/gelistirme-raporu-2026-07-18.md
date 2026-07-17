# İTÜ Aday Sistemi Geliştirme Raporu

Tarih: 18 Temmuz 2026

## Hedef

Sistemin adayla İTÜ'lü bir içeriden konuşması, İTÜ Bilgisayar Mühendisliğini dürüst ve kaynaklı biçimde öne çıkarması, genel ifadeler yerine sayı ve örnek kullanması amaçlandı. Rakip üniversiteler kötülenmeden, adayın sıralamasına göre gerçekçi kabul değerlendirmesi yapılması korundu.

## Yapılan Ana Değişiklikler

- 2025 kabul verileri için İTÜ Bilgisayar, İTÜ Yapay Zekâ ve Veri, Koç Bilgisayar tam burslu ve YTÜ Bilgisayar kartları eklendi.
- 1.435 İTÜ Bilgisayar ve 1.947 İTÜ Yapay Zekâ ve Veri tabanlarına göre sıralama gerçekliği kapısı eklendi.
- 2.000 ve 2.500 sıralama profillerinde boş umut vermeden gerçekçi İTÜ alternatifleri üretme kuralı eklendi.
- İTÜ başarı ödülü dilimleri sıralamaya bağlandı; 11-100 dilimindeki resmî `10.000 TL + 10.000 TL` ifadesinin yarım söylenmesini engelleyen kontrol eklendi.
- Hoca, laboratuvar, müfredat, kariyer, yurt, yemek, kampüs, sosyal alan, girişimcilik ve yazılım lisansı bilgileri genişletildi.
- Selfiş, MED çimleri, Bestra, gölet, stadyum, pizza, Migros/A101/Şok ve kampüs yemek noktaları sosyal yaşam kartlarına eklendi.
- İbadet alanları yalnız açıkça sorulduğunda nötr biçimde yanıtlanıyor; görünüşten veya isimden dinî profil çıkarımı yapılmıyor.
- Aynı cevabı arka arkaya verme, alakasız profil ilgisinin yeni soruyu ele geçirmesi ve kıvrımlı apostrof gibi Türkçe yazım biçimleri için düzeltmeler yapıldı.

## Yeni Doğrudan Cevap Kartları

- Hocaların sektör deneyimi hakkında kanıt sınırı
- Ders içeriklerinin güncelliği ve BLG 483E örneği
- MATLAB, Office 2021, SPSS ve Visual Studio lisansları
- Robotik Laboratuvarı ve lisans öğrencisi erişimi
- Erasmus hibe tutarı ve masrafın tamamını karşılamama uyarısı
- ABD değişimi ile ayrı çift diploma yollarının ayrımı
- Laboratuvar bilgisayarlarının güncelliği hakkında dürüst cevap
- Yapay zekâ projelerinde GPU erişimi hakkında dürüst cevap
- Bilgisayar Mühendisliği Erasmus üniversite örnekleri
- Erasmus B1/65 yabancı dil eşiği
- Müfredat yenileme sıklığı hakkında dürüst cevap
- Proje ekipmanı ödünç alma hakkında kanıt sınırı
- Akademik kariyer için LÖKAP ve laboratuvar yolu
- Slayt, programlama ödevi ve proje dengesini açıklayan kart

## Kontrol Sonuçları

- Ekli dosyadan 22 kategoride 451 aday sorusu ayrıştırıldı.
- 451 sorunun tamamı yerel RAG kapsama taramasından geçti; bu kontrol yalnız belge bulunabilirliğini ölçer, cevap kalitesini tek başına kanıtlamaz.
- Gerçek API ile son tamamlanan kontrol 1 profil ve 12 turdur. Bu konuşma `sess_fb2fc5db25da` kimliğiyle kaydedildi.
- Bu gerçek konuşmada bulunan yeni yönlendirme hataları sonrasında dokuz ayrı doğrudan kart ve yönlendirme düzeltmesi eklendi.
- Kullanıcının isteği üzerine sonraki gerçek LLM testleri durduruldu. Son eklenen kartlar gerçek LLM sorgusu yerine yönlendirici ve RAG üst-kart seçimiyle kontrol edildi.
- Son statik kontrolde hedeflenen dokuz sorunun dokuzu da doğru doğrudan cevap kartını birinci sırada getirdi.

## Bilinen Sınırlar

- Gelecek yılın YKS taban sırası garanti edilemez; sistem yalnız 2025 verisini referans alır.
- Laboratuvar GPU modeli, bilgisayar yaşı ve bölüm geneli ekipman ödünç politikası yayımlanmadığı için sistem bunları garanti etmez.
- Erasmus anlaşmaları, kontenjanları ve hibeli öğrenci sayısı dönem çağrısına göre değişir.
- Bestra maç gösterimleri ve fakülte mescidi öğrenci geri bildirimidir; dönemsel değişebilir.
- Stadyumun kesin güncel açılış-kapanış saatleri doğrulanmış resmî kartta bulunmuyor.

## Elle Deneme

Arayüz: http://127.0.0.1:8000

Geçmiş konuşmalar: http://127.0.0.1:8000/conversations.html

FSM görünümü: http://127.0.0.1:8000/fsm.html
# 18 Temmuz Ek Mimari Düzeltme: RAG Konuşmacı Değil, Kanıt Katmanı

- RAG kartları final cevap olarak kopyalanmıyor; iddia, örnek, kaynak ve güven düzeyi içeren kanıt paketine çevriliyor.
- İlk LLM taslağı artık relevance/evidence/fact/admission/scholarship/repetition kontrolleri tarafından doğrudan silinmiyor.
- Kontroller düzeltme notu üretiyor; LLM en fazla bir kez, yalnız seçilen kanıtlarla yeniden yazıyor.
- Kart tabanlı deterministik cevap yalnız API hatasında veya ikinci yazım da kritik doğrulamadan geçmezse kullanılıyor.
- Her turda ham taslak, seçilen kanıt kimlikleri, düzeltme notları, yeniden yazım ve final cevap `response_pipeline` altında saklanıyor.
- `taban` kelimesinin `veritabanı` içinde eşleşmesi ve `OLA` ifadesinin `olarak` içinde eşleşmesi kelime sınırı kontrolüyle giderildi.
- Veritabanı, bulut teknolojileri ve genel öğrenci ortamı ayrı yönlendirme başlıkları oldu.
- BLG 361E için resmî katalogdan uygulama/SQL/takım projesi ayrıntısı; bulut için HPC-Bulut laboratuvar alanı ve zorunlu ders konusundaki dürüst sınır eklendi.

