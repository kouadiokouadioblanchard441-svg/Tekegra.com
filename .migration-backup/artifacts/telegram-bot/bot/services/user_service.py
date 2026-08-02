"""User management service."""
from datetime import datetime, date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from database.models import User, SignalHistory, PremiumSubscription
from config import settings
from loguru import logger


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
        language_code: Optional[str],
    ) -> User:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code or "fr",
                approval_status="pending",  # new users must be approved
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            user._is_new = True  # signal to start handler
            logger.info(f"New user registered (pending): {telegram_id} (@{username})")
        else:
            user._is_new = False
            # Updating activity on every callback forces a remote Supabase
            # commit before every screen can be displayed. Keep the activity
            # timestamp useful without turning every button click into a
            # write round trip.
            dirty = False
            now = datetime.utcnow()
            if user.last_active is None or (now - user.last_active).total_seconds() >= 60:
                user.last_active = now
                dirty = True
            if username:
                if user.username != username:
                    user.username = username
                    dirty = True
            if first_name:
                if user.first_name != first_name:
                    user.first_name = first_name
                    dirty = True
            if dirty:
                await self.session.commit()

        return user

    async def get_by_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def set_language(self, telegram_id: int, lang: str) -> None:
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(language_code=lang)
        )
        await self.session.commit()

    async def approve_user(self, telegram_id: int) -> bool:
        """Approve a pending user. Returns True if user was found."""
        result = await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(approval_status="approved")
            .returning(User.telegram_id)
        )
        await self.session.commit()
        return result.scalar_one_or_none() is not None

    async def reject_user(self, telegram_id: int) -> bool:
        """Reject a user. Returns True if user was found."""
        result = await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(approval_status="rejected")
            .returning(User.telegram_id)
        )
        await self.session.commit()
        return result.scalar_one_or_none() is not None

    async def get_pending_users(self) -> list:
        result = await self.session.execute(
            select(User).where(User.approval_status == "pending")
            .order_by(User.registered_at.asc())
        )
        return result.scalars().all()

    async def try_consume_free_signal(self, user: User) -> tuple[bool, int]:
        """Atomically check and consume a free signal (quota total à vie).

        Returns (allowed, remaining_after_consume).
        """
        if user.free_signals_used_total >= settings.FREE_SIGNALS_TOTAL:
            return False, 0

        user.free_signals_used_total += 1
        user.total_analyses += 1
        await self.session.commit()
        remaining = settings.FREE_SIGNALS_TOTAL - user.free_signals_used_total
        return True, remaining

    async def can_use_free_signal(self, user: User) -> bool:
        return user.free_signals_used_total < settings.FREE_SIGNALS_TOTAL

    async def consume_free_signal(self, user: User) -> int:
        user.free_signals_used_total += 1
        user.total_analyses += 1
        await self.session.commit()
        return settings.FREE_SIGNALS_TOTAL - user.free_signals_used_total

    async def consume_premium_signal(self, user: User) -> None:
        user.total_analyses += 1
        await self.session.commit()

    async def save_signal(
        self,
        user_id: int,
        game_type: str,
        signal_data: dict,
        is_premium: bool,
    ) -> None:
        record = SignalHistory(
            user_id=user_id,
            game_type=game_type,
            signal_data=signal_data,
            is_premium=is_premium,
        )
        self.session.add(record)
        await self.session.commit()

    async def get_history(self, telegram_id: int, limit: int = 10) -> list:
        result = await self.session.execute(
            select(SignalHistory)
            .where(SignalHistory.user_id == telegram_id)
            .order_by(SignalHistory.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_total_users(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar_one()

    async def get_premium_users_count(self) -> int:
        result = await self.session.execute(
            select(func.count(User.id)).where(User.is_premium == True)
        )
        return result.scalar_one()

    async def get_active_today(self) -> int:
        today = datetime.utcnow().date()
        result = await self.session.execute(
            select(func.count(User.id)).where(
                func.date(User.last_active) == today
            )
        )
        return result.scalar_one()

    async def get_total_signals(self) -> int:
        result = await self.session.execute(select(func.count(SignalHistory.id)))
        return result.scalar_one()

    async def get_pending_count(self) -> int:
        result = await self.session.execute(
            select(func.count(User.id)).where(User.approval_status == "pending")
        )
        return result.scalar_one()

    async def get_all_users(self) -> list:
        """Returns approved, non-banned users (for broadcasts)."""
        result = await self.session.execute(
            select(User).where(
                User.is_banned == False,
                User.approval_status == "approved",
            )
        )
        return result.scalars().all()

    async def set_premium(self, telegram_id: int, is_premium: bool) -> None:
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(is_premium=is_premium)
        )
        await self.session.commit()

    async def ban_user(self, telegram_id: int) -> None:
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(is_banned=True)
        )
        await self.session.commit()

    async def mark_registered(self, telegram_id: int) -> None:
        """Mark user as having registered on 1WIN with the affiliate link."""
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(has_registered=True)
        )
        await self.session.commit()
