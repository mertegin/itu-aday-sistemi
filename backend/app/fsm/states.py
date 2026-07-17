from enum import Enum


class FSMState(str, Enum):
    S0_FALLBACK = "S0_FALLBACK"                    # Anlaşılmayan input / hata
    S1_GREETING = "S1_GREETING"                    # Karşılama, güven kurma
    S2_INDECISION_PROBE = "S2_INDECISION_PROBE"    # Sıralama + ilgi + kararsızlık ölçümü
    S2R_PROFILE_UPDATE = "S2R_PROFILE_UPDATE"      # Yeni sinyal geldi, profil güncelle
    S3_ARGUMENT_SELECTION = "S3_ARGUMENT_SELECTION"  # Bandit argüman seçimi
    S4_ARGUMENT_DELIVERY = "S4_ARGUMENT_DELIVERY"  # Argümanı sun
    S5_RECEPTION_EVAL = "S5_RECEPTION_EVAL"        # Tepkiyi ölç
    S6_RAG_DEEP_DIVE = "S6_RAG_DEEP_DIVE"          # Somut detay/veri talebi
    S7_CONCERN_HANDLING = "S7_CONCERN_HANDLING"    # İtiraz/kaygı yönetimi
    S8_IDEAL_MATCH_SUMMARY = "S8_IDEAL_MATCH_SUMMARY"  # Özet + öneri
    S9_CLOSING = "S9_CLOSING"                      # Kapanış
