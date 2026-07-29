"""Rocket Queen signal and analysis handlers."""
import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.signals import generate_rocketqueen_signal
from bot.services.user_service import UserService
from bot.utils.formatters import format_rocketqueen_signal, format_countdown
from bot.utils.message_cleaner import schedule_delete
from bot.keyboards.rocketqueen import (
    rocketqueen_menu_keyboard,
    rocketqueen_after_signal_keyboard,
    rocketqueen_after_premium_keyboard,
)
from bot.keyboards.premium import premium_locked_keyboard
from config import settings
from loguru import logger

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


@router.callback_query(F.data.startswith("rq:signal_free:"))
async def cb_rq_free(call: CallbackQuery, session: AsyncSession):
    cote_type = call.data.split(":")[-1]  # "petite" or "grosse"
    user = call.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )

    label = "Petite Cote" if cote_type == "petite" else "Grosse Cote"
    await call.message.edit_text(
        f"⏳ *Chargement du signal Rocket Queen [{label}]...*",
        parse_mode="Markdown",
    )
    await asyncio.sleep(2)

    allowed, remaining = await svc.try_consume_free_signal(db_user)
    if not allowed:
        text = (
            f"⛔ *Limite journalière atteinte*\n\n"
            f"{SEP}\n"
            f"│◉ Limite : *{settings.FREE_SIGNALS_PER_DAY} signaux/jour*\n"
            f"│◉ Renouvellement : minuit UTC\n"
            f"{SEP}\n\n"
            "⭐ Passe en *Premium* pour des signaux illimités !"
        )
        await call.message.edit_text(text, parse_mode="Markdown",
                                     reply_markup=premium_locked_keyboard())
        await call.answer("⛔ Limite atteinte")
        return

    signal = generate_rocketqueen_signal(is_premium=False, cote_type=cote_type)
    await svc.save_signal(user.id, "rocketqueen", signal, is_premium=False)

    text = format_rocketqueen_signal(
        heure=signal["heure"],
        cote=signal["cote"],
        assurance=signal["assurance"],
        cote_type=cote_type,
        promo_code=settings.BOT_PROMO_CODE,
        is_premium=False,
        confidence=signal.get("confidence", 0),
        quality=signal.get("quality", ""),
        trend=signal.get("trend", ""),
        volatilite=signal.get("volatilite", ""),
        force_bar=signal.get("force_bar", ""),
        verification_code=signal.get("verification_code", ""),
        rounds_analysed=signal.get("rounds_analysed", 0),
    )
    text += f"\n\n🎯 Signaux restants : *{remaining}/{settings.FREE_SIGNALS_PER_DAY}*"
    text += f"\n\n{format_countdown(signal['countdown'])}"

    await call.message.edit_text(
        text, parse_mode="Markdown",
        reply_markup=rocketqueen_after_signal_keyboard(settings.BOT_AFFILIATE_LINK, cote_type),
    )

    # Schedule auto-delete 2 minutes after game time
    schedule_delete(call.message.chat.id, call.message.message_id,
                    delete_in_seconds=signal["countdown"] + 120)

    await call.answer("✅ Signal Rocket Queen généré !")
    logger.info(f"Free RQ {cote_type} signal for user {user.id}")


@router.callback_query(F.data.startswith("rq:signal_premium:"))
async def cb_rq_premium(call: CallbackQuery, session: AsyncSession):
    cote_type = call.data.split(":")[-1]
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
            f"🔒 *Signal Premium Rocket Queen — Accès restreint*\n\n"
            f"{SEP}\n"
            f"│◉ Réservé aux membres *Premium*\n"
            f"│◉ Grosses cotes jusqu'à 50x 🚀\n"
            f"│◉ Précision IA maximale\n"
            f"{SEP}\n\n"
            "⭐ Passe Premium pour débloquer !"
        )
        await call.message.edit_text(text, parse_mode="Markdown",
                                     reply_markup=premium_locked_keyboard())
        await call.answer("🔒 Premium requis")
        return

    label = "Petite Cote" if cote_type == "petite" else "Grosse Cote"
    await call.message.edit_text(
        f"⏳ *Chargement du signal Premium Rocket Queen [{label}]...*",
        parse_mode="Markdown",
    )
    await asyncio.sleep(2.5)

    signal = generate_rocketqueen_signal(is_premium=True, cote_type=cote_type)
    await svc.consume_premium_signal(db_user)
    await svc.save_signal(user.id, "rocketqueen", signal, is_premium=True)

    text = format_rocketqueen_signal(
        heure=signal["heure"],
        cote=signal["cote"],
        assurance=signal["assurance"],
        cote_type=cote_type,
        promo_code=settings.BOT_PROMO_CODE,
        is_premium=True,
        confidence=signal.get("confidence", 0),
        quality=signal.get("quality", ""),
        trend=signal.get("trend", ""),
        volatilite=signal.get("volatilite", ""),
        force_bar=signal.get("force_bar", ""),
        verification_code=signal.get("verification_code", ""),
        rounds_analysed=signal.get("rounds_analysed", 0),
    )
    text += f"\n\n{format_countdown(signal['countdown'])}"

    await call.message.edit_text(
        text, parse_mode="Markdown",
        reply_markup=rocketqueen_after_premium_keyboard(settings.BOT_AFFILIATE_LINK, cote_type),
    )

    schedule_delete(call.message.chat.id, call.message.message_id,
                    delete_in_seconds=signal["countdown"] + 120)

    await call.answer("⭐ Signal Premium Rocket Queen généré !")
    logger.info(f"Premium RQ {cote_type} signal for user {user.id}")


@router.callback_query(F.data == "rq:analyse")
async def cb_rq_analyse(call: CallbackQuery):
    await call.message.edit_text("⏳ *Chargement Rocket Queen...*", parse_mode="Markdown")
    await asyncio.sleep(1.5)
    signal = generate_rocketqueen_signal(is_premium=False, cote_type="auto")
    text = (
        f"🚀 *ROCKET QUEEN ANALYSE*\n"
        f"{SEP}\n"
        f"│◉ *Heure prévue* : {signal['heure']} ⏰\n"
        f"│◉ *Cote estimée* : {signal['cote']}\n"
        f"│◉ *Niveau* : {signal['niveau']}\n"
        f"│◉ *Risque* : {signal['risque']} ✅\n"
        f"{SEP}\n"
        f"code promo: `{settings.BOT_PROMO_CODE}`"
    )
    await call.message.edit_text(text, parse_mode="Markdown",
                                 reply_markup=rocketqueen_menu_keyboard())
    await call.answer()


@router.callback_query(F.data == "rq:history")
async def cb_rq_history(call: CallbackQuery, session: AsyncSession):
    from database.models import SignalHistory
    from sqlalchemy import select

    result = await session.execute(
        select(SignalHistory)
        .where(
            SignalHistory.user_id == call.from_user.id,
            SignalHistory.game_type == "rocketqueen",
        )
        .order_by(SignalHistory.created_at.desc())
        .limit(5)
    )
    records = result.scalars().all()

    if not records:
        text = (
            f"📈 *Historique Rocket Queen*\n\n{SEP}\n"
            f"│◉ Aucun signal dans l'historique\n{SEP}\n\n"
            "Lance ton premier signal ! 🚀"
        )
    else:
        lines = [f"📈 *Historique Rocket Queen* (5 derniers)\n{SEP}"]
        for r in records:
            data = r.signal_data
            badge = "⭐" if r.is_premium else "🎯"
            ts = r.created_at.strftime("%d/%m %H:%M")
            ct = data.get("cote_type", "?")
            lines.append(
                f"│{badge} *{ts}* — Cote: {data.get('cote', '?')} [{ct}]"
            )
        lines.append(SEP)
        text = "\n".join(lines)

    await call.message.edit_text(text, parse_mode="Markdown",
                                 reply_markup=rocketqueen_menu_keyboard())
    await call.answer()
