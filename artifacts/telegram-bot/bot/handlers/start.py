"""Start command handler — welcome message and language selection."""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.user_service import UserService
from bot.utils.formatters import format_welcome
from bot.keyboards.main_menu import main_menu_keyboard, language_keyboard
from config import settings
from loguru import logger

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    user = message.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )
    logger.info(f"/start from {user.id} (@{user.username})")

    welcome_text = format_welcome(
        first_name=user.first_name or "Joueur",
        free_count=settings.FREE_SIGNALS_PER_DAY,
        premium_count=settings.PREMIUM_SIGNALS_PER_DAY,
        promo_code=settings.BOT_PROMO_CODE,
        affiliate_link=settings.BOT_AFFILIATE_LINK,
    )

    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(settings.BOT_AFFILIATE_LINK),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, session: AsyncSession):
    await message.answer(
        "🎯 *Menu principal* — Choisis une option :",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(settings.BOT_AFFILIATE_LINK),
    )


@router.message(Command("language"))
async def cmd_language(message: Message):
    await message.answer(
        "🌍 *Choisissez votre langue :*",
        parse_mode="Markdown",
        reply_markup=language_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    text = (
        "❓ *AIDE — Lucky Jet AI Bot*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "│◉ `/start` — Démarrer le bot\n"
        "│◉ `/menu` — Menu principal\n"
        "│◉ `/luckyjet` — Signaux Lucky Jet\n"
        "│◉ `/mines` — Signaux Mines\n"
        "│◉ `/profile` — Mon profil\n"
        "│◉ `/premium` — Abonnement Premium\n"
        "│◉ `/history` — Historique des signaux\n"
        "│◉ `/language` — Changer de langue\n"
        "│◉ `/help` — Cette aide\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📣 Code promo : `{settings.BOT_PROMO_CODE}`"
    )
    await message.answer(text, parse_mode="Markdown",
                         reply_markup=main_menu_keyboard(settings.BOT_AFFILIATE_LINK))


@router.message(Command("luckyjet"))
async def cmd_luckyjet(message: Message):
    from bot.keyboards.luckyjet import luckyjet_menu_keyboard
    await message.answer(
        "🎯 *Lucky Jet* — Choisis une option :",
        parse_mode="Markdown",
        reply_markup=luckyjet_menu_keyboard(),
    )


@router.message(Command("mines"))
async def cmd_mines(message: Message):
    from bot.keyboards.mines import mines_menu_keyboard
    await message.answer(
        "💣 *Mines* — Choisis une option :",
        parse_mode="Markdown",
        reply_markup=mines_menu_keyboard(),
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message, session: AsyncSession):
    from bot.handlers.profile import show_profile
    await show_profile(message, session)


@router.message(Command("premium"))
async def cmd_premium(message: Message):
    from bot.handlers.premium import show_premium
    await show_premium(message)


@router.message(Command("history"))
async def cmd_history(message: Message, session: AsyncSession):
    from bot.handlers.profile import show_history
    await show_history(message, session)


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    await message.answer(
        "⚙️ *Paramètres*\n\nUtilise le menu ci-dessous pour configurer le bot.",
        parse_mode="Markdown",
        reply_markup=language_keyboard(),
    )
