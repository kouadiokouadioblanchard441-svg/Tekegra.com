"""Admin panel handlers."""
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
from bot.utils.formatters import format_admin_stats
from bot.keyboards.admin import admin_keyboard, admin_premium_action_keyboard, admin_confirm_broadcast_keyboard
from config import settings
from loguru import logger

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


class BroadcastState(StatesGroup):
    waiting_message = State()
    confirm = State()


class PremiumManageState(StatesGroup):
    waiting_user_id = State()


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


@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(call: CallbackQuery, session: AsyncSession):
    svc = UserService(session)
    total = await svc.get_total_users()
    premium = await svc.get_premium_users_count()
    active = await svc.get_active_today()
    signals = await svc.get_total_signals()

    text = format_admin_stats(
        total_users=total,
        premium_users=premium,
        active_today=active,
        total_signals=signals,
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_keyboard())
    await call.answer()


@router.callback_query(F.data == "admin:users")
async def cb_admin_users(call: CallbackQuery, session: AsyncSession):
    svc = UserService(session)
    total = await svc.get_total_users()
    premium = await svc.get_premium_users_count()

    text = (
        f"👥 *GESTION UTILISATEURS*\n\n"
        f"{SEP}\n"
        f"│◉ Total : *{total}*\n"
        f"│◉ Premium : *{premium}*\n"
        f"│◉ Gratuits : *{total - premium}*\n"
        f"{SEP}\n\n"
        f"Pour gérer un utilisateur spécifique,\n"
        f"utilisez la commande :\n"
        f"`/admin_user <telegram_id>`"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_keyboard())
    await call.answer()


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

    text = (
        f"👤 *Utilisateur*\n{SEP}\n"
        f"│◉ ID : `{user.telegram_id}`\n"
        f"│◉ Nom : {user.first_name or '—'}\n"
        f"│◉ @{user.username or '—'}\n"
        f"│◉ Premium : {'✅' if user.is_premium else '❌'}\n"
        f"│◉ Analyses : {user.total_analyses}\n"
        f"│◉ Banni : {'🚫' if user.is_banned else '✅ Non'}\n"
        f"{SEP}"
    )
    await message.answer(text, parse_mode="Markdown",
                         reply_markup=admin_premium_action_keyboard(user_id))


@router.callback_query(F.data.startswith("admin:prem_on:"))
async def cb_activate_premium(call: CallbackQuery, session: AsyncSession):
    user_id = int(call.data.split(":")[-1])
    svc = PremiumService(session)
    await svc.activate_premium(user_id, days=30, payment_method="admin")
    await call.message.edit_text(
        f"✅ *Premium activé* (30 jours) pour l'utilisateur `{user_id}`",
        parse_mode="Markdown", reply_markup=admin_keyboard()
    )
    await call.answer("✅ Premium activé")
    logger.info(f"Admin {call.from_user.id} activated premium for {user_id}")


@router.callback_query(F.data.startswith("admin:prem_off:"))
async def cb_deactivate_premium(call: CallbackQuery, session: AsyncSession):
    user_id = int(call.data.split(":")[-1])
    svc = PremiumService(session)
    await svc.deactivate_premium(user_id)
    await call.message.edit_text(
        f"❌ *Premium désactivé* pour l'utilisateur `{user_id}`",
        parse_mode="Markdown", reply_markup=admin_keyboard()
    )
    await call.answer("❌ Premium désactivé")


@router.callback_query(F.data == "admin:broadcast")
async def cb_broadcast_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastState.waiting_message)
    await call.message.edit_text(
        "📢 *Diffusion de message*\n\n"
        "Envoyez le message à diffuser à tous les utilisateurs.\n"
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
        f"📢 *Diffusion en cours...*\n{len(users)} utilisateurs",
        parse_mode="Markdown",
    )

    sent = 0
    failed = 0
    for user in users:
        try:
            await bot.send_message(user.telegram_id, text, parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.05)  # Rate limiting
        except Exception:
            failed += 1

    await call.message.edit_text(
        f"✅ *Diffusion terminée*\n\n"
        f"│◉ Envoyé : *{sent}*\n"
        f"│◉ Échecs : *{failed}*",
        parse_mode="Markdown", reply_markup=admin_keyboard()
    )
    logger.info(f"Broadcast sent by {call.from_user.id}: {sent} success, {failed} failed")


@router.callback_query(F.data == "admin:broadcast_cancel")
async def cb_broadcast_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ *Diffusion annulée*", parse_mode="Markdown", reply_markup=admin_keyboard()
    )
    await call.answer("❌ Annulée")


@router.callback_query(F.data == "admin:logs")
async def cb_admin_logs(call: CallbackQuery):
    import os
    log_files = []
    log_dir = "logs"
    if os.path.exists(log_dir):
        log_files = os.listdir(log_dir)
    text = (
        f"📋 *LOGS*\n\n{SEP}\n"
        f"│◉ Fichiers : {len(log_files)}\n"
        f"{SEP}\n\n"
        "Les logs sont disponibles dans `/logs/`"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=admin_keyboard())
    await call.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Action annulée.", reply_markup=admin_keyboard())
