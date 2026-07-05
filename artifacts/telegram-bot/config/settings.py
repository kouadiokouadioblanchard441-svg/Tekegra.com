import os
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    ADMIN_IDS: str = ""

    # Bot config
    BOT_PROMO_CODE: str = "JRYVES"
    BOT_AFFILIATE_LINK: str = "https://1win.com"
    BOT_NAME: str = "Lucky Jet AI Bot"
    FREE_SIGNALS_PER_DAY: int = 6
    PREMIUM_SIGNALS_PER_DAY: int = 9

    # Database
    DATABASE_URL: str = ""

    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Channels (links to join, shown in guide)
    CHANNEL_1_LINK: str = ""   # e.g. https://t.me/moncanal1
    CHANNEL_1_NAME: str = "📢 Canal Officiel"
    CHANNEL_2_LINK: str = ""   # e.g. https://t.me/moncanal2
    CHANNEL_2_NAME: str = "📢 Canal Signaux VIP"

    # Anti-spam
    THROTTLE_RATE: float = 0.5  # seconds between requests

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip()]

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
