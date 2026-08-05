"""Start command handler — welcome with photo banner."""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.user_service import UserService
from bot.services.settings_service import BotSettingsService
from bot.keyboards.main_menu import main_menu_keyboard, language_keyboard, back_to_main_keyboard
from bot.utils.navigation import send_menu
from bot.utils.message_cleaner import delete_incoming_message, send_tracked_message
from config import settings
from loguru import logger

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    # Keep the chat clean: remove the user's incoming /start command.
    await delete_incoming_message(message)

    user = message.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )
    logger.info(f"/start from {user.id} (@{user.username}) banned={db_user.is_banned}")

    # ── Banned ────────────────────────────────────────────────────────────────
    if db_user.is_banned:
        await send_tracked_message(message, user.id, "🚫 Votre compte est banni.")
        return

    # ── Send main menu with photo ──────────────────────────────────────────────
    bss = BotSettingsService(session)
    photo = await bss.get("menu_banner")

    text = (
        f"🏆 *Bienvenue {user.first_name or 'Joueur'} !* 🎉\n\n"
        f"◉ *1WIN GAME PREDICTOR* [*{settings.BOT_PROMO_CODE}*]\n\n"
        f"🔥 Activate the bot now and start winning! 🚀"
    )
    await send_menu(message, text, main_menu_keyboard(settings.BOT_AFFILIATE_LINK), photo_id=photo)


@router.message(F.text.casefold() == "start")
async def cmd_start_text(message: Message, session: AsyncSession):
    """Accept plain `start` text as a user-friendly alias for /start."""
    await cmd_start(message, session)


@router.message(Command("menu"))
async def cmd_menu(message: Message, session: AsyncSession):
    bss = BotSettingsService(session)
    photo = await bss.get("menu_banner")
    text = "🎮 *Menu*\n\nChoisis une option ci-dessous 👇"
    await send_menu(message, text, main_menu_keyboard(settings.BOT_AFFILIATE_LINK), photo_id=photo)


@router.message(Command("language"))
async def cmd_language(message: Message):
    await delete_incoming_message(message)
    await send_tracked_message(
        message,
        message.from_user.id,
        "🌍 *Choisissez votre langue :*",
        parse_mode="Markdown",
        reply_markup=language_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message, session: AsyncSession):
    bss = BotSettingsService(session)
    photo = await bss.get("menu_banner")
    text = (
        "❓ *AIDE — Bot 1WIN Predictions*\n\n"
        f"{SEP}\n"
        "│◉ `/start` — Démarrer le bot\n"
        "│◉ `/menu` — Menu principal\n"
        "│◉ `/profile` — Mon profil\n"
        "│◉ `/premium` — Abonnement Premium\n"
        "│◉ `/language` — Changer de langue\n"
        "│◉ `/help` — Cette aide\n"
        f"{SEP}\n\n"
        f"🎁 Code promo : *{settings.BOT_PROMO_CODE}*"
    )
    await send_menu(message, text, main_menu_keyboard(settings.BOT_AFFILIATE_LINK), photo_id=photo)


@router.message(Command("profile"))
async def cmd_profile(message: Message, session: AsyncSession):
    from bot.handlers.profile import show_profile
    await show_profile(message, session)


@router.message(Command("premium"))
async def cmd_premium(message: Message, session: AsyncSession):
    from bot.handlers.premium import show_premium
    await show_premium(message, session)
