"""Middleware that enforces channel membership before any bot action.

Logic:
  • Admins always bypass the gate.
  • /start always passes through (so new users can be created).
  • The special callback "sub:check" passes through (the verification button).
  • If no CHANNEL_1_ID / CHANNEL_2_ID are configured the gate is disabled.
  • For every other update, the user must be a member (or admin/owner) of ALL
    configured channels. Non-members see a prompt with channel links and a
    "✅ J'ai rejoint — Vérifier" button.
"""
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

from config import settings

# Statuses that count as "member"
_MEMBER_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


def _subscription_keyboard() -> InlineKeyboardMarkup:
    """Build the keyboard shown to non-members."""
    rows = []

    pairs = [
        (settings.CHANNEL_1_ID, settings.CHANNEL_1_NAME, settings.CHANNEL_1_LINK),
        (settings.CHANNEL_2_ID, settings.CHANNEL_2_NAME, settings.CHANNEL_2_LINK),
    ]
    for cid, name, link in pairs:
        if cid.strip():  # only show configured channels
            url = link.strip() or f"https://t.me/c/{str(cid).lstrip('-100')}"
            rows.append([InlineKeyboardButton(text=f"➡️ {name}", url=url)])

    rows.append([
        InlineKeyboardButton(text="✅ J'ai rejoint — Vérifier", callback_data="sub:check")
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _gate_text() -> str:
    channel_lines = []
    pairs = [
        (settings.CHANNEL_1_ID, settings.CHANNEL_1_NAME),
        (settings.CHANNEL_2_ID, settings.CHANNEL_2_NAME),
    ]
    for cid, name in pairs:
        if cid.strip():
            channel_lines.append(f"│◉ {name}")

    channels_block = "\n".join(channel_lines) if channel_lines else "│◉ Notre canal officiel"

    return (
        f"🔒 *Accès restreint*\n\n"
        f"{SEP}\n"
        f"Pour utiliser le bot et recevoir les prédictions,\n"
        f"tu dois rejoindre nos chaînes :\n\n"
        f"{channels_block}\n"
        f"{SEP}\n\n"
        f"1️⃣ Rejoins les chaînes ci-dessous\n"
        f"2️⃣ Clique sur ✅ *J'ai rejoint — Vérifier*"
    )


async def _is_member(bot, user_id: int, channel_id: int) -> bool:
    """Return True if the user is a member / admin / creator of the channel."""
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in _MEMBER_STATUSES
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
        required = settings.required_channel_ids
        # Gate disabled — no channels configured
        if not required:
            return await handler(event, data)

        # ── Identify user & bot ────────────────────────────────────────────────
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        bot = data.get("bot")
        if bot is None:
            return await handler(event, data)

        # ── Admins always bypass ───────────────────────────────────────────────
        if user.id in settings.admin_ids_list:
            return await handler(event, data)

        # ── /start always passes through ───────────────────────────────────────
        if isinstance(event, Message) and event.text and event.text.startswith("/start"):
            return await handler(event, data)

        # ── Verification button passes through ─────────────────────────────────
        if isinstance(event, CallbackQuery) and event.data == "sub:check":
            return await handler(event, data)

        # ── Check membership for every required channel ────────────────────────
        for channel_id in required:
            if not await _is_member(bot, user.id, channel_id):
                logger.debug(f"channel_check: user {user.id} not in channel {channel_id}")
                text = _gate_text()
                kb = _subscription_keyboard()

                if isinstance(event, CallbackQuery):
                    try:
                        await event.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
                    except TelegramBadRequest:
                        await event.message.answer(text, parse_mode="Markdown", reply_markup=kb)
                    await event.answer("🔒 Rejoins nos chaînes d'abord !", show_alert=False)
                elif isinstance(event, Message):
                    await event.answer(text, parse_mode="Markdown", reply_markup=kb)
                return  # block

        return await handler(event, data)
