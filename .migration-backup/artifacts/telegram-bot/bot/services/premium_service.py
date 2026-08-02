"""Premium subscription management."""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.models import PremiumSubscription, User
from loguru import logger


class PremiumService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def activate_premium(
        self,
        user_id: int,
        days: int = 30,
        payment_method: str = "manual",
        amount: float = 0.0,
    ) -> PremiumSubscription:
        # Check existing subscription
        result = await self.session.execute(
            select(PremiumSubscription)
            .where(
                PremiumSubscription.user_id == user_id,
                PremiumSubscription.is_active == True,
            )
        )
        existing = result.scalar_one_or_none()

        now = datetime.utcnow()
        expires_at = now + timedelta(days=days)

        if existing:
            # Extend existing
            if existing.expires_at and existing.expires_at > now:
                expires_at = existing.expires_at + timedelta(days=days)
            existing.expires_at = expires_at
            existing.is_active = True
            await self.session.commit()
            sub = existing
        else:
            sub = PremiumSubscription(
                user_id=user_id,
                started_at=now,
                expires_at=expires_at,
                payment_method=payment_method,
                amount=amount,
                is_active=True,
            )
            self.session.add(sub)

        # Update user
        await self.session.execute(
            update(User)
            .where(User.telegram_id == user_id)
            .values(is_premium=True)
        )
        await self.session.commit()
        logger.info(f"Premium activated for user {user_id} until {expires_at}")
        return sub

    async def deactivate_premium(self, user_id: int) -> None:
        await self.session.execute(
            update(PremiumSubscription)
            .where(PremiumSubscription.user_id == user_id)
            .values(is_active=False)
        )
        await self.session.execute(
            update(User)
            .where(User.telegram_id == user_id)
            .values(is_premium=False)
        )
        await self.session.commit()

    async def get_subscription(self, user_id: int) -> Optional[PremiumSubscription]:
        result = await self.session.execute(
            select(PremiumSubscription)
            .where(
                PremiumSubscription.user_id == user_id,
                PremiumSubscription.is_active == True,
            )
            .order_by(PremiumSubscription.started_at.desc())
        )
        return result.scalar_one_or_none()

    async def check_and_expire(self) -> int:
        """Deactivate expired subscriptions. Returns count of deactivated."""
        now = datetime.utcnow()
        result = await self.session.execute(
            select(PremiumSubscription).where(
                PremiumSubscription.is_active == True,
                PremiumSubscription.expires_at < now,
            )
        )
        expired = result.scalars().all()
        count = 0
        for sub in expired:
            sub.is_active = False
            await self.session.execute(
                update(User)
                .where(User.telegram_id == sub.user_id)
                .values(is_premium=False)
            )
            count += 1
        if count:
            await self.session.commit()
            logger.info(f"Expired {count} premium subscriptions")
        return count
