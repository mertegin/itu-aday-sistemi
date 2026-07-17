"""Ethics filter testleri — yakalama, sanitize, güvenli değişim."""
from app.guardrails.ethics import EthicsFilter, enforce_conversation_voice, enforce_spoken_length


def test_clean_text_passes():
    f = EthicsFilter()
    text, result = f.enforce("İTÜ'nün mühendislik odağı güçlü; senin hedefine göre değerlendirebiliriz.")
    assert result["clean"]
    assert not result["replaced"]


def test_disparaging_caught_and_replaced():
    f = EthicsFilter()
    text, result = f.enforce("Boğaziçi kötü bir üniversite, oraya gitme.")
    assert result["replaced"]
    assert "kötü" not in text.lower()


def test_absolutist_softened_by_sanitize():
    f = EthicsFilter()
    text, result = f.enforce("İTÜ kesinlikle en iyi seçim, hiç şüphesiz.")
    # soft_sanitize "kesinlikle en iyi" → "güçlü seçeneklerden biri" çevirir; kalan temiz olmalı
    assert "kesinlikle en iyi" not in text.lower()


def test_judgmental_replaced():
    f = EthicsFilter()
    text, result = f.enforce("Bu sıralamayla başaramazsın bence.")
    assert "başaramazsın" not in text.lower()


def test_dogru_mu_anladim_removed():
    f = EthicsFilter()
    text = f.soft_sanitize("Yazılım seviyorsun yani. Doğru mu anladım?")
    assert "doğru mu anladım" not in text.lower()


def test_yks_hazirlik_fixed():
    f = EthicsFilter()
    text = f.soft_sanitize("YKS'ye hazırlık sürecinde nasıl gidiyor?")
    assert "hazırlık sürecinde" not in text.lower()
    assert "tercih sürecinde" in text.lower()


def test_spoken_length_is_hard_limited_without_cutting_mid_word():
    long_text = " ".join(f"kelime{i}" for i in range(55))
    text, meta = enforce_spoken_length(long_text, max_words=40)
    assert meta["trimmed"] is True
    assert len(text.split()) <= 40
    assert text.endswith(".")


def test_spoken_length_prefers_complete_sentences():
    text, meta = enforce_spoken_length(
        "İTÜ Bilgisayar geniş bir temel sunar. " + " ".join(["ayrıntı"] * 45),
        max_words=10,
    )
    assert text == "İTÜ Bilgisayar geniş bir temel sunar."
    assert meta["trimmed"] is True


def test_canned_question_is_removed_even_when_user_did_not_request_detail():
    text, meta = enforce_conversation_voice(
        "Bizim kampüsümüzde Selfish ve Med Çim sosyalleşme için öne çıkıyor. Ne dersin?",
        "itu_campus_life",
    )
    assert text.endswith("öne çıkıyor.")
    assert "Ne dersin" not in text
    assert meta["question_removed"] is True
