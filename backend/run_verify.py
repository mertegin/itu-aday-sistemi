"""Fix doğrulama — 3 sorunlu senaryoyu tekrar koşar (S01/S05/S07 regresyonları)."""
from run_scenarios import SCENARIOS, run_scenario, profile_brief

TARGET_IDS = {"S01_top1000_yazilim", "S05_yz_vs_compe", "S07_para_motivasyonu"}


def main():
    targets = [s for s in SCENARIOS if s["id"] in TARGET_IDS]
    for sc in targets:
        print(f"=== {sc['id']}: {sc['title']} ===")
        r = run_scenario(sc)
        for i, t in enumerate(r["turns"], 1):
            print(f"  T{i} [{t['argument']}] {t['fsm']}")
            print(f"     Bot: {t['bot'][:180]}")
        print(f"  Profil: {profile_brief(r['final_profile'])}")
        print()


if __name__ == "__main__":
    main()
