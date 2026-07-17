"""Savunma argümanları kataloğu — Majidov'un system prompt Bölüm 4-8'inden türetildi."""
from dataclasses import dataclass, field


@dataclass
class DefenseArgument:
    id: str
    label: str                    # Kullanıcıya gösterilebilir kısa isim (XAI için)
    technique: str                # Bandit arm — kullanılan ikna tekniği
    trigger_hint: str             # Ne zaman iyi (bandit + LLM için ipucu)
    talking_points: list[str]     # LLM promptuna injecte edilecek somut noktalar
    expected_pushback: list[str] = field(default_factory=list)


# --- ARGÜMAN KATALOĞU ---
ARGUMENTS: dict[str, DefenseArgument] = {

    # === İlk keşif / soru sorma ===
    "socratic_probe": DefenseArgument(
        id="socratic_probe",
        label="Sokratik soru",
        technique="active_discovery",
        trigger_hint="Profil eksik, ilgi/hedef netleşmemiş",
        talking_points=[
            "Adayın kendi motivasyonunu keşfetmesine yardım et.",
            "Açık uçlu bir tek soru sor — anket havası olmasın.",
            "Örnek: 'Bir problemi çözerken donanıma mı yazılıma mı daha çok ilgi duyuyorsun?'",
            "Örnek: 'Bir şirket kurmak mı, araştırmacı olmak mı sana daha çekici geliyor?'",
        ],
    ),

    "rank_probe": DefenseArgument(
        id="rank_probe",
        label="YKS sıralama sorusu",
        technique="active_discovery",
        trigger_hint="YKS sıralaması henüz bilinmiyor — Bilgisayar önermek için kritik veri",
        talking_points=[
            "Sohbetin doğal akışı içinde sıralamayı öğrenmeye çalış — anket sorusu gibi durmasın.",
            "İlk kez soruyorsan bağlam ver: 'Sana en doğru yönlendirmeyi yapabilmem için sıralamanı bilmem iyi olur.'",
            "Sonuç açıklanmadıysa deneme sıralamasını veya hedef aralığını sor — 'yaklaşık bir aralık da yeter' de.",
            "Aday bilmiyorsa/söylemek istemiyorsa ISRAR ETME — ilgi alanlarından devam et, sıralamayı sonra tekrar sorma.",
        ],
    ),

    "active_listening": DefenseArgument(
        id="active_listening",
        label="Aktif dinleme / yansıtma",
        technique="active_listening",
        trigger_hint="Aday duygusal veya karışık bir şey söyledi; anladığını hissettirmen gerekiyor",
        talking_points=[
            "Söylediğinin kısa bir özetini kendi kelimelerinle geri yansıt — ama 'doğru mu anladım' gibi teyit isteme.",
            "Onaylandığını hissettir, ama pohpohlama, tekrar sözcüğü olma.",
            "Doğal bir geçişle konuşmayı bir adım ileri taşı: adayın söylediğini kısa biçimde karşıla ve yeni, somut bir bilgi getir.",
            "'Anladım.', 'Mantıklı.', 'Bu önemli bir nokta.' gibi kısa onayları kullanabilirsin — ama her turda tekrar etme.",
        ],
    ),

    # === Bilgisayar Müh. lehine argümanlar (İlk 1000 için) ===
    "compe_priority_top1000": DefenseArgument(
        id="compe_priority_top1000",
        label="Bilgisayar önceliği (ilk 1000)",
        technique="framing + commitment",
        trigger_hint="Aday ilk 1000'de, ilgi yazılım/AI/girişim/yurt dışı yönünde",
        talking_points=[
            "İTÜ Bilgisayar 2025 tabanı yaklaşık 1.435; ilk 1000 bu tabanın belirgin biçimde önündedir, fakat yerleşme garantisi verme.",
            "Adayın ilgi/hedefini Bilgisayar'ın somut fırsatlarıyla eşleştir.",
            "Somut örnek ver (Çekirdek, AI lab, mezun yolu) — genel iddia değil.",
            "Adayın kendi hedefini bir kez anıp İTÜ Bilgisayar fırsatının o hedefe nasıl hizmet ettiğini söyle; teyit sorusu sorma.",
        ],
    ),

    "compe_borderline_1000_1500": DefenseArgument(
        id="compe_borderline_1000_1500",
        label="Bilgisayar sınırda (1000-1500)",
        technique="framing + honesty",
        trigger_hint="Sıralama 1000-1500 arası, ilgi Bilgisayar yönünde",
        talking_points=[
            "Dürüst çerçeve: '2025 sırası ~1.435, senin için ulaşılabilir ama sınırda.'",
            "İkinci güçlü seçenek olarak Yapay Zeka ve Veri Müh. hazırda tut (~1.947).",
            "Kesin garanti verme, 'geçen yılki verilere göre' de.",
        ],
    ),

    # === Kararsızlık dallarına özel savunmalar ===
    "med_vs_eng_health_tech": DefenseArgument(
        id="med_vs_eng_health_tech",
        label="Tıp ↔ Mühendislik köprüsü",
        technique="framing + future_self",
        trigger_hint="Aday tıp ile mühendislik arasında kararsız",
        talking_points=[
            "Sağlık teknolojisi kesişimini göster: biyomedikal AI, tıbbi görüntüleme, klinik karar destek.",
            "İTÜ'de Sağlık Bilişimi ve Biyoinformatik laboratuvarları var.",
            "'Sağlığa dokunmak' motivasyonu CS ile karşılanabilir — direkt hasta bakmak istiyorsa tıp doğal.",
            "Kesin bir öneri dayatma; kesişimi göster, adayın kendi tercih etmesine bırak.",
        ],
        expected_pushback=["Ama ben hasta ile birebir çalışmak istiyorum"],
    ),

    "koc_vs_itu_value": DefenseArgument(
        id="koc_vs_itu_value",
        label="Koç ↔ İTÜ (burs + ekol)",
        technique="social_proof + authority",
        trigger_hint="Aday Koç ile İTÜ arasında",
        talking_points=[
            "Koç'un teklifini küçümseme; maddi teklif adayın kararında merkeziyse bunu ilk cümlede kabul et.",
            "Adayın sıralamasına uyan İTÜ başarı ödülünü, ilk tercih/devam koşullarını ve yurt desteğini yalnız RAG'deki güncel tutarlarla karşılaştır.",
            "Koç'un net aylık veya yıllık teklif tutarı bilinmiyorsa kısa ve doğrudan sor; gerçek toplam değer karşılaştırması için bu bilgi gerekir.",
            "250+ yıllık köklü ekol, devasa mezun ağı, sektörde ağırlık.",
            "QS Mühendislik 91 — dünyada ilk 100'deki tek Türk üniversitesi.",
            "İki üniversite de saygın; karşılaştırmayı mali destek, eğitim ekosistemi ve adayın hedefi üzerinden somutlaştır.",
        ],
    ),

    "ai_vs_compe_foundation": DefenseArgument(
        id="ai_vs_compe_foundation",
        label="Yapay Zeka ↔ Bilgisayar (temel)",
        technique="framing + authority",
        trigger_hint="Aday İTÜ Yapay Zeka Müh. mi Bilgisayar Müh. mi kararsız",
        talking_points=[
            "AI, bilgisayar mühendisliğinin güçlü bir alt kümesi.",
            "Bilgisayar diploması geniş esneklik verir — AI'ya, sistemlere, gömülüye, girişime dallanabilirsin.",
            "İTÜ CompE çekirdeğinde zaten AI + Learning From Data dersleri var.",
            "Komşu bölüm (Yapay Zeka ve Veri) ile çift anadal/yandal yapılabilir.",
        ],
    ),

    "electronics_vs_compe_overlap": DefenseArgument(
        id="electronics_vs_compe_overlap",
        label="Elektronik ↔ Bilgisayar (kesişim)",
        technique="framing",
        trigger_hint="Aday elektronik ile bilgisayar arasında",
        talking_points=[
            "İTÜ CompE çekirdeği donanım açısından güçlü: Digital Circuits, Microprocessor Systems, Computer Architecture.",
            "Gömülü sistemler, IoT, RISC-V (YONGA proje takımı) — CompE tarafından da erişilebilir.",
            "Elektronik-Haberleşme daha çok sinyal/haberleşme/çip odaklı; CompE daha çok sistem/yazılım/algoritma.",
            "İki bölüm arasında çift anadal olabilir.",
        ],
    ),

    "money_motivated_data": DefenseArgument(
        id="money_motivated_data",
        label="Para/kariyer motivasyonu",
        technique="authority + social_proof",
        trigger_hint="Adayın öncelikli motivasyonu maddi kazanç",
        talking_points=[
            "Yazılım mühendisliği Türkiye'de en yüksek başlangıç maaşlarından; İstanbul giriş seviyesi ~985 bin TL/yıl (topluluk verisi).",
            "ABD BLS: yazılım istihdamı 2023-2033 %17,9 büyüme (ortalama üstü).",
            "İTÜ Kariyer Zirvesi 2005'ten beri yüzlerce firma; ARI Teknokent Maslak kampüsünde.",
            "Sayıları abartma; 'topluluk verisi' / 'genel eğilim' diye çerçevele.",
        ],
    ),

    "science_motivated_labs": DefenseArgument(
        id="science_motivated_labs",
        label="Bilim/araştırma motivasyonu",
        technique="authority + future_self",
        trigger_hint="Aday akademisyenlik, araştırma, doktora yönelimli",
        talking_points=[
            "Güncel BBF sayfasında 18 araştırma laboratuvarı var: AI Sistemleri, NLP, Görsel Zekâ, Biyoinformatik, Robotik ve daha fazlası.",
            "37 öğretim üyesi, 10 tam zamanlı öğretim görevlisi ve 53 araştırma görevlisi bulunuyor.",
            "Yurt dışı doktora yolu için ABET akreditasyonu + %100 İngilizce büyük avantaj.",
            "Erasmus + ABD çift diploma programları.",
        ],
    ),

    "itu_faculty_research": DefenseArgument(
        id="itu_faculty_research",
        label="İTÜ Bilgisayar hoca ve araştırma örnekleri",
        technique="authority + concrete_evidence",
        trigger_hint="Aday hoca, laboratuvar, araştırma alanı veya akademik kadro soruyor",
        talking_points=[
            "Adayın sorduğu alana doğrudan cevap ver; RAG varsa 1-2 ilgili hoca/lab örneği kullan.",
            "İsim ve araştırma alanı ilişkisini yalnızca kaynakta açıkça varsa kur.",
            "Ulaşılabilirlik gibi öğrenci deneyimlerini resmi özellik gibi değil, açıkça öğrenci geri bildirimi olarak aktar.",
            "Bu akademik çeşitliliği İTÜ Bilgisayar'ın geniş uzmanlaşma imkanıyla ilişkilendir.",
        ],
    ),

    "itu_curriculum_flexibility": DefenseArgument(
        id="itu_curriculum_flexibility",
        label="Müfredat ve akademik esneklik",
        technique="concrete_evidence + framing",
        trigger_hint="Aday ders, müfredat, ÇAP/yandal veya lisansüstü geçiş soruyor",
        talking_points=[
            "Önce sorulan ders/program ayrıntısını kaynaklı biçimde cevapla.",
            "Bilgisayar Mühendisliği'nin geniş temelini AI, sistem, yazılım ve donanım yollarına bağla.",
            "Kaynakta koşul veya program yoksa mümkünmüş gibi konuşma; resmi doğrulama öner.",
        ],
    ),

    "itu_first_year_curriculum": DefenseArgument(
        id="itu_first_year_curriculum",
        label="İlk sınıf resmî ders planı",
        technique="direct_answer + concrete_evidence",
        trigger_hint="Aday ilk sınıf, ilk yıl veya ilk iki yarıyıl derslerini soruyor",
        talking_points=[
            "Yalnızca resmî plandaki 1. ve 2. yarıyıl derslerini cevapla.",
            "İleri sınıf veya seçmeli dersleri ilk sınıf dersi gibi sunma.",
            "Dersleri yarıyıl bazında kısa ve okunabilir biçimde listele.",
        ],
    ),

    "itu_curriculum_beginner": DefenseArgument(
        id="itu_curriculum_beginner",
        label="Programlama deneyimi olmayan aday için müfredat",
        technique="normalization + concrete_evidence",
        trigger_hint="Aday bölümün yalnızca kod olup olmadığını veya deneyimsiz başlayınca zorlanıp zorlanmayacağını soruyor",
        talking_points=[
            "Kaygıyı normalleştir ve bölümün matematik, fizik, sistem, etik ve yazılım bileşenlerini somutlaştır.",
            "C programlamanın ikinci yarıyıldaki giriş dersiyle başladığını kaynaklı biçimde söyle.",
            "Başarı garantisi verme; düzenli pratik, ders ve çalışma desteğinin önemini dürüstçe belirt.",
        ],
    ),

    "itu_curriculum_overview": DefenseArgument(
        id="itu_curriculum_overview",
        label="Bilgisayar Mühendisliği müfredatının ilerleyişi",
        technique="concrete_evidence + future_self",
        trigger_hint="Aday bölümde tam olarak ne öğretildiğini genel olarak soruyor",
        talking_points=[
            "Programın ilk yıldan tasarım projesine uzanan ilerleyişini somut ders alanlarıyla anlat.",
            "Bölümü yalnızca araştırma alanları veya yalnızca kod yazma olarak daraltma.",
            "Bu geniş temeli adayın daha sonra yazılım, sistem veya yapay zekâ yönü seçebilmesine bağla.",
        ],
    ),

    "itu_curriculum_details": DefenseArgument(
        id="itu_curriculum_details",
        label="Programlama, sistem ve proje dersleri",
        technique="direct_answer + concrete_evidence",
        trigger_hint="Aday programlama dilleri, sistem dersleri, proje yapısı veya teori-uygulama dengesini soruyor",
        talking_points=[
            "Sorulan alt başlığa ilk cümlede doğrudan cevap ver; tüm müfredatı dökme.",
            "C, C/C++, Unix ödevleri, grup projesi veya güncel seçmelilerden ilgili 1-2 somut örnek kullan.",
            "Bir programlama dilinin öğretildiğini yalnız resmî katalog açıkça destekliyorsa söyle.",
        ],
    ),

    "itu_academic_workload": DefenseArgument(
        id="itu_academic_workload",
        label="Ders yükü ve çalışma düzeni",
        technique="expectation_setting + risk_reduction",
        trigger_hint="Aday ders yükü, sınav, ödev, kalma veya çalışma süresi konusunda kaygılı",
        talking_points=[
            "İTÜ Bilgisayar'ın zorlayıcı olabileceğini saklama; güncel plandaki 30 AKTS/dönem yapısıyla somutlaştır.",
            "Yayımlanmamış haftalık saat, kalma oranı veya not dağılımı uydurma.",
            "Düzenli çalışma ile algoritma-sistem-lab dizisinin adaya kazandırdığı teknik temeli ilişkilendir.",
        ],
    ),

    "itu_technical_resources": DefenseArgument(
        id="itu_technical_resources",
        label="Laboratuvar ve teknik çalışma kaynakları",
        technique="authority + concrete_evidence",
        trigger_hint="Aday laboratuvar, cihaz, sunucu, GPU, kütüphane veya çalışma alanı soruyor",
        talking_points=[
            "18 araştırma laboratuvarı ve 7/24 Mustafa İnan Kütüphanesi gibi doğrulanmış olanakları kullan.",
            "GPU modeli, cihaz adedi veya lisans öğrencisine sınırsız erişim gibi kaynakta olmayan ayrıntıyı garanti etme.",
            "Olanakları adayın somut ilgi alanıyla eşleştir.",
        ],
    ),

    "itu_internship_pathways": DefenseArgument(
        id="itu_internship_pathways",
        label="Zorunlu staj yolu",
        technique="direct_answer + employability",
        trigger_hint="Aday staj süresi, kapsamı, zorunluluğu veya çevrim içi stajı soruyor",
        talking_points=[
            "40 iş günü ve iki ayrı kurumda en az 20'şer gün koşulunu açık söyle.",
            "Yazılım ve kabul edilebilir donanım işi örneklerini kullan; staj yeri bulma garantisi verme.",
            "Staj yapısını İTÜ Bilgisayar öğrencisinin iki ayrı iş ortamı görmesi avantajına bağla.",
        ],
    ),

    "itu_research_projects": DefenseArgument(
        id="itu_research_projects",
        label="Lisans araştırması ve hoca projeleri",
        technique="authority + future_self + concrete_evidence",
        trigger_hint="Aday lisans araştırması, laboratuvara katılım, yayın veya hocayla proje soruyor",
        talking_points=[
            "LÖKAP ve 18 laboratuvarı araştırmaya giriş yolları olarak anlat.",
            "Robotik Laboratuvarı'nın yayın, atıf, bitirme tezi ve lisans öğrenci sayılarını somut örnek olarak kullanabilirsin.",
            "Her öğrencinin otomatik kabul edileceğini söyleme; ilgili hocayla iletişim ve uygun proje gerekir.",
        ],
    ),

    "itu_specialization": DefenseArgument(
        id="itu_specialization",
        label="Uzmanlaşma ve güncel seçmeliler",
        technique="choice_architecture + concrete_evidence",
        trigger_hint="Aday AI, güvenlik, robotik, oyun, sistem veya seçmeli ders yolunu soruyor",
        talking_points=[
            "Adayın alanını zorunlu ders, güncel seçmeli ve laboratuvar üçlüsüyle eşleştir.",
            "Örneğin güvenlikte Bilgisayar Güvenliği/Güvenli Programlama/Ağ Güvenliği; AI'da Veriden Öğrenme/Yapay Zekâ/AI Accelerators Lab kullan.",
            "Seçmeli havuzundaki her dersin her dönem açılmayabileceğini belirt.",
        ],
    ),

    "itu_double_major_transfer": DefenseArgument(
        id="itu_double_major_transfer",
        label="ÇAP, yandal ve yatay geçiş koşulları",
        technique="uncertainty_reduction + concrete_evidence",
        trigger_hint="Aday çift anadal, yandal veya bölüm değiştirmeyi soruyor",
        talking_points=[
            "ÇAP için 3,00 GNO, üst %20 ve 3.-5. yarıyıl penceresini; yandal için 2,50 eşiğini anlat.",
            "Belirli iki program arasında o yıl kontenjan olduğunu güncel tablo olmadan garanti etme.",
            "Bilgisayar'ın geniş temelini korurken ikinci alan ekleme seçeneği olarak çerçevele.",
        ],
    ),

    "itu_erasmus_mobility": DefenseArgument(
        id="itu_erasmus_mobility",
        label="Erasmus öğrenim ve staj hareketliliği",
        technique="future_self + concrete_evidence",
        trigger_hint="Aday Erasmus koşulları, ülke, üniversite veya yurt dışı staj soruyor",
        talking_points=[
            "Öğrenim hareketliliğinde 2,50 GNO ve %50 akademik+%50 dil puanını kullan.",
            "Staj hareketliliğinde 60 gün, B1/65 ve ilk sınıf zamanlamasını ayır.",
            "Üniversite/ülke anlaşmalarını güncel çağrıya bağlı göster; eski örneği güncel garanti gibi sunma.",
        ],
    ),

    "itu_clubs_teams": DefenseArgument(
        id="itu_clubs_teams",
        label="Bölüm kulüpleri, takımlar ve sosyal çevre",
        technique="social_proof + experiential_evidence",
        trigger_hint="Aday kulüp, takım, arkadaş ortamı, hackathon veya bölümün sosyal profilini soruyor",
        talking_points=[
            "5 bölüm kulübü ve 3 takım içinden adayın ilgisine uyan adlandırılmış örnekler ver.",
            "Resmî kişilik/rekabet oranı olmadığını dürüstçe söyle; sosyal uyumu kulüp, takım ve lab temas kanallarıyla somutlaştır.",
            "Katılım ve etkinlik takvimini güncel kulüp duyurusuna bağlı göster.",
        ],
    ),

    "itu_housing_details": DefenseArgument(
        id="itu_housing_details",
        label="Yurt kapasitesi ve güncel ücretler",
        technique="risk_reduction + concrete_evidence",
        trigger_hint="Aday yurt ücreti, oda tipi, kapasite, başvuru veya barınma maliyeti soruyor",
        talking_points=[
            "5.300 yatak ve 2025-26 ücret aralığını, mümkünse adlandırılmış oda örneğiyle söyle.",
            "Yurt çıkmasını garanti etme; başvuru ve yerleştirme sonucunun ayrı olduğunu belirt.",
            "Maddi kaygı varsa ihtiyaç/burs/yemek desteklerini yurt ücretinden ayrı yollar olarak göster.",
        ],
    ),

    "itu_istanbul_life": DefenseArgument(
        id="itu_istanbul_life",
        label="İstanbul ve ulaşım dengesi",
        technique="tradeoff_framing + concrete_evidence",
        trigger_hint="Aday İstanbul maliyeti, trafik, ulaşım veya şehir yaşamını soruyor",
        talking_points=[
            "İstanbul'un maliyet ve yoğunluk dezavantajını saklama.",
            "Ayazağa'nın M2 ile Levent, Şişli-Mecidiyeköy ve Taksim bağlantısını somut avantaj olarak anlat.",
            "Şehir erişimini ARI Teknokent, etkinlik ve staj ağıyla adayın kariyer hedefine bağla; kesin yolculuk süresi verme.",
        ],
    ),

    "itu_student_wellbeing": DefenseArgument(
        id="itu_student_wellbeing",
        label="Uyum, yalnızlık ve psikolojik destek",
        technique="validation + support_evidence",
        trigger_hint="Aday yalnızlık, uyum, stres, kaygı veya pişmanlık korkusu dile getiriyor",
        talking_points=[
            "Önce duyguyu kısa ve doğal biçimde kabul et; satış cümlesiyle üstünü örtme.",
            "Ücretsiz PDR, Ayazağa hizmeti ve 2025'teki 934 başvuru verisini destek kanıtı olarak kullan.",
            "Kulüp/takım/danışman yollarını sosyal temas seçenekleri olarak ekle; herkesin aynı deneyimi yaşayacağını garanti etme.",
        ],
    ),

    "itu_graduation_requirements": DefenseArgument(
        id="itu_graduation_requirements",
        label="Mezuniyet, tasarım projesi ve süre",
        technique="direct_answer + expectation_setting",
        trigger_hint="Aday mezuniyet şartı, kredi, bitirme projesi, erken mezuniyet veya okul uzamasını soruyor",
        talking_points=[
            "240 AKTS, 130 yerel kredi, en az 2,00 GNO, zorunlu stajlar ve Tasarım I-II şartlarını ayır.",
            "Azami sürenin 7 yıl olduğunu söyle; tipik mezuniyet süresi veya uzatma oranı uydurma.",
            "Yaz okulunun hızlandırabileceğini fakat ders açılışı ve onaya bağlı olduğunu dürüstçe belirt.",
        ],
    ),

    "itu_student_life_support": DefenseArgument(
        id="itu_student_life_support",
        label="Burs, yurt ve öğrenci yaşamı",
        technique="practical_value + concrete_evidence",
        trigger_hint="Aday burs, yurt, maliyet, kampüs veya yemekhane soruyor",
        talking_points=[
            "Adayın sorduğu pratik ihtiyaca doğrudan, kaynaklı cevap ver.",
            "Garanti dili kullanma; yıl ve koşul varsa belirt.",
            "İTÜ Bilgisayar tercihini sürdürülebilir kılan maliyet ve kampüs avantajını adayın ihtiyacına bağla.",
        ],
    ),

    "itu_campus_life": DefenseArgument(
        id="itu_campus_life",
        label="Ayazağa kampüsü ve sosyal imkanlar",
        technique="experiential_evidence + concrete_evidence",
        trigger_hint="Aday Bilgisayar'ın kampüsünü, kampüsteki sosyal alanları veya spor imkanlarını soruyor",
        talking_points=[
            "Bilgisayar Mühendisliği'nin Ayazağa Kampüsü'nde olduğunu ilk cümlede söyle.",
            "RAG'dan en az bir kampüs ölçüsü ve 2 somut mekan/tesis örneği kullan.",
            "Kampüs imkanını İTÜ Bilgisayar öğrencisinin günlük yaşamına bağla; doğrulanmamış mekan veya beğeni uydurma.",
        ],
    ),

    "itu_dining": DefenseArgument(
        id="itu_dining",
        label="Yemekhane ücreti ve yemek seçenekleri",
        technique="practical_value + concrete_evidence",
        trigger_hint="Aday yemek ücretini, yemekhaneyi, öğünleri veya yemek seçeneklerini soruyor",
        talking_points=[
            "Güncel resmi öğrenci ücretini tarihiyle birlikte söyle.",
            "Dört kaplık menü yapısından vejetaryen seçenek veya gerçek yemek kategorileriyle örnek ver.",
            "Lezzet gibi öznel bir iddiayı resmi veriymiş gibi sunma; yemek bursu uygunsa ayrıca belirt.",
        ],
    ),

    "itu_career_evidence": DefenseArgument(
        id="itu_career_evidence",
        label="Mezuniyet öncesi iş ve şirket bağlantıları",
        technique="social_proof + concrete_evidence",
        trigger_hint="Aday mezun olmadan iş, staj, işe başlama veya Kariyer Zirvesi şirketlerini soruyor",
        talking_points=[
            "İşe başlama verisini yılı/kaynak bağlamıyla söyle; bireysel iş garantisi verme.",
            "Kariyer Zirvesi'nden güncel ve kaynaklı şirket örnekleri ekle.",
            "Bu erişimi İTÜ Bilgisayar öğrencisinin staj, görüşme ve portfolyo geliştirme fırsatına bağla.",
        ],
    ),

    "itu_english_prep": DefenseArgument(
        id="itu_english_prep",
        label="İngilizce hazırlık ve yeterlik yolu",
        technique="uncertainty_reduction + concrete_evidence",
        trigger_hint="Aday hazırlığın zorunluluğunu, atlama/yeterlik sınavını veya İngilizce muafiyetini soruyor",
        talking_points=[
            "Hazırlığın yeterlik/muafiyet sağlayamayan öğrenci için zorunlu olduğunu açık söyle.",
            "İngilizcesini yeterli gören adayın İTÜ Yeterlik Sınavı ya da kabul edilen eşdeğer sınavlarla bölüme doğrudan başlayabileceğini anlat.",
            "Sınav aşaması veya süre vereceksen yalnızca RAG'daki güncel resmi koşulları kullan.",
        ],
    ),

    "itu_compe_differentiators": DefenseArgument(
        id="itu_compe_differentiators",
        label="İTÜ Bilgisayar'ın ölçülebilir farkı",
        technique="authority + differentiation + concrete_evidence",
        trigger_hint="Aday İTÜ'yü seçince ne kazanacağını veya İTÜ Bilgisayar'ı eşsiz yapan ayrıntıyı soruyor",
        talking_points=[
            "Genel sıfat kullanma; en az bir sıralama/akreditasyon verisi ve bir adlandırılmış örnek ver.",
            "Bilgisayar Mühendisliği vurgusunu koru: ABET, akademik kadro, araştırma ve Maslak kariyer ekosistemini adayın hedefine bağla.",
            "Yapay zeka örneğinde resmi araştırma alanıyla birlikte Burak Berk Üstündağ'ı kullanabilirsin; iletişime açıklığını yalnızca öğrenci geri bildirimi olarak çerçevele.",
        ],
    ),

    "itu_financial_support": DefenseArgument(
        id="itu_financial_support",
        label="Burs ve maddi kaygı desteği",
        technique="risk_reduction + concrete_evidence",
        trigger_hint="Aday burs tutarı, geçim, masraf veya ailesinin karşılayamaması konusunda kaygılı",
        talking_points=[
            "Kaygıyı önce kabul et; ardından adayın sıralamasına uyan 2025 burs dilimini rakam ve koşullarıyla söyle.",
            "Sıralama bilinmiyorsa başarı bursunu garanti etme; ilk tercih, ihtiyaç ve yemek bursu yollarını ayır.",
            "Tutarla birlikte ilk tercih, GNO 2,50 ve hazırlık koşullarından ilgili olanı kısa biçimde belirt.",
            "Maddi sürdürülebilirliği İTÜ Bilgisayar tercihini gerçekçi kılan bir unsur olarak çerçevele.",
        ],
    ),

    "itu_entrepreneurship_ecosystem": DefenseArgument(
        id="itu_entrepreneurship_ecosystem",
        label="İTÜ Çekirdek girişimcilik verileri",
        technique="social_proof + concrete_evidence",
        trigger_hint="Aday startup, şirket kurma, yatırım veya İTÜ Çekirdek soruyor",
        talking_points=[
            "Resmi İTÜ Çekirdek kaynağından en fazla iki tarihli ve somut ekosistem verisi kullan.",
            "Yazılım girişimi ilgisini İTÜ Bilgisayar'da teknik ürün geliştirme temeliyle ilişkilendir.",
            "Ekosistem toplamını adaya kişisel yatırım, kabul veya şirket başarısı garantisi gibi sunma.",
            "Sıralamasına uygun başarı ödülünde Teknopark önceliği varsa koşuluyla birlikte söyle.",
        ],
    ),

    "itu_global_opportunities": DefenseArgument(
        id="itu_global_opportunities",
        label="Yurt dışı ve uluslararası yol",
        technique="future_self + concrete_evidence",
        trigger_hint="Aday Erasmus, çift diploma, yurt dışı eğitim veya kariyer soruyor",
        talking_points=[
            "Kaynakta bulunan uluslararası imkanları adayın hedefine bağla.",
            "Kabul veya iş garantisi verme; program ile sonucu birbirinden ayır.",
            "İTÜ Bilgisayar'ın İngilizce/akademik temelini yurt dışı hedefi açısından çerçevele.",
        ],
    ),

    "itu_clubs_projects": DefenseArgument(
        id="itu_clubs_projects",
        label="Kulüp, takım ve proje deneyimi",
        technique="experiential_evidence + future_self",
        trigger_hint="Aday kulüp, takım, oyun, robotik veya proje deneyimi soruyor",
        talking_points=[
            "Yalnızca RAG'da bulunan kulüp/takım/proje örneklerini kullan.",
            "Katılım koşulu bilinmiyorsa herkese açıkmış gibi garanti verme.",
            "Öğrencinin ilgisini İTÜ Bilgisayar'da portfolyo ve ekip deneyimine dönüştürebileceğini göster.",
        ],
    ),

    "itu_worship_facilities": DefenseArgument(
        id="itu_worship_facilities",
        label="Kampüste ibadet imkânları",
        technique="direct_information + inclusion",
        trigger_hint="Aday cami, mescit, namaz veya ibadet imkânını açıkça soruyor",
        talking_points=[
            "Bu başlığı yalnız aday açıkça sorduğunda yanıtla; isim, görünüş veya konuşma biçiminden inanç çıkarımı yapma.",
            "RAG'deki resmî kampüs haritasında bulunan camiyi ve öğrenci geri bildirimindeki fakülte mescidini kaynak türlerini ayırarak söyle.",
            "Sınavda ibadet izni veya Ramazan uygulaması gibi RAG'de doğrulanmayan bir kural uydurma.",
        ],
    ),

    "itu_social_venues": DefenseArgument(
        id="itu_social_venues",
        label="Ayazağa'da sosyal mekânlar ve günlük yaşam",
        technique="experiential_evidence + direct_information",
        trigger_hint="Aday sinema, maç izleme, kafe, pizza, market veya kampüste buluşma noktası soruyor",
        talking_points=[
            "Sorulan ihtiyaca doğrudan RAG'deki adlandırılmış mekân veya etkinlik örnekleriyle cevap ver.",
            "Resmî kampüs listesindeki mekânlarla öğrenci geri bildirimindeki dönemsel deneyimleri birbirinden ayır.",
            "Geçmiş bir Dünya Kupası etkinliğini sürekli veya her dönem garanti edilen program gibi anlatma.",
        ],
    ),

    "itu_admission_reality": DefenseArgument(
        id="itu_admission_reality",
        label="Sıralama ve tercih gerçekliği",
        technique="honesty + evidence",
        trigger_hint="Aday taban sırası, puan, girme ihtimali veya başka bölüm sırası soruyor",
        talking_points=[
            "Sorulan bölümün kaynaklı taban sırasını ve yılı açıkça söyle.",
            "Aday geçen yılın tabanının gerisindeyse bunu açıkça '2025 tabanına göre geride' diye söyle; yalnız gelecek yıl için kesin sonuç verme.",
            "İTÜ Bilgisayar gerçekçi değilse, sıralamaya uyan İTÜ bölümünü yalnız kaynaklı 2025 tabanlarıyla alternatif olarak göster.",
        ],
    ),

    # === İtiraz/kaygı yönetimi ===
    "concern_math_difficulty": DefenseArgument(
        id="concern_math_difficulty",
        label="Matematik/zorluk kaygısı",
        technique="validation + reframing",
        trigger_hint="Aday 'matematikte kötüyüm' veya 'zor değil mi' diyor",
        talking_points=[
            "ÖNCE kabul et: 'Kaygın anlaşılır, İTÜ zorlayıcı bir okul.'",
            "Sonra destek mekanizmalarını anlat: mentörlük, ders çalışma grupları, tekrar dersi hakkı.",
            "Öğrenci memnuniyeti yüksek — zorluk yıldırıcı değil, yönlendirici.",
            "Motivational Interviewing: adayın kendi motivasyonunu hatırlat.",
        ],
    ),

    "concern_family_pressure": DefenseArgument(
        id="concern_family_pressure",
        label="Aile baskısı",
        technique="validation + data",
        trigger_hint="Aday 'ailem başka istiyor' veya benzeri baskı belirtiyor",
        talking_points=[
            "Kabul et: 'Aile baskısı zor bir konu, birçok aday yaşıyor.'",
            "Aileye yönelik somut veri sun: TÜİK bilişim istihdamı, İTÜ mezun yolu, ABET, Çekirdek girişimleri.",
            "Nihai karar adaya ait — bunu son bir kez vurgula.",
        ],
    ),

    "balanced_perspective": DefenseArgument(
        id="balanced_perspective",
        label="Dengeli perspektif",
        technique="framing (honest)",
        trigger_hint="Karşılaştırma sorusu geldi veya aday şüpheci",
        talking_points=[
            "İTÜ her metrikte 1. değil — QS genelde ODTÜ önde (269 < 298); dürüstçe söyle.",
            "Sonra İTÜ'nün önde olduğu boyutlara geç: QS Mühendislik&Teknoloji 91, ABET, İstanbul, Çekirdek.",
            "Kimseyi kötüleme — 'ODTÜ de çok güçlü, farklı odaklarla' de.",
            "Adayın daha önce söylediği öncelik varsa karşılaştırmayı ona bağla; yoksa iki ölçütü kısa ve somut biçimde sun, otomatik kapanış sorusu sorma.",
        ],
    ),

    "software_vs_compe": DefenseArgument(
        id="software_vs_compe",
        label="Yazılım Müh. ↔ Bilgisayar Müh. farkı",
        technique="framing + authority",
        trigger_hint="Aday yazılım mühendisliği ile bilgisayar mühendisliği arasındaki farkı soruyor veya yazılım bölümü arıyor",
        talking_points=[
            "İTÜ'de ayrı bir Yazılım Müh. lisansı YOK — yazılım eğitimi Bilgisayar Müh. çekirdeğinin içinde (Software Engineering dersi + yazılım seçmelileri).",
            "Kavramsal fark: Yazılım Müh. geliştirme yaşam döngüsüne odaklanır; Bilgisayar Müh. buna donanım, mimari, OS, ağ ve teoriyi ekleyen geniş temel verir.",
            "Sektörde iki bölümün mezunu da 'yazılım mühendisi' olarak çalışır — işe alımda beceri/portfolyo bölüm adından önemlidir.",
            "Geniş temel isteyen adaya Bilgisayar'ın esnekliğini göster; dar-odak yazılım isteyen adaya da dürüst ol.",
        ],
    ),

    "university_comparison_general": DefenseArgument(
        id="university_comparison_general",
        label="Üniversite karşılaştırma (Boğaziçi/Sabancı/YTÜ)",
        technique="framing (honest) + authority",
        trigger_hint="Aday Koç dışında bir üniversiteyle (Boğaziçi, Sabancı, YTÜ, Bilkent...) kıyaslama istiyor",
        talking_points=[
            "İTÜ'NÜN GÜÇLÜ KARTLARIYLA BAŞLA: kaynaklı QS Mühendislik&Teknoloji verisi; 37 öğretim üyesi + 10 tam zamanlı öğretim görevlisi + 18 laboratuvar; ABET + %100 İngilizce + devlet/ücretsiz; Çekirdek + ARI Teknokent + Kariyer Zirvesi.",
            "MÜFREDAT YAPISI FARKLARINI ('İTÜ donanım-sistem ağırlıklı') ANA ARGÜMAN YAPMA — bu bir satış kartı değil, nötr bir nüanstır. Yalnızca aday özellikle donanım/gömülü/robotik meraklısıysa avantaj olarak kullan.",
            "Kötüleme YOK — karşı okulun gerçek güçlü yanını tek cümleyle kabul et (Boğaziçi kampüs kültürü, Sabancı esnek programı, YTÜ erişilebilirliği), sonra İTÜ kartlarına dön.",
            "Adayın KISITLARINA bağla: maliyet → devlet/ücretsiz; İngilizce → %100 İng+ABET; sektör → Maslak/Teknokent.",
            "Sayı vereceksen yalnızca kaynaklı olanları kullan; Sabancı gibi elimizde sayı olmayanlarda 'güncel kaynaktan teyit edelim' de.",
            "Kararı adaya bırak; bunu klişe bir kapanış sorusuyla her turda tekrar etme.",
        ],
    ),

    "future_of_compe": DefenseArgument(
        id="future_of_compe",
        label="Bilgisayar Müh. geleceği & yapay zekâ",
        technique="reframing + authority",
        trigger_hint="Aday 'AI gelişti, bilgisayar mühendisliği ölür mü / işimizi alır mı' tipi gelecek kaygısı taşıyor",
        talking_points=[
            "Önce kaygıyı KABUL et — bu çağın en meşru sorusu, geçiştirme.",
            "Çerçeveyi düzelt: AI, bilgisayar mühendisliğinin alt alanı; AI sistemlerini kuran/ölçekleyen/güvenli kılan mühendislerin temeli CompE.",
            "Veri: ABD BLS 2023-2033 yazılım istihdamında %17,9 büyüme öngörüyor — AI araçları yaygınlaşırken yayımlanmış projeksiyon.",
            "Dengeli ol: rutin kodlama otomatikleşiyor, sistem tasarımı/güvenlik/AI kurma becerisi değerleniyor. Kesin gelecek tahmini KİMSE veremez — bunu dürüstçe söyle, garanti verme.",
        ],
    ),

    # === Kapanış ===
    "ideal_match_summary": DefenseArgument(
        id="ideal_match_summary",
        label="İdeal Tercih Özeti",
        technique="commitment + summary",
        trigger_hint="Konuşma sonuna yaklaşıldı, profil netleşti, özet zamanı",
        talking_points=[
            "Adayın söylediklerini 2-3 cümleyle özetle: 'Anladığım — ...'",
            "Profilindeki motivasyonları İTÜ Bilgisayar ile eşleştiren en güçlü 2 sebebi söyle.",
            "'Karar sana ait; sana yardımcı olabildiysem sevindim' ile bitir.",
            "Sonraki adım öner: broşür, bölüm web sitesi, öğrenci kulüpleri iletişimi.",
        ],
    ),
}


def get_argument(argument_id: str) -> DefenseArgument | None:
    return ARGUMENTS.get(argument_id)


def all_argument_ids() -> list[str]:
    return list(ARGUMENTS.keys())
