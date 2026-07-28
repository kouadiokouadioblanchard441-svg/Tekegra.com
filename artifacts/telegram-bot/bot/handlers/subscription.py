"""Subscription verification handler — triggered by the 'sub:check' button."""
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ChatMemberStatus
from aiogram.types import CallbackQuery
from loguru import logger

from config import settings

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"

_MEMBER_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


@router.callback_query(lambda c: c.data == "sub:check")
async def cb_check_subscription(call: CallbackQuery):
    """Re-check channel membership when the user taps 'J'ai rejoint'."""
    required = settings.required_channel_ids
    user_id = call.from_user.id
    bot = call.bot

    missing = []
    for channel_id in required:
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status not in _MEMBER_STATUSES:
                missing.append(channel_id)
        except Exception as e:
            logger.warning(f"sub:check — cannot verify channel {channel_id}: {e}")
            # Fail open: don't block user if we can't verify
            pass

    if missing:
        await call.answer(
            "❌ Tu n'as pas encore rejoint toutes les chaînes. Réessaie après avoir rejoint !",
            show_alert=True,
        )
        return

    # ── All channels joined — show main menu ──────────────────────────────────
    from bot.keyboards.main_menu import main_menu_keyboard
    from bot.services.settings_service import BotSettingsService
    from bot.utils.navigation import send_menu

    text = (
        f"✅ *Accès débloqué !*\n\n"
        f"{SEP}\n"
        f"│◉ Abonnement vérifié avec succès\n"
        f"│◉ Tu peux maintenant recevoir des prédictions\n"
        f"{SEP}\n\n"
        f"🚀 Bienvenue *{call.from_user.first_name or 'Joueur'}* !"
    )

    try:
        await call.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(settings.BOT_AFFILIATE_LINK),
        )
    except TelegramBadRequest:
        await call.message.answer(
            text,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(settings.BOT_AFFILIATE_LINK),
        )

    await call.answer("✅ Accès débloqué !")
    logger.info(f"sub:check passed for user {user_id}")
