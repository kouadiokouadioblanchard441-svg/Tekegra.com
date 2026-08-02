"""Middleware that enforces channel membership before any bot action.

Logic:
  • Admins always bypass the gate.
  • /start always passes through (so new users can be created).
  • The special callback "sub:check" passes through (the verification button).
  • If no channel IDs are configured in bot_settings the gate is disabled.
  • Channel IDs are read from the DB (bot_settings keys: channel_1_id, channel_2_id)
    so they can be changed from the admin panel without restarting the bot.
  • For every other update, the user must be a member (or admin/owner) of ALL
    configured channels. Non-members see a prompt with channel links and a
    "✅ J'ai rejoint — Vérifier" button.
"""
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    TelegramObject,
)
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.settings_service import BotSettingsService

# Statuses that count as "member"
_MEMBER_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}

SEP = "━━━━━━━━━━━━━━━━━━━━━━"

# Channel settings change rarely, while this middleware runs on every update.
# A short TTL removes several Supabase round trips from each button click.
_CHANNEL_CONFIG_TTL_SECONDS = 15.0
_CHANNEL_CONFIG_CACHE: tuple[float, list[dict]] | None = None

# Telegram membership is also stable for a few seconds. Keep this short so a
# newly joined user is not meaningfully delayed, while rapid button clicks do
# not repeat the same Bot API request.
_MEMBERSHIP_TTL_SECONDS = 5.0
_MEMBERSHIP_CACHE: dict[tuple[int, int], tuple[float, bool]] = {}


async def _get_channel_config(session: AsyncSession) -> list[dict]:
    """Return a list of {id, name, link} dicts for configured channels."""
    global _CHANNEL_CONFIG_CACHE
    now = time.monotonic()
    if _CHANNEL_CONFIG_CACHE and now - _CHANNEL_CONFIG_CACHE[0] < _CHANNEL_CONFIG_TTL_SECONDS:
        return _CHANNEL_CONFIG_CACHE[1]

    svc = BotSettingsService(session)
    channels = []
    for slot in ("1", "2"):
        raw_id = await svc.get(f"channel_{slot}_id", "")
        raw_id = (raw_id or "").strip()
        if not raw_id:
            continue
        try:
            channel_id = int(raw_id)
        except ValueError:
            logger.warning(f"channel_check: invalid channel_{slot}_id value: {raw_id!r}")
            continue
        name = await svc.get(f"channel_{slot}_name", f"📢 Canal {slot}")
        link = await svc.get(f"channel_{slot}_link", "")
        channels.append({"id": channel_id, "name": name or f"📢 Canal {slot}", "link": link or ""})
    _CHANNEL_CONFIG_CACHE = (now, channels)
    return channels


def _subscription_keyboard(channels: list[dict]) -> InlineKeyboardMarkup:
    """Build the keyboard shown to non-members."""
    rows = []
    for ch in channels:
        url = ch["link"] or f"https://t.me/c/{str(ch['id']).lstrip('-100')}"
        rows.append([InlineKeyboardButton(text=f"➡️ {ch['name']}", url=url)])
    rows.append([
        InlineKeyboardButton(text="✅ J'ai rejoint — Vérifier", callback_data="sub:check")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _gate_text(channels: list[dict]) -> str:
    channel_lines = "\n".join(f"│◉ {ch['name']}" for ch in channels) or "│◉ Notre canal officiel"
    return (
        f"🔒 *Accès restreint*\n\n"
        f"{SEP}\n"
        f"Pour utiliser le bot et recevoir les prédictions,\n"
        f"tu dois rejoindre nos chaînes :\n\n"
        f"{channel_lines}\n"
        f"{SEP}\n\n"
        f"1️⃣ Rejoins les chaînes ci-dessous\n"
        f"2️⃣ Clique sur ✅ *J'ai rejoint — Vérifier*"
    )


async def _is_member(bot, user_id: int, channel_id: int) -> bool:
    """Return True if the user is a member / admin / creator of the channel."""
    key = (user_id, channel_id)
    now = time.monotonic()
    cached = _MEMBERSHIP_CACHE.get(key)
    if cached and now - cached[0] < _MEMBERSHIP_TTL_SECONDS:
        return cached[1]

    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        result = member.status in _MEMBER_STATUSES
        _MEMBERSHIP_CACHE[key] = (now, result)
        return result
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        # Channel not found or bot not admin — fail open so we don't lock everyone out
        logger.warning(f"channel_check: cannot check channel {channel_id}: {e}")
        return True
    except Exception as e:
        logger.warning(f"channel_check: unexpected error for channel {channel_id}: {e}")
        return True


class ChannelCheckMiddleware(BaseMiddleware):
    """Gate: users must join all configured channels before using the bot."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # ── Identify user & bot ────────────────────────────────────────────────
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        bot = data.get("bot")
        if bot is None:
            return await handler(event, data)

        from config import settings as _settings
        # ── Admins always bypass ───────────────────────────────────────────────
        if user.id in _settings.admin_ids_list:
            return await handler(event, data)

        # ── /start always passes through ───────────────────────────────────────
        if isinstance(event, Message) and event.text:
            command = event.text.strip().split()[0].split("@")[0].casefold()
            if command in {"/start", "start"}:
                return await handler(event, data)

        # ── Verification button passes through ─────────────────────────────────
        if isinstance(event, CallbackQuery) and event.data == "sub:check":
            return await handler(event, data)

        # ── Read channel config from DB ────────────────────────────────────────
        session: AsyncSession | None = data.get("session")
        if session is None:
            # No DB session available — fail open
            return await handler(event, data)

        channels = await _get_channel_config(session)

        # Gate disabled — no channels configured
        if not channels:
            return await handler(event, data)

        # ── Check membership for every required channel ────────────────────────
        for ch in channels:
            if not await _is_member(bot, user.id, ch["id"]):
                logger.debug(f"channel_check: user {user.id} not in channel {ch['id']}")
                text = _gate_text(channels)
                kb = _subscription_keyboard(channels)

                if isinstance(event, CallbackQuery):
                    try:
                        await event.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
                    except TelegramBadRequest:
                        from bot.utils.message_cleaner import send_tracked_message
                        await send_tracked_message(
                            event.message,
                            user.id,
                            text,
                            parse_mode="Markdown",
                            reply_markup=kb,
                        )
                    await event.answer("🔒 Rejoins nos chaînes d'abord !", show_alert=False)
                elif isinstance(event, Message):
                    from bot.utils.message_cleaner import send_tracked_message
                    await send_tracked_message(
                        event,
                        user.id,
                        text,
                        parse_mode="Markdown",
                        reply_markup=kb,
                    )
                return  # block

        return await handler(event, data)
