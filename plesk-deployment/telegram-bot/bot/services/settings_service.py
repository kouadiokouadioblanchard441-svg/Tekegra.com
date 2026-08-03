"""BotSettings key/value store service."""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import BotSettings


class BotSettingsService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        setting = result.scalar_one_or_none()
        return setting.value if setting else default

    async def set(self, key: str, value: str) -> None:
        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = BotSettings(key=key, value=value)
            self.session.add(setting)
        await self.session.commit()

    async def delete(self, key: str) -> None:
        result = await self.session.execute(
            select(BotSettings).where(BotSettings.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            await self.session.delete(setting)
            await self.session.commit()
