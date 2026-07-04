"""Mines signal and analysis handlers."""
import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.signals import generate_mines_signal
from bot.services.user_service import UserService
from bot.utils.formatters import format_mines_signal, format_countdown
from bot.keyboards.mines import mines_menu_keyboard, mines_after_signal_keyboard
from bot.keyboards.premium import premium_locked_keyboard
from config import settings
from loguru import logger

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


@router.callback_query(F.data == "mines:signal_free")
async def cb_mines_free(call: CallbackQuery, session: AsyncSession):
    user = call.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )

    can_use = await svc.can_use_free_signal(db_user)
    if not can_use:
        text = (
            f"⛔ *Limite journalière atteinte*\n\n"
            f"{SEP}\n"
            f"│◉ Limite : *{settings.FREE_SIGNALS_PER_DAY} signaux/jour*\n"
            f"│◉ Renouvellement : minuit UTC\n"
            f"{SEP}\n\n"
            f"⭐ Passe en *Premium* pour des signaux illimités !"
        )
        await call.message.edit_text(text, parse_mode="Markdown",
                                     reply_markup=premium_locked_keyboard())
        await call.answer("⛔ Limite atteinte")
        return

    await call.message.edit_text("⏳ *Analyse IA Mines en cours...*", parse_mode="Markdown")
    await asyncio.sleep(2)

    signal = generate_mines_signal(is_premium=False)
    remaining = await svc.consume_free_signal(db_user)
    await svc.save_signal(user.id, "mines", signal, is_premium=False)

    text = format_mines_signal(
        mines=signal["mines"],
        niveau=signal["niveau"],
        risque=signal["risque"],
        promo_code=settings.BOT_PROMO_CODE,
        is_premium=False,
    )
    text += f"\n\n│◉ *Cases sûres* : {signal['safe_tiles']} / 25"
    text += f"\n\n🎯 Signaux restants : *{remaining}/{settings.FREE_SIGNALS_PER_DAY}*"
    text += f"\n\n{format_countdown(signal['countdown'])}"

    await call.message.edit_text(
        text, parse_mode="Markdown",
        reply_markup=mines_after_signal_keyboard(settings.BOT_AFFILIATE_LINK),
    )
    await call.answer("✅ Signal Mines généré !")
    logger.info(f"Free Mines signal for user {user.id}")


@router.callback_query(F.data == "mines:signal_premium")
async def cb_mines_premium(call: CallbackQuery, session: AsyncSession):
    user = call.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )

    if not db_user.is_premium:
        text = (
            f"🔒 *Signal Premium Mines — Accès restreint*\n\n"
            f"{SEP}\n"
            f"│◉ Réservé aux membres *Premium*\n"
            f"{SEP}\n\n"
            f"⭐ Avantages : mines réduites, cases sûres optimisées"
        )
        await call.message.edit_text(text, parse_mode="Markdown",
                                     reply_markup=premium_locked_keyboard())
        await call.answer("🔒 Premium requis")
        return

    await call.message.edit_text("⏳ *Analyse IA premium Mines...*", parse_mode="Markdown")
    await asyncio.sleep(2.5)

    signal = generate_mines_signal(is_premium=True)
    await svc.consume_premium_signal(db_user)
    await svc.save_signal(user.id, "mines", signal, is_premium=True)

    text = format_mines_signal(
        mines=signal["mines"],
        niveau=signal["niveau"],
        risque=signal["risque"],
        promo_code=settings.BOT_PROMO_CODE,
        is_premium=True,
    )
    text += f"\n\n│◉ *Cases sûres* : {signal['safe_tiles']} / 25"
    text += f"\n\n{format_countdown(signal['countdown'])}"

    await call.message.edit_text(
        text, parse_mode="Markdown",
        reply_markup=mines_after_signal_keyboard(settings.BOT_AFFILIATE_LINK),
    )
    await call.answer("⭐ Signal Premium Mines généré !")


@router.callback_query(F.data == "mines:analyse")
async def cb_mines_analyse(call: CallbackQuery):
    await call.message.edit_text("⏳ *Analyse IA Mines...*", parse_mode="Markdown")
    await asyncio.sleep(1.5)

    signal = generate_mines_signal(is_premium=False)
    text = (
        f"💣 *MINES ANALYSE*\n"
        f"{SEP}\n"
        f"│◉ *Difficulté* : {signal['mines']} mines 💣\n"
        f"│◉ *Cases sûres* : {signal['safe_tiles']} / 25\n"
        f"│◉ *Niveau conseillé* : {signal['niveau']}\n"
        f"│◉ *Gestion du risque* : {signal['risque']} ✅\n"
        f"{SEP}"
    )
    await call.message.edit_text(text, parse_mode="Markdown",
                                 reply_markup=mines_menu_keyboard())
    await call.answer()


@router.callback_query(F.data == "mines:history")
async def cb_mines_history(call: CallbackQuery, session: AsyncSession):
    from database.models import SignalHistory
    from sqlalchemy import select

    result = await session.execute(
        select(SignalHistory)
        .where(
            SignalHistory.user_id == call.from_user.id,
            SignalHistory.game_type == "mines",
        )
        .order_by(SignalHistory.created_at.desc())
        .limit(5)
    )
    records = result.scalars().all()

    if not records:
        text = (
            f"📈 *Historique Mines*\n\n{SEP}\n"
            f"│◉ Aucun signal dans l'historique\n{SEP}\n\n"
            "Génère ton premier signal ! 💣"
        )
    else:
        lines = [f"📈 *Historique Mines* (5 derniers)\n{SEP}"]
        for r in records:
            data = r.signal_data
            badge = "⭐" if r.is_premium else "🎯"
            ts = r.created_at.strftime("%d/%m %H:%M")
            lines.append(
                f"│{badge} *{ts}* — Mines: {data.get('mines', '?')} | Risque: {data.get('risque', '?')}"
            )
        lines.append(SEP)
        text = "\n".join(lines)

    await call.message.edit_text(text, parse_mode="Markdown",
                                 reply_markup=mines_menu_keyboard())
    await call.answer()
