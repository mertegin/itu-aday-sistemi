# Kaynak Talimatlar — Mert

**Tarih:** 2026-07-09, 12:04
**Kaynak:** WhatsApp konuşması, Mert (proje talimatları)

Bu dosya proje gereksinimlerinin ham kaynağıdır. DESIGN.md bu talimatları yorumlayıp mimariye çeviren dokümandır. Talimatlar değişirse buradan takip edilir.

---

## Genel Amaç

Bu çalışma, tanıtım gününde gelen öğrencileri doğru argümanlarla İTÜ Bilgisayar Mühendisliği seçmeye ikna etmeyi amaçlayan, müzakere (negotiation) mantığına dayalı etkileşimli bir senaryo modelidir.

Sistem, adayın mevcut durumunu, motivasyonlarını ve şüphelerini "sorular sorarak" analiz edecek, adayı doğrudan yönlendirmek yerine kendi koşullarına uygun gerekçelerle ikna edecek.

**Hiçbir alternatif üniversite veya bölüm kötülenmeyecek**; tamamen "kişiye özel doğru eşleşme ve güçlü savunma algoritmaları" üzerinden ilerlenecektir.

---

## 1. Aşama: Profil ve Kararsızlık Analizi (Giriş)

Süreç, adayın netlik seviyesini ölçmek için şu sorular etrafında şekillenecek bir kararsızlık matrisiyle başlar:

- **Mühendislik Kesin mi?** Aday mühendislik mi istiyor, yoksa Tıp gibi tamamen farklı bir alana mı kayma eğiliminde?
- **Üniversite Tercihi Net mi?** İTÜ'yü kesin seçmiş mi, yoksa Koç Üniversitesi gibi güçlü alternatifler arasında mı kalıyor?

---

## 2. Aşama: Karakter ve Motivasyon Tiplerine Göre Savunma Algoritmaları

Adayın eğilimlerine göre sistem arkada belirli savunma mekanizmalarını ve dokümanları devreye sokacaktır:

- **Tıp ve Mühendislik Arasında Kalanlar İçin:** Sağlık alanında teknolojinin gelişimine vurgu yapılabilir.

- **Koç ve İTÜ Bilgisayar Arasında Kalanlar İçin:** Vakıf üniversitesi imkanlarına karşı, İTÜ'nün köklü ekolü, devasa mezun ağı, sektördeki ağırlığı ve özellikle **ilk 1000 öğrencilerine sağlanan özel İTÜ bursları**, yurt imkanları ve akademik teşvikler ön plana çıkarılabilir.

- **İTÜ Yapay Zeka mı, Bilgisayar mı?** Yapay zekanın aslında bilgisayar mühendisliğinin güçlü bir alt kümesi olduğu, bilgisayar mühendisliği diplomasının adaya çok daha geniş bir esneklik ve temel kazandıracağı gerekçelendirilebilir.

**Bu liste uzayabilir** — Elektronik isteyenler olabilir, çok para kazanmak isteyen biri olabilir ya da sadece bilim yapmak için tercih yapacak biri gelebilir. Kısaca tüm bunları göz önüne alarak bir tasarım yapmalıyız.

---

## 3. Aşama: Etkileşim ve Test Modülü

Sistemin sadece statik bir metin olarak kalmaması, dinamik bir yapıya bürünmesi için:

- Kullanıcıya durum tabanlı sorular sorulacak ve verdiği cevaplara göre kişiselleştirilmiş bir **"İdeal Tercih Analizi"** uygulanacaktır.
- Sistem, adayın kendi profiline göre neden İTÜ Bilgisayar'ı seçmesi gerektiğine dair koşullardan bahsedecektir.

---

## Genişleme Notu

Bu çalışmayı şu an İTÜ Bilgisayar Müh. için uyguluyoruz ama ileride İTÜ'deki farklı bölümler ya da farklı üniversitelerin farklı bölümlerine de genişletilebilir.

**Projenin ismi:** Negotiation Tabanlı Aday Öğrenci Sistemi
