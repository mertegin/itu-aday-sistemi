"""10 UZUN senaryo (10'ar kullanıcı mesajı) — uzun konuşma dinamiği testi.

Neyi test eder:
- FSM'in uzun akışta davranışı (turn 12 kapanış zorlaması dahil)
- Argüman çeşitliliği / tekrar blokajı uzun vadede
- Profil birikimi + provenance güven artışı
- Engagement dinamiği (sessiz aday, açılan aday)
- Robustness (konu değiştiren kaotik aday)

Kullanım (backend çalışırken):
    .venv\\Scripts\\python.exe run_long_scenarios.py
Çıktı: long_scenario_report.md
"""
from run_scenarios import new_session, post_chat, profile_brief
import time

LONG_SCENARIOS = [
    {
        "id": "L01_tip_derin_kararsizlik",
        "title": "Tıp hayali + aile doktoru — 10 turn derin kararsızlık",
        "messages": [
            "Merhaba, ben Elif",
            "Sıralamam 950 geldi bu sene",
            "Aslında çok kararsızım. Babam doktor, hep tıp okuyacağım sanıyordum ama son iki yıldır bilgisayarla uğraşıyorum ve çok seviyorum",
            "Python öğrendim kendi kendime, küçük bir oyun bile yaptım",
            "Ama babama nasıl söylerim bilmiyorum, o hep tıp der",
            "Tıpta da insanlara yardım etmek var ama, onu bırakmak istemiyorum sanki",
            "Sağlık teknolojisi dediniz de, orada gerçekten iş var mı? Yoksa hayal mi",
            "Peki İTÜ'de sağlıkla ilgili çalışan hocalar ya da laboratuvarlar var mı",
            "Bunları babama da anlatsam ikna olur mu sizce, ne desem",
            "Tamam, teşekkür ederim, sanırım biraz daha düşüneceğim ama artık daha net görüyorum",
        ],
    },
    {
        "id": "L02_koc_pazarlikci",
        "title": "Koç tam burs teklifi — maddi analizci, 10 turn kıyaslama",
        "messages": [
            "Selam, ben Arda",
            "750 sıralamam var, Koç'tan tam burs geldi, İTÜ ile karşılaştırıyorum",
            "Koç'ta burs + yurt + yemek hepsi dahil diyorlar, İTÜ'de ne var somut olarak",
            "İlk 1000 bursu dediniz, tam olarak neyi kapsıyor? Aylık para var mı",
            "Peki mezun olunca fark ediyor mu, Koç mezunu mu İTÜ mezunu mu daha kolay iş buluyor",
            "Yazılım sektöründe çalışmak istiyorum, belki kendi işimi de kurarım",
            "Çekirdek'ten bahsettiniz, oraya öğrenciyken mi giriliyor, nasıl çalışıyor",
            "Koç'un da girişimcilik merkezi var ama, fark ne",
            "Dürüst olun, siz İTÜ'nün robotusunuz tabii İTÜ diyeceksiniz, objektif olabilir misiniz",
            "Mantıklı cevap, tamam. İkisini de listeme yazacağım ama İTÜ öne geçti sanırım",
        ],
    },
    {
        "id": "L03_matematik_ozguven_krizi",
        "title": "Derin özgüven sorunu — sürekli endişe, cesaretlendirme testi",
        "messages": [
            "merhaba",
            "1350 sıralamam var ama açıkçası buraya gelmemin sebebi korkularım",
            "İTÜ bilgisayar istiyorum ama herkes çok zor diyor, kalanlar oluyormuş",
            "ben lisede matematikte hep ortalamaydım, buranın matematiği ağır değil mi",
            "ya girerim de yapamazsam? bir yıl kaybederim, ailem de üzülür",
            "hazırlık var bir de değil mi, İngilizcem de orta seviye",
            "destek dediniz ama gerçekçi olalım, hocalar birebir ilgilenir mi yüzlerce öğrenciyle",
            "üst sınıflardan yardım alınıyor mu peki, mentor gibi",
            "biraz rahatladım açıkçası, demek ki kalan herkes atılmıyor",
            "tamam, deneyeceğim o zaman. teşekkürler, iyi geldi bu konuşma",
        ],
    },
    {
        "id": "L04_yz_compe_mufredat_detayci",
        "title": "YZ-Veri vs CompE — müfredat düzeyinde detaycı sorular",
        "messages": [
            "Merhaba ben Deniz, 1600 sıralamam var",
            "Yapay Zeka ve Veri Mühendisliği ile Bilgisayar Mühendisliği arasında kaldım, makine öğrenmesi alanında kariyer istiyorum",
            "İkisinin müfredatı somut olarak nasıl farklı? Ders isimleriyle anlatır mısınız",
            "Bilgisayarda AI dersi kaçıncı sınıfta geliyor",
            "YZ bölümü daha yeni değil mi, mezunu bile yok, riskli olmaz mı",
            "Bilgisayardan yapay zekaya yüksek lisansla geçilir mi, yoksa YZ lisansı mı şart",
            "Çift anadal yapılabiliyor mu ikisi arasında, şartları neler",
            "Donanım dersleri beni biraz korkutuyor açıkçası, bilgisayarda çok mu donanım var",
            "Sıralamam 1600 dedim, bilgisayara girme şansım gerçekçi olarak ne",
            "Anladım, o zaman YZ-Veri birinci tercihe, Bilgisayar da üstüne yazarım, mantıklı mı",
        ],
    },
    {
        "id": "L05_sessiz_acilan_aday",
        "title": "Sessiz başlayan aday — kısa cevaplar, yavaş açılma (engagement testi)",
        "messages": [
            "mrb",
            "bilmiyorum",
            "annem getirdi buraya, gezelim dedi",
            "1900 falan",
            "bilgisayar oyunları oynuyorum çok, o sayılır mı",
            "valorant, cs, bazen kendi haritalarımı yapıyorum workshopta",
            "harita yapmak kodlamak gibi mi yani? onu bilmiyordum",
            "oyun yapan bölüm var mı peki burada",
            "bu dediğiniz kulüp herkese açık mı, birinci sınıf da girebiliyor mu",
            "iyiymiş ya, ilk defa üniversite ilgimi çekti, teşekkürler",
        ],
    },
    {
        "id": "L06_supheci_agresif",
        "title": "Şüpheci aday — 'İTÜ abartılıyor', zorlayıcı itirazlar (etik sınır testi)",
        "messages": [
            "selam, 1050 sıram var",
            "açık konuşayım, İTÜ bence abartılıyor. herkes İTÜ İTÜ diyor ama ODTÜ sıralamada önünüzde",
            "bak QS'te bile ODTÜ daha yukarıda, niye İTÜ seçeyim ki",
            "mühendislikte iyisiniz tamam ama bilgisayarda ODTÜ tabanı sizden yüksek, demek ki daha kaliteli",
            "hocalarınız da eski kafalı diyorlar, dersler hep teorik mi",
            "kampüs de İstanbul'un ortasında, trafik rezalet, Ankara daha sakin",
            "peki size zor bir soru: İTÜ'nün ODTÜ'den net kötü olduğu bir şey söyleyin, dürüstseniz söylersiniz",
            "hmm, dürüst cevap verdiniz beklemiyordum",
            "yurt meselesi bende önemli, Ankara'da ailem var ama İstanbul'da kimsem yok, yurt garantili mi",
            "tamam objektif konuştunuz, saygı duydum. iki okulu da gezeceğim, sağolun",
        ],
    },
    {
        "id": "L07_girisimci_vizyoner",
        "title": "Girişimci vizyoner — startup hayali, ekosistem soruları",
        "messages": [
            "Merhaba! Ben Emre, 680 sıralamam var",
            "Benim net bir hayalim var: kendi teknoloji şirketimi kuracağım. Üniversite bunun için bir araç benim için",
            "Lisede bir arkadaşımla mobil uygulama yaptık, 10 bin indirme aldı",
            "O yüzden soruyorum: İTÜ bana girişimcilik için somut ne verir?",
            "Çekirdek'e öğrenciyken başvurabilir miyim, yoksa mezun mu olmak lazım",
            "Yatırımcılarla nasıl tanışılıyor, demo day gibi şeyler var mı",
            "Peki okul yoğunluğu girişime zaman bırakır mı, ders yükü nasıl",
            "Bilgisayar mı okusam endüstri mi? Girişimci için hangisi daha mantıklı",
            "Yurt dışına açılmak istersem, İTÜ'nün ağı orada da işe yarar mı",
            "Süper, ben zaten İTÜ diyordum, şimdi emin oldum. Görüşürüz!",
        ],
    },
    {
        "id": "L08_aile_catismasi_derin",
        "title": "Aile çatışması — babası İnşaat istiyor, kendisi Bilgisayar",
        "messages": [
            "merhaba, ben Zehra",
            "1250 sıralamam var ama benim sorunum sıralama değil, ailem",
            "babam inşaat mühendisi, illa inşaat oku diyor, kendi şirketi var, hazır iş diyor",
            "ama ben bilgisayar istiyorum, kod yazmayı seviyorum, inşaat hiç ilgimi çekmiyor",
            "babam 'bilgisayarcılar işsiz kalıyor, yapay zeka hepsinin işini alacak' diyor, doğru mu",
            "bak bu istatistikleri babama göstersem işe yarar mı",
            "bir de 'kız çocuğu şantiyede ne yapar, ofiste otur' diyor, bilgisayarda kadınlar nasıl, ayrımcılık var mı",
            "İTÜ'de kadın mühendis oranı nedir bilgisayarda",
            "hazır şirket konusuna ne derim peki, 'benim işim hazır' diyor babam",
            "çok teşekkür ederim, bu konuşmayı babama kaydetseymişim keşke. broşür var mı alabileceğim",
        ],
    },
    {
        "id": "L09_donanim_robotik_tutkunu",
        "title": "Donanım/robotik tutkunu — elektronik-bilgisayar kesişimi, kulüp detayları",
        "messages": [
            "Selam ben Burak, 2800 sıralamam var",
            "Ben tam bir donanımcıyım, arduino, raspberry pi, 3d printer, evde mini lab kurdum",
            "Robot yapıyorum, line follower ile yarışmaya bile katıldım, bölge ikincisi olduk",
            "Elektronik mi bilgisayar mı karar veremiyorum, ikisini de seviyorum",
            "2800 ile bilgisayar zor herhalde değil mi, dürüst söyleyin",
            "Elektronik-Haberleşme tabanı ne, ona yeter mi sıralamam",
            "İTÜ'de robotik takımlar varmış, AnthRo mu ne, oraya elektronikçiler de giriyor mu",
            "Gömülü sistemler hangi bölümde daha güçlü, ben o alana gitmek istiyorum aslında",
            "Çift anadal şansım olur mu elektronikten bilgisayara, ortalama şartı var mı",
            "Tamam hocam çok net oldu: elektronik yazacağım, gömülüye yöneleceğim, çift anadalı da deneyeceğim",
        ],
    },
    {
        "id": "L10_kaotik_konu_degistiren",
        "title": "Kaotik aday — sürekli konu değiştiriyor (robustness testi)",
        "messages": [
            "selaaam",
            "ya ben aslında tıp istiyordum ama vazgeçtim galiba, 1150 sıram var bu arada",
            "oyun yapmak da istiyorum ama, unity öğreniyorum",
            "bir de kripto ile ilgileniyorum, blockchain dersi var mı sizde",
            "yok ya aslında en çok parayı nerede kazanırım onu söyleyin",
            "yurt dışına gitsem mi ki direkt, Almanya'da okusam",
            "neyse İTÜ'de kalalım, yemekhane nasıl, yurtlar nasıl",
            "şaka şaka, ciddi soru: bilgisayar mı yazayım yapay zeka mı, 1150 ile ikisi de olur mu",
            "hmm mantıklı, peki oyun kulübü de var dediniz, hem AI hem oyun yapabilir miyim orada",
            "tamam abi süpersin, bilgisayar birinci tercih, görüşürüz",
        ],
    },
]


def run_scenario_long(sc):
    sid = new_session()
    turns = []
    result = None
    for msg in sc["messages"]:
        t0 = time.time()
        result = post_chat(sid, msg)
        elapsed = time.time() - t0
        turns.append({
            "user": msg,
            "bot": result["response_text"],
            "fsm": f'{result["xai_meta"]["fsm_from"]} -> {result["xai_meta"]["fsm_to"]}',
            "trigger": result["xai_meta"]["fsm_trigger"],
            "argument": result["xai_meta"]["argument_id"],
            "user_type": result["xai_meta"]["user_type"],
            "reward_prev": result.get("reward_previous_turn"),
            "elapsed": round(elapsed, 1),
        })
        print(f"    turn {len(turns):2d}: {turns[-1]['fsm']:60s} | {turns[-1]['argument']}")
    return {"session_id": sid, "turns": turns, "final_profile": result["profile"],
            "academic": result.get("academic", {})}


def main():
    print(f"{len(LONG_SCENARIOS)} uzun senaryo (10'ar mesaj) çalıştırılıyor...\n")
    results = []
    for i, sc in enumerate(LONG_SCENARIOS, 1):
        print(f"[{i}/{len(LONG_SCENARIOS)}] {sc['id']}: {sc['title']}")
        try:
            r = run_scenario_long(sc)
            results.append({"scenario": sc, "result": r, "error": None})
        except Exception as e:
            print(f"    HATA: {e}")
            results.append({"scenario": sc, "result": None, "error": str(e)})
        print()

    lines = ["# Uzun Senaryo Test Raporu (10 mesajlık konuşmalar)", ""]
    ok_count = sum(1 for r in results if not r["error"])
    lines.append(f"Toplam: {len(LONG_SCENARIOS)} senaryo | Başarılı koşu: {ok_count}")
    lines.append("")

    for r in results:
        sc = r["scenario"]
        lines.append(f"## {sc['id']} — {sc['title']}")
        lines.append("")
        if r["error"]:
            lines.append(f"**HATA:** {r['error']}")
            lines.append("")
            continue
        res = r["result"]
        lines.append(f"Session: `{res['session_id']}`")
        lines.append("")
        for i, t in enumerate(res["turns"], 1):
            reward = f" · r={t['reward_prev']:.2f}" if t["reward_prev"] is not None else ""
            lines.append(f"**Turn {i}** — `{t['fsm']}` · arg: `{t['argument']}`{reward}")
            lines.append(f"- 🧑 {t['user']}")
            lines.append(f"- 🤖 {t['bot']}")
            lines.append("")
        lines.append(f"**Final profil:** {profile_brief(res['final_profile'])}")
        band = res.get("academic", {}).get("risk_band", "?")
        lines.append(f"**Risk bandı:** {band}")
        args_used = [t["argument"] for t in res["turns"]]
        lines.append(f"**Argüman çeşitliliği:** {len(set(args_used))} farklı / {len(args_used)} turn")
        prov = res["final_profile"].get("provenance", {})
        facts = [k for k, v in prov.items() if v.get("confidence", 0) >= 0.75]
        guesses = [k for k, v in prov.items() if v.get("confidence", 0) < 0.75]
        lines.append(f"**Kesin bilinenler ({len(facts)}):** {', '.join(facts[:12])}")
        if guesses:
            lines.append(f"**Tahminler ({len(guesses)}):** {', '.join(guesses[:8])}")
        lines.append("")
        lines.append("---")
        lines.append("")

    with open("long_scenario_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("Rapor yazıldı: long_scenario_report.md")


if __name__ == "__main__":
    main()
