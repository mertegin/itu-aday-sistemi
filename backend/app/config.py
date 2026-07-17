from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite+aiosqlite:///./aday_sistemi.db"

    # Bandit — demo için deterministic-ağırlıklı (düşük exploration).
    # Saha/deney modunda kappa'yı 1.41'e çıkar.
    bandit_kappa: float = 0.5
    bandit_cold_start_bonus: float = 0.05
    bandit_repeat_penalty: float = 0.70
    bandit_recent_penalty: float = 0.85


settings = Settings()
