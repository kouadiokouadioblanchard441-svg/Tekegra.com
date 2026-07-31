"""Admin panel handlers — stats, user management, broadcast, approve/reject."""
import asyncio
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.admin_filter import IsAdmin
from bot.services.user_service import UserService
from bot.services.premium_service import PremiumService
from bot.services.settings_service import BotSettingsService
from bot.utils.formatters import format_admin_stats
from bot.keyboards.admin import (
    admin_keyboard,
    admin_user_action_keyboard,
    admin_approve_reject_keyboard,
    admin_confirm_broadcast_keyboard,
)
from config import settings
from loguru import logger

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


class BroadcastState(StatesGroup):
    waiting_message = State()
    confirm = State()


class BannerState(StatesGroup):
    waiting_photo = State()


# ── Panel entry ──────────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    text = (
        f"🛡️ *PANNEAU ADMIN*\n\n"
        f"{SEP}\n"
        f"│◉ Bienvenue, Admin !\n"
        f"│◉ ID : `{message.from_user.id}`\n"
        f"{SEP}\n\n"
        "Choisissez une action :"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=admin_keyboard())


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(call: CallbackQuery, session: AsyncSession):
    svc = UserService(session)
    total = await svc.get_total_users()
    premium = await svc.get_premium_users_count()
    active = await svc.get_active_today()
    signals = await svc.get_total_signals()
    pending = await svc.get_pending_count()

    text = format_admin_stats(
        total_users=total,
        premium_users=premium,
        active_today=active,
        total_signals=signals,
        pending_users=pending,
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_keyboard())
    await call.answer()


# ── Users list ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:users")
async def cb_admin_users(call: CallbackQuery, session: AsyncSession):
    svc = UserService(session)
    total = await svc.get_total_users()
    premium = await svc.get_premium_users_count()
    pending = await svc.get_pending_count()

    text = (
        f"👥 *GESTION UTILISATEURS*\n\n"
        f"{SEP}\n"
        f"│◉ Total : *{total}*\n"
        f"│◉ Approuvés Premium : *{premium}*\n"
        f"│◉ En attente : *{pending}* ⏳\n"
        f"│◉ Gratuits approuvés : *{total - premium - pending}*\n"
        f"{SEP}\n\n"
        "Pour gérer un utilisateur :\n"
        "`/admin_user <telegram_id>`"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_keyboard())
    await call.answer()


# ── Pending users list ────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:pending")
async def cb_admin_pending(call: CallbackQuery, session: AsyncSession):
    svc = UserService(session)
    pending = await svc.get_pending_users()

    if not pending:
        text = (
            f"⏳ *UTILISATEURS EN ATTENTE*\n\n"
            f"{SEP}\n"
            f"│◉ Aucun utilisateur en attente ✅\n"
            f"{SEP}"
        )
        await call.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_keyboard())
        await call.answer()
        return

    lines = [f"⏳ *UTILISATEURS EN ATTENTE* ({len(pending)})\n{SEP}"]
    for u in pending[:10]:  # show max 10
        name = f"{u.first_name or ''} {u.last_name or ''}".strip() or "—"
        lines.append(
            f"│◉ `{u.telegram_id}` — {name} (@{u.username or '—'})\n"
            f"│   [Inscrip. {u.registered_at.strftime('%d/%m %H:%M')}]"
        )
    lines.append(SEP)
    lines.append("\nUtilise `/admin_user <id>` pour agir sur un utilisateur.")

    await call.message.edit_text(
        "\n".join(lines), parse_mode="Markdown", reply_markup=admin_keyboard()
    )
    await call.answer()


# ── Approve / Reject ──────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:approve:"))
async def cb_approve_user(call: CallbackQuery, session: AsyncSession, bot: Bot):
    try:
        user_id = int(call.data.split(":")[-1])
    except (ValueError, IndexError):
        await call.answer("❌ Données invalides", show_alert=True)
        return
    svc = UserService(session)
    found = await svc.approve_user(user_id)

    if not found:
        await call.answer("❌ Utilisateur introuvable", show_alert=True)
        return

    await call.message.edit_text(
        f"✅ *Accès approuvé* pour `{user_id}`",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )
    await call.answer("✅ Approuvé !")
    logger.info(f"Admin {call.from_user.id} approved user {user_id}")

    # Notify the approved user
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"🎉 *Accès approuvé !*\n\n"
                f"{SEP}\n"
                f"│◉ Votre accès au bot a été *approuvé* ✅\n"
                f"│◉ Utilise /start pour accéder au menu.\n"
                f"{SEP}\n\n"
                f"🎁 Code promo 1WIN : *{settings.BOT_PROMO_CODE}*"
            ),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.warning(f"Could not notify user {user_id} of approval: {e}")


@router.callback_query(F.data.startswith("admin:reject:"))
async def cb_reject_user(call: CallbackQuery, session: AsyncSession, bot: Bot):
    try:
        user_id = int(call.data.split(":")[-1])
    except (ValueError, IndexError):
        await call.answer("❌ Données invalides", show_alert=True)
        return
    svc = UserService(session)
    found = await svc.reject_user(user_id)

    if not found:
        await call.answer("❌ Utilisateur introuvable", show_alert=True)
        return

    await call.message.edit_text(
        f"❌ *Accès refusé* pour `{user_id}`",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )
    await call.answer("❌ Refusé")
    logger.info(f"Admin {call.from_user.id} rejected user {user_id}")

    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"🚫 *Accès refusé*\n\n"
                f"Votre demande d'accès n'a pas été approuvée.\n"
                f"Contactez le support si vous pensez qu'il s'agit d'une erreur."
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass


# ── Ban ───────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin:ban:"))
async def cb_ban_user(call: CallbackQuery, session: AsyncSession):
    try:
        user_id = int(call.data.split(":")[-1])
    except (ValueError, IndexError):
        await call.answer("❌ Données invalides", show_alert=True)
        return
    svc = UserService(session)
    await svc.ban_user(user_id)
    await call.message.edit_text(
        f"🚫 *Utilisateur banni* : `{user_id}`",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )
    await call.answer("🚫 Banni")
    logger.info(f"Admin {call.from_user.id} banned user {user_id}")


# ── Admin user details (/admin_user <id>) ─────────────────────────────────────

@router.message(Command("admin_user"))
async def cmd_admin_user(message: Message, session: AsyncSession):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Usage: `/admin_user <telegram_id>`", parse_mode="Markdown")
        return
    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID invalide")
        return

    svc = UserService(session)
    user = await svc.get_by_id(user_id)
    if not user:
        await message.answer("❌ Utilisateur introuvable")
        return

    status_icon = {"approved": "✅", "pending": "⏳", "rejected": "🚫"}.get(
        user.approval_status, "?"
    )
    text = (
        f"👤 *Utilisateur*\n{SEP}\n"
        f"│◉ ID : `{user.telegram_id}`\n"
        f"│◉ Nom : {user.first_name or '—'}\n"
        f"│◉ @{user.username or '—'}\n"
        f"│◉ Accès : {status_icon} {user.approval_status}\n"
        f"│◉ Premium : {'✅' if user.is_premium else '❌'}\n"
        f"│◉ Analyses : {user.total_analyses}\n"
        f"│◉ Banni : {'🚫' if user.is_banned else '✅ Non'}\n"
        f"{SEP}"
    )
    await message.answer(text, parse_mode="Markdown",
                         reply_markup=admin_user_action_keyboard(user_id))


# ── Premium management ────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:premium")
async def cb_admin_premium_menu(call: CallbackQuery):
    await call.message.edit_text(
        f"⭐ *Gérer Premium*\n\n{SEP}\n"
        "Utilise `/admin_user <telegram_id>` pour activer / désactiver le premium\n"
        "d'un utilisateur spécifique.\n"
        f"{SEP}",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:prem_on:"))
async def cb_activate_premium(call: CallbackQuery, session: AsyncSession):
    try:
        user_id = int(call.data.split(":")[-1])
    except (ValueError, IndexError):
        await call.answer("❌ Données invalides", show_alert=True)
        return
    svc = PremiumService(session)
    await svc.activate_premium(user_id, days=30, payment_method="admin")
    await call.message.edit_text(
        f"✅ *Premium activé* (30 jours) pour `{user_id}`",
        parse_mode="Markdown", reply_markup=admin_keyboard()
    )
    await call.answer("✅ Premium activé")
    logger.info(f"Admin {call.from_user.id} activated premium for {user_id}")


@router.callback_query(F.data.startswith("admin:prem_off:"))
async def cb_deactivate_premium(call: CallbackQuery, session: AsyncSession):
    try:
        user_id = int(call.data.split(":")[-1])
    except (ValueError, IndexError):
        await call.answer("❌ Données invalides", show_alert=True)
        return
    svc = PremiumService(session)
    await svc.deactivate_premium(user_id)
    await call.message.edit_text(
        f"❌ *Premium désactivé* pour `{user_id}`",
        parse_mode="Markdown", reply_markup=admin_keyboard()
    )
    await call.answer("❌ Premium désactivé")


# ── Broadcast ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:broadcast")
async def cb_broadcast_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastState.waiting_message)
    await call.message.edit_text(
        "📢 *Diffusion de message*\n\n"
        "Envoyez le message à diffuser à tous les utilisateurs approuvés.\n"
        "Vous pouvez utiliser le format Markdown.\n\n"
        "Envoyez /cancel pour annuler.",
        parse_mode="Markdown",
    )
    await call.answer()


@router.message(BroadcastState.waiting_message)
async def cb_broadcast_message(message: Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text or message.caption or "")
    await state.set_state(BroadcastState.confirm)
    await message.answer(
        f"📢 *Message à diffuser :*\n\n{message.text}\n\n"
        "Confirmez l'envoi ?",
        parse_mode="Markdown",
        reply_markup=admin_confirm_broadcast_keyboard(),
    )


@router.callback_query(F.data == "admin:broadcast_confirm")
async def cb_broadcast_confirm(call: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    data = await state.get_data()
    text = data.get("broadcast_text", "")
    await state.clear()

    if not text:
        await call.answer("❌ Aucun message")
        return

    svc = UserService(session)
    users = await svc.get_all_users()

    await call.message.edit_text(
        f"📢 *Diffusion en cours...*\n{len(users)} utilisateurs approuvés",
        parse_mode="Markdown",
    )

    sent = 0
    failed = 0
    for user in users:
        try:
            await bot.send_message(user.telegram_id, text, parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await call.message.edit_text(
        f"✅ *Diffusion terminée*\n\n"
        f"│◉ Envoyé : *{sent}*\n"
        f"│◉ Échecs : *{failed}*",
        parse_mode="Markdown", reply_markup=admin_keyboard()
    )
    logger.info(f"Broadcast by {call.from_user.id}: {sent} ok, {failed} failed")


@router.callback_query(F.data == "admin:broadcast_cancel")
async def cb_broadcast_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ *Diffusion annulée*", parse_mode="Markdown", reply_markup=admin_keyboard()
    )
    await call.answer("❌ Annulée")


# ── Banners ───────────────────────────────────────────────────────────────────

BANNER_KEYS = {
    "menu_banner":        "📋 Menu principal",
    "register_banner":    "📝 Page inscription",
    "game_select_banner": "🎮 Sélection jeu",
    "luckyjet_banner":    "🎯 Lucky Jet",
    "mines_banner":       "💣 Mines",
    "guide_banner":       "📚 Guide",
}


def _banner_keyboard() -> "InlineKeyboardMarkup":
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"admin:set_banner:{key}")]
        for key, label in BANNER_KEYS.items()
    ]
    rows.append([InlineKeyboardButton(text="🔙 Retour", callback_data="admin:stats")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "admin:banners")
async def cb_admin_banners(call: CallbackQuery, session: AsyncSession):
    bss = BotSettingsService(session)
    lines = [f"🖼 *GESTION DES BANNIÈRES*\n\n{SEP}"]
    for key, label in BANNER_KEYS.items():
        val = await bss.get(key)
        status = "✅ Définie" if val else "❌ Non définie"
        lines.append(f"│◉ {label} : {status}")
    lines.append(SEP)
    lines.append("\nAppuie sur une bannière pour la modifier.")
    await call.message.edit_text(
        "\n".join(lines), parse_mode="Markdown", reply_markup=_banner_keyboard()
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin:set_banner:"))
async def cb_set_banner_start(call: CallbackQuery, state: FSMContext):
    key = call.data.split(":", 2)[-1]
    label = BANNER_KEYS.get(key, key)
    await state.set_state(BannerState.waiting_photo)
    await state.update_data(banner_key=key)
    await call.message.edit_text(
        f"🖼 *Modifier la bannière : {label}*\n\n"
        "Envoie une **photo** pour définir cette bannière.\n"
        "Envoie /cancel pour annuler.",
        parse_mode="Markdown",
    )
    await call.answer()


@router.message(BannerState.waiting_photo, F.photo)
async def cb_set_banner_photo(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    key = data.get("banner_key", "menu_banner")
    label = BANNER_KEYS.get(key, key)

    # Use the largest photo size
    file_id = message.photo[-1].file_id
    bss = BotSettingsService(session)
    await bss.set(key, file_id)
    await state.clear()

    await message.answer(
        f"✅ *Bannière mise à jour !*\n\n│◉ Page : *{label}*\n│◉ Photo enregistrée.",
        parse_mode="Markdown",
        reply_markup=admin_keyboard(),
    )
    logger.info(f"Admin {message.from_user.id} updated banner '{key}'")


@router.callback_query(F.data.startswith("admin:del_banner:"))
async def cb_del_banner(call: CallbackQuery, session: AsyncSession):
    key = call.data.split(":", 2)[-1]
    bss = BotSettingsService(session)
    await bss.delete(key)
    await call.answer(f"🗑 Bannière supprimée", show_alert=True)
    # Refresh banners page
    await cb_admin_banners(call, session)


# ── Logs ──────────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin:logs")
async def cb_admin_logs(call: CallbackQuery):
    import os
    log_files = []
    if os.path.exists("logs"):
        log_files = os.listdir("logs")
    text = (
        f"📋 *LOGS*\n\n{SEP}\n"
        f"│◉ Fichiers : {len(log_files)}\n"
        f"{SEP}\n\n"
        "Les logs sont dans `/logs/`"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_keyboard())
    await call.answer()


# ── Cancel ────────────────────────────────────────────────────────────────────

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Action annulée.", reply_markup=admin_keyboard())
