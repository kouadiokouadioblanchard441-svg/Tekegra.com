"""Start command handler — welcome, approval gate, language selection."""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.user_service import UserService
from bot.utils.formatters import format_welcome
from bot.keyboards.main_menu import main_menu_keyboard, language_keyboard
from bot.keyboards.admin import admin_approve_reject_keyboard
from config import settings
from loguru import logger

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


async def _notify_admins_new_user(message: Message, db_user) -> None:
    """Send a new-user notification to every admin with approve/reject buttons."""
    user = message.from_user
    text = (
        f"🆕 *Nouvel utilisateur en attente !*\n\n"
        f"{SEP}\n"
        f"│◉ *Nom* : {user.first_name or '—'} {user.last_name or ''}\n"
        f"│◉ *Username* : @{user.username or '—'}\n"
        f"│◉ *ID* : `{user.id}`\n"
        f"│◉ *Langue* : {user.language_code or 'fr'}\n"
        f"{SEP}\n\n"
        "Accepter ou refuser l'accès ?"
    )
    keyboard = admin_approve_reject_keyboard(user.id)
    for admin_id in settings.admin_ids_list:
        try:
            await message.bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
        except Exception as e:
            logger.warning(f"Could not notify admin {admin_id}: {e}")


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
    logger.info(f"/start from {user.id} (@{user.username}) — status={db_user.approval_status}, banned={db_user.is_banned}")

    # ── Banned — check even on /start ─────────────────────────────────────────
    if db_user.is_banned:
        await message.answer("🚫 Votre compte est banni.")
        return

    # ── Rejected ─────────────────────────────────────────────────────────────
    if db_user.approval_status == "rejected":
        await message.answer(
            f"🚫 *Accès refusé*\n\n"
            f"{SEP}\n"
            f"│◉ Votre demande d'accès a été *refusée*.\n"
            f"│◉ Contactez le support si vous pensez\n"
            f"│   qu'il s'agit d'une erreur.\n"
            f"{SEP}",
            parse_mode="Markdown",
        )
        return

    # ── Pending ───────────────────────────────────────────────────────────────
    if db_user.approval_status == "pending":
        is_new = getattr(db_user, "_is_new", False)
        await message.answer(
            f"⏳ *Demande d'accès en cours...*\n\n"
            f"{SEP}\n"
            f"│◉ Votre compte est en attente d'approbation.\n"
            f"│◉ Un admin va examiner votre demande.\n"
            f"│◉ Vous serez notifié(e) dès l'approbation.\n"
            f"{SEP}\n\n"
            f"🎁 Code promo pour 1WIN : `{settings.BOT_PROMO_CODE}`",
            parse_mode="Markdown",
        )
        if is_new:
            await _notify_admins_new_user(message, db_user)
        return

    # ── Approved ──────────────────────────────────────────────────────────────
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
async def cmd_menu(message: Message):
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
        "❓ *AIDE — Bot 1WIN Predictions*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "│◉ `/start` — Démarrer le bot\n"
        "│◉ `/menu` — Menu principal\n"
        "│◉ `/luckyjet` — Signaux Lucky Jet\n"
        "│◉ `/rocketqueen` — Signaux Rocket Queen\n"
        "│◉ `/profile` — Mon profil\n"
        "│◉ `/premium` — Abonnement Premium\n"
        "│◉ `/history` — Historique des signaux\n"
        "│◉ `/language` — Changer de langue\n"
        "│◉ `/help` — Cette aide\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎁 Code promo : `{settings.BOT_PROMO_CODE}`"
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


@router.message(Command("rocketqueen"))
async def cmd_rocketqueen(message: Message):
    from bot.keyboards.rocketqueen import rocketqueen_menu_keyboard
    await message.answer(
        "👑 *Rocket Queen* — Choisis une option :",
        parse_mode="Markdown",
        reply_markup=rocketqueen_menu_keyboard(),
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
