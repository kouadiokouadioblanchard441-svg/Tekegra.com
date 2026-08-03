"""Rocket Queen signal handlers — signals sent as new messages, deleted on next request."""
import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.signals import generate_rocketqueen_signal
from bot.services.user_service import UserService
from bot.services.settings_service import get_affiliate_link
from bot.utils.formatters import format_rocketqueen_signal, format_countdown
from bot.utils.message_cleaner import (
    delete_previous_signal,
    is_tracked_message,
    track_existing_message,
    track_signal_message,
    schedule_delete,
)
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


async def _send_signal_message(call: CallbackQuery, text: str, keyboard) -> None:
    """Delete trigger message, send loading, then edit to final signal."""
    trigger_was_tracked = is_tracked_message(call.from_user.id, call.message)
    await delete_previous_signal(call.from_user.id)
    if not trigger_was_tracked:
        try:
            await call.message.delete()
        except Exception:
            pass
    loading = await call.message.answer("⏳ *Analyse en cours...*", parse_mode="Markdown")
    track_signal_message(call.from_user.id, loading.chat.id, loading.message_id)
    schedule_delete(loading.chat.id, loading.message_id)
    await asyncio.sleep(0.15)
    await loading.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(F.data.startswith("rq:signal_free:"))
async def cb_rq_free(call: CallbackQuery, session: AsyncSession):
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

    await delete_previous_signal(user.id)

    allowed, remaining = await svc.try_consume_free_signal(db_user)
    if not allowed:
        text = (
            f"⛔ *Quota gratuit épuisé*\n\n"
            f"{SEP}\n"
            f"│◉ Tu as utilisé tes *{settings.FREE_SIGNALS_TOTAL} signaux gratuits*\n"
            f"│◉ Passe Premium pour continuer 🚀\n"
            f"{SEP}\n\n"
            "⭐ Abonne-toi pour des signaux *illimités* !"
        )
        try:
            await call.message.edit_text(text, parse_mode="Markdown",
                                         reply_markup=premium_locked_keyboard())
            await track_existing_message(user.id, call.message)
        except Exception:
            from bot.utils.message_cleaner import send_tracked_message
            await send_tracked_message(
                call.message,
                user.id,
                text,
                parse_mode="Markdown",
                reply_markup=premium_locked_keyboard(),
            )
        await call.answer("⛔ Quota gratuit épuisé")
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
    text += f"\n\n🎯 Signaux gratuits restants : *{remaining}/{settings.FREE_SIGNALS_TOTAL}*"
    text += f"\n\n{format_countdown(signal['countdown'])}"

    await _send_signal_message(
        call, text,
        rocketqueen_after_signal_keyboard(
            await get_affiliate_link(session, settings.BOT_AFFILIATE_LINK),
            cote_type,
        ),
    )
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
        try:
            await call.message.edit_text(text, parse_mode="Markdown",
                                         reply_markup=premium_locked_keyboard())
            await track_existing_message(user.id, call.message)
        except Exception:
            from bot.utils.message_cleaner import send_tracked_message
            await send_tracked_message(
                call.message,
                user.id,
                text,
                parse_mode="Markdown",
                reply_markup=premium_locked_keyboard(),
            )
        await call.answer("🔒 Premium requis")
        return

    await delete_previous_signal(user.id)

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

    await _send_signal_message(
        call, text,
        rocketqueen_after_premium_keyboard(
            await get_affiliate_link(session, settings.BOT_AFFILIATE_LINK),
            cote_type,
        ),
    )
    await call.answer("⭐ Signal Premium Rocket Queen généré !")
    logger.info(f"Premium RQ {cote_type} signal for user {user.id}")


@router.callback_query(F.data == "rq:analyse")
async def cb_rq_analyse(call: CallbackQuery, session: AsyncSession):
    user = call.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )
    if not db_user.is_premium and db_user.free_signals_used_total >= settings.FREE_SIGNALS_TOTAL:
        text = (
            f"⛔ *Quota gratuit épuisé*\n\n{SEP}\n"
            f"│◉ Tu as utilisé tes *{settings.FREE_SIGNALS_TOTAL} signaux gratuits*\n"
            f"│◉ Passe Premium pour continuer 🚀\n"
            f"{SEP}\n\n⭐ Abonne-toi pour des signaux *illimités* !"
        )
        try:
            await call.message.edit_text(text, parse_mode="Markdown",
                                         reply_markup=premium_locked_keyboard())
        except Exception:
            from bot.utils.message_cleaner import send_tracked_message
            await send_tracked_message(call.message, user.id, text,
                                       parse_mode="Markdown",
                                       reply_markup=premium_locked_keyboard())
        await call.answer("⛔ Quota gratuit épuisé")
        return

    await call.message.edit_text("⏳ *Chargement Rocket Queen...*", parse_mode="Markdown")
    await asyncio.sleep(0.15)
    signal = generate_rocketqueen_signal(is_premium=False, cote_type="auto")
    text = (
        f"🚀 *ROCKET QUEEN ANALYSE*\n"
        f"{SEP}\n"
        f"│◉ *Heure prévue* : {signal['heure']} ⏰\n"
        f"│◉ *Cote estimée* : {signal['cote']}\n"
        f"│◉ *Niveau* : {signal['niveau']}\n"
        f"│◉ *Risque* : {signal['risque']} ✅\n"
        f"{SEP}\n"
        f"code promo: *{settings.BOT_PROMO_CODE}*"
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
