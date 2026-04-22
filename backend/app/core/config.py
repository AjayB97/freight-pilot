from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Freight Pilot API"
    environment: str = "development"

    # Comma-separated list of valid API keys. First key is the "primary".
    api_keys: str = "dev-local-key"

    # SQLite file (mounted as a volume in production).
    database_url: str = "sqlite:///./data/freight_pilot.db"

    # FMCSA QCMobile API
    fmcsa_api_key: str = ""
    fmcsa_base_url: str = "https://mobile.fmcsa.dot.gov/qc/services"

    # Negotiation policy (business rules)
    negotiation_max_rounds: int = 3
    # Max percentage above loadboard_rate the broker is authorized to pay.
    negotiation_max_markup_pct: float = 0.15
    # Minimum percentage of loadboard_rate the broker will accept (floor).
    negotiation_min_floor_pct: float = 0.92

    # CORS - allow the dashboard origins
    cors_origins: str = "http://localhost:3000"

    @property
    def api_key_set(self) -> set[str]:
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
