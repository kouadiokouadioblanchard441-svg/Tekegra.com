"""Start command handler — welcome with photo banner, approval gate."""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.user_service import UserService
from bot.services.settings_service import BotSettingsService
from bot.keyboards.main_menu import main_menu_keyboard, language_keyboard, back_to_main_keyboard
from bot.keyboards.admin import admin_approve_reject_keyboard
from bot.utils.navigation import send_menu
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
    logger.info(
        f"/start from {user.id} (@{user.username}) "
        f"status={db_user.approval_status}, banned={db_user.is_banned}"
    )

    # ── Banned ────────────────────────────────────────────────────────────────
    if db_user.is_banned:
        await message.answer("🚫 Votre compte est banni.")
        return

    # ── Rejected ──────────────────────────────────────────────────────────────
    if db_user.approval_status == "rejected":
        await message.answer(
            f"🚫 *Accès refusé*\n\n{SEP}\n"
            "│◉ Votre demande d'accès a été *refusée*.\n"
            "│◉ Contactez le support si vous pensez qu'il s'agit d'une erreur.\n"
            f"{SEP}",
            parse_mode="Markdown",
        )
        return

    # ── Pending ───────────────────────────────────────────────────────────────
    if db_user.approval_status == "pending":
        is_new = getattr(db_user, "_is_new", False)
        await message.answer(
            f"⏳ *Demande d'accès en cours...*\n\n{SEP}\n"
            "│◉ Votre compte est en attente d'approbation.\n"
            "│◉ Un admin va examiner votre demande.\n"
            "│◉ Vous serez notifié(e) dès l'approbation.\n"
            f"{SEP}\n\n"
            f"🎁 Code promo pour 1WIN : `{settings.BOT_PROMO_CODE}`",
            parse_mode="Markdown",
        )
        if is_new:
            await _notify_admins_new_user(message, db_user)
        return

    # ── Approved — send main menu with photo ──────────────────────────────────
    bss = BotSettingsService(session)
    photo = await bss.get("menu_banner")

    text = (
        f"🏆 *Bienvenue {user.first_name or 'Joueur'} !* 🎉\n\n"
        f"◉ *1WIN GAME PREDICTOR* [`{settings.BOT_PROMO_CODE}`]\n\n"
        f"🔥 Activate the bot now and start winning! 🚀"
    )
    await send_menu(message, text, main_menu_keyboard(settings.BOT_AFFILIATE_LINK), photo_id=photo)


@router.message(Command("menu"))
async def cmd_menu(message: Message, session: AsyncSession):
    bss = BotSettingsService(session)
    photo = await bss.get("menu_banner")
    text = "🎮 *Menu*\n\nChoisis une option ci-dessous 👇"
    await send_menu(message, text, main_menu_keyboard(settings.BOT_AFFILIATE_LINK), photo_id=photo)


@router.message(Command("language"))
async def cmd_language(message: Message):
    await message.answer(
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
        f"🎁 Code promo : `{settings.BOT_PROMO_CODE}`"
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
