"""10 farklı aday senaryosunu API üzerinden çalıştırır, markdown rapor üretir.

Kullanım (backend çalışırken):
    .venv\\Scripts\\python.exe run_scenarios.py
"""
import json
import sys
import time
import urllib.request

API = "http://127.0.0.1:8000/api"

SCENARIOS = [
    {
        "id": "S01_top1000_yazilim",
        "title": "Top-1000, yazılım/AI ilgili, girişimci ruhlu",
        "messages": [
            "Merhaba, ben Deniz",
            "Sıralamam 600 geldi",
            "Yazılım gelistirmeyi cok seviyorum, lisede oyun yaptım. Yapay zekaya da meraklıyım",
            "Kendi şirketimi kurmak istiyorum ileride",
        ],
    },
    {
        "id": "S02_tip_muhendislik",
        "title": "1200 sıra, tıp-mühendislik arasında kararsız",
        "messages": [
            "selam ben mert",
            "1200 falan bekliyorum",
            "aslında tıp da istiyorum, doktorluk hep hayalimdi ama bilgisayar da ilgimi çekiyor",
            "insanlara yardım etmek benim için önemli",
        ],
    },
    {
        "id": "S03_koc_alternatifi",
        "title": "800 sıra, Koç bursuyla İTÜ arasında",
        "messages": [
            "Merhaba, Zeynep ben",
            "800 civarı sıralamam var. Koç'tan tam burs teklifi aldım ama İTÜ'yü de düşünüyorum",
            "Maddi durum bizim için önemli açıkçası",
            "Peki mezun olduktan sonra iş bulma konusunda fark var mı?",
        ],
    },
    {
        "id": "S04_matematik_kaygisi",
        "title": "1400 sınırda + matematik özgüven eksikliği",
        "messages": [
            "merhaba",
            "1400 sıralamam var, İTÜ bilgisayar istiyorum ama açıkçası korkuyorum",
            "matematiğim çok iyi değil, kalırsam ne olur diye düşünüyorum",
            "peki destek var mı okulda zorlanırsam",
        ],
    },
    {
        "id": "S05_yz_vs_compe",
        "title": "1800 sıra, YZ-Veri Müh. ile Bilgisayar arasında",
        "messages": [
            "Selam, ben Ege",
            "Sıralamam 1800. Yapay zeka mühendisliği mi bilgisayar mühendisliği mi karar veremiyorum",
            "Hedefim machine learning engineer olmak",
            "İkisinin farkı tam olarak ne?",
        ],
    },
    {
        "id": "S06_elektronik_ilgisi",
        "title": "3000 sıra, donanım/elektronik meraklısı",
        "messages": [
            "Merhaba ben Can",
            "3000 sıralarındayım",
            "Elektronik devrelerle uğraşmayı seviyorum, arduino projeleri yapıyorum",
            "Robotik de ilgimi çekiyor açıkçası",
        ],
    },
    {
        "id": "S07_para_motivasyonu",
        "title": "900 sıra, öncelik yüksek maaş",
        "messages": [
            "selam",
            "900 sıram var. açık konuşayım benim için önemli olan para kazanmak",
            "hangi bölüm daha çok kazandırır? yazılımcılar gerçekten iyi kazanıyor mu",
            "yurt dışına gitmek de mantıklı mı maaş için",
        ],
    },
    {
        "id": "S08_bilim_akademi",
        "title": "700 sıra, akademisyen/araştırmacı olmak istiyor",
        "messages": [
            "Merhaba, ben Elif",
            "Sıralamam 700. Ben araştırmacı olmak istiyorum, akademide kalmayı düşünüyorum",
            "Yapay zeka üzerine doktora yapmak istiyorum, tercihen yurt dışında",
            "İTÜ'de araştırma imkanları nasıl?",
        ],
    },
    {
        "id": "S09_aile_baskisi",
        "title": "1100 sıra, ailesi başka üniversite istiyor",
        "messages": [
            "merhaba",
            "1100 sıralamam var, ben İTÜ bilgisayar istiyorum ama ailem ODTÜ istiyor illa",
            "babam ODTÜ mezunu, oranın daha iyi olduğunu söylüyor",
            "aileme nasıl anlatabilirim bilmiyorum",
        ],
    },
    {
        "id": "S10_kararsiz_siralamasiz",
        "title": "Sıralama belirsiz, tamamen kararsız aday",
        "messages": [
            "selam ya",
            "daha sonuçlar açıklanmadı, bilmiyorum kaç gelir",
            "denemelerde 1500-2500 arası geliyor genelde",
            "ne istediğimi de tam bilmiyorum açıkçası, herkes mühendislik diyor",
        ],
    },
]


def post_chat(session_id, text):
    payload = json.dumps({"session_id": session_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(
        f"{API}/chat",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def new_session():
    req = urllib.request.Request(f"{API}/session/new", data=b"", method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))["session_id"]


def run_scenario(sc):
    sid = new_session()
    turns = []
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
        print(f"    turn {len(turns)}: {turns[-1]['fsm']} | arg={turns[-1]['argument']} | {elapsed:.1f}s")
    final_profile = result["profile"]
    return {"session_id": sid, "turns": turns, "final_profile": final_profile}


def profile_brief(p):
    ind = p.get("indecision", {})
    bits = []
    if p.get("yks_rank"):
        bits.append(f"rank={p['yks_rank']}")
    mot = ind.get("motivation", {})
    if mot:
        top = max(mot.items(), key=lambda kv: kv[1])
        if top[1] >= 0.15:
            bits.append(f"motivasyon={top[0]}({top[1]:.2f})")
    for key, lbl in (("field_alternatives", "alan_alt"), ("university_alternatives", "univ_alt"), ("department_alternatives", "dept_alt")):
        if ind.get(key):
            bits.append(f"{lbl}={','.join(ind[key])}")
    ints = {k: v for k, v in p.get("interests", {}).items() if v > 0.15}
    if ints:
        bits.append("ilgi=" + ",".join(f"{k}({v:.1f})" for k, v in sorted(ints.items(), key=lambda kv: -kv[1])[:3]))
    if p.get("concerns"):
        bits.append("kaygi=" + ",".join(p["concerns"]))
    return " | ".join(bits) if bits else "(profil boş)"


def main():
    print(f"{len(SCENARIOS)} senaryo çalıştırılıyor...\n")
    results = []
    for i, sc in enumerate(SCENARIOS, 1):
        print(f"[{i}/{len(SCENARIOS)}] {sc['id']}: {sc['title']}")
        try:
            r = run_scenario(sc)
            results.append({"scenario": sc, "result": r, "error": None})
        except Exception as e:
            print(f"    HATA: {e}")
            results.append({"scenario": sc, "result": None, "error": str(e)})
        print()

    # Markdown rapor
    lines = ["# Senaryo Test Raporu", ""]
    lines.append(f"Toplam: {len(SCENARIOS)} senaryo | Başarılı: {sum(1 for r in results if not r['error'])}")
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
            lines.append(f"**Turn {i}** — `{t['fsm']}` · arg: `{t['argument']}` · user_type: `{t['user_type']}`" +
                         (f" · reward(önceki): {t['reward_prev']:.2f}" if t['reward_prev'] is not None else ""))
            lines.append(f"- 🧑 **Aday:** {t['user']}")
            lines.append(f"- 🤖 **Neco:** {t['bot']}")
            lines.append("")
        lines.append(f"**Final profil:** {profile_brief(res['final_profile'])}")
        lines.append("")
        fsm_path = " → ".join([res["turns"][0]["fsm"].split(" -> ")[0]] + [t["fsm"].split(" -> ")[1] for t in res["turns"]])
        lines.append(f"**FSM yolu:** {fsm_path}")
        lines.append("")
        lines.append("---")
        lines.append("")

    report = "\n".join(lines)
    out_path = "scenario_report.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Rapor yazıldı: {out_path}")


if __name__ == "__main__":
    main()
