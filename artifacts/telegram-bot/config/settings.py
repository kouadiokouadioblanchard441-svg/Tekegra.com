import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram/Vercel webhook contract
    BOT_TOKEN: str = ""
    APP_URL: str = ""
    WEBHOOK_SECRET: str = ""
    ADMIN_ID: str = ""

    # Bot config
    BOT_PROMO_CODE: str = "JRYVES"
    BOT_AFFILIATE_LINK: str = "https://1win.com"
    BOT_NAME: str = "Lucky Jet AI Bot"
    FREE_SIGNALS_TOTAL: int = 10       # total à vie pour les gratuits
    FREE_SIGNALS_PER_DAY: int = 10    # gardé pour compatibilité (non utilisé)
    PREMIUM_SIGNALS_PER_DAY: int = 9

    # Database (accepts DATABASE_URL or SUPABASE_DATABASE_URL)
    DATABASE_URL: str = ""
    SUPABASE_DATABASE_URL: str = ""

    @property
    def effective_database_url(self) -> str:
        return self.SUPABASE_DATABASE_URL or self.DATABASE_URL

    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Channels (links to join, shown in guide)
    CHANNEL_1_LINK: str = ""   # e.g. https://t.me/moncanal1
    CHANNEL_1_NAME: str = "📢 Canal Officiel"
    CHANNEL_2_LINK: str = ""   # e.g. https://t.me/moncanal2
    CHANNEL_2_NAME: str = "📢 Canal Signaux VIP"

    # Channel IDs for membership enforcement (integers, e.g. -1001234567890)
    # Leave empty to disable the subscription gate for that slot.
    CHANNEL_1_ID: str = ""
    CHANNEL_2_ID: str = ""

    @property
    def required_channel_ids(self) -> list[int]:
        """Return the list of channel IDs that users must join."""
        ids = []
        for raw in (self.CHANNEL_1_ID, self.CHANNEL_2_ID):
            raw = raw.strip()
            if raw:
                try:
                    ids.append(int(raw))
                except ValueError:
                    pass
        return ids

    # Anti-spam
    THROTTLE_RATE: float = 0.5  # seconds between requests

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.ADMIN_ID:
            return []
        try:
            return [int(self.ADMIN_ID.strip())]
        except ValueError:
            return []

    @property
    def async_database_url(self) -> str:
        url = self.effective_database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
