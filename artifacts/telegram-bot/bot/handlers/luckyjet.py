"""Lucky Jet signal and analysis handlers."""
import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.signals import generate_luckyjet_signal
from bot.services.user_service import UserService
from bot.utils.formatters import (
    format_luckyjet_signal, format_luckyjet_analysis, format_countdown
)
from bot.keyboards.luckyjet import (
    luckyjet_menu_keyboard, luckyjet_after_signal_keyboard, luckyjet_after_premium_keyboard
)
from bot.keyboards.premium import premium_locked_keyboard
from config import settings
from loguru import logger

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


@router.callback_query(F.data == "lj:signal_free")
async def cb_free_signal(call: CallbackQuery, session: AsyncSession):
    user = call.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )

    # Check daily limit
    can_use = await svc.can_use_free_signal(db_user)
    if not can_use:
        text = (
            f"⛔ *Limite journalière atteinte*\n\n"
            f"{SEP}\n"
            f"│◉ Tu as utilisé tous tes signaux gratuits\n"
            f"│◉ Limite : *{settings.FREE_SIGNALS_PER_DAY} signaux/jour*\n"
            f"│◉ Renouvellement : minuit UTC\n"
            f"{SEP}\n\n"
            f"⭐ Passe en *Premium* pour des signaux illimités !"
        )
        from bot.keyboards.premium import premium_locked_keyboard
        await call.message.edit_text(text, parse_mode="Markdown",
                                     reply_markup=premium_locked_keyboard())
        await call.answer("⛔ Limite atteinte")
        return

    # Show loading animation
    await call.message.edit_text("⏳ *Analyse IA en cours...*", parse_mode="Markdown")
    await asyncio.sleep(2)

    signal = generate_luckyjet_signal(is_premium=False)
    remaining = await svc.consume_free_signal(db_user)
    await svc.save_signal(user.id, "luckyjet", signal, is_premium=False)

    text = format_luckyjet_signal(
        heure=signal["heure"],
        cote=signal["cote"],
        assurance=signal["assurance"],
        promo_code=settings.BOT_PROMO_CODE,
        is_premium=False,
    )
    text += f"\n\n🎯 Signaux restants aujourd'hui : *{remaining}/{settings.FREE_SIGNALS_PER_DAY}*"
    text += f"\n\n{format_countdown(signal['countdown'])}"

    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=luckyjet_after_signal_keyboard(settings.BOT_AFFILIATE_LINK),
    )
    await call.answer("✅ Signal généré !")
    logger.info(f"Free LJ signal generated for user {user.id}")


@router.callback_query(F.data == "lj:signal_premium")
async def cb_premium_signal(call: CallbackQuery, session: AsyncSession):
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
            f"🔒 *Signal Premium — Accès restreint*\n\n"
            f"{SEP}\n"
            f"│◉ Cette fonctionnalité est réservée\n"
            f"│   aux membres *Premium*\n"
            f"{SEP}\n\n"
            f"⭐ Avantages Premium :\n"
            f"│◉ {settings.PREMIUM_SIGNALS_PER_DAY} signaux/jour\n"
            f"│◉ Cotes ultra-élevées (jusqu'à 25x+)\n"
            f"│◉ Analyses IA avancées\n"
            f"│◉ Priorité de traitement"
        )
        await call.message.edit_text(
            text, parse_mode="Markdown",
            reply_markup=premium_locked_keyboard(),
        )
        await call.answer("🔒 Premium requis")
        return

    # Show premium loading
    await call.message.edit_text(
        "⏳ *Analyse IA premium en cours...*", parse_mode="Markdown"
    )
    await asyncio.sleep(2.5)

    signal = generate_luckyjet_signal(is_premium=True)
    await svc.consume_premium_signal(db_user)
    await svc.save_signal(user.id, "luckyjet", signal, is_premium=True)

    text = format_luckyjet_signal(
        heure=signal["heure"],
        cote=signal["cote"],
        assurance=signal["assurance"],
        promo_code=settings.BOT_PROMO_CODE,
        is_premium=True,
    )
    text += f"\n\n{format_countdown(signal['countdown'])}"

    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=luckyjet_after_premium_keyboard(settings.BOT_AFFILIATE_LINK),
    )
    await call.answer("⭐ Signal Premium généré !")
    logger.info(f"Premium LJ signal generated for user {user.id}")


@router.callback_query(F.data == "lj:analyse")
async def cb_analyse(call: CallbackQuery, session: AsyncSession):
    await call.message.edit_text("⏳ *Analyse IA en cours...*", parse_mode="Markdown")
    await asyncio.sleep(1.5)

    signal = generate_luckyjet_signal(is_premium=False)
    text = format_luckyjet_analysis(
        heure=signal["heure"],
        niveau=signal["niveau"],
        risque=signal["risque"],
    )
    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=luckyjet_menu_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "lj:history")
async def cb_history(call: CallbackQuery, session: AsyncSession):
    svc = UserService(session)
    records = await svc.get_history(call.from_user.id, limit=5)

    if not records:
        text = (
            f"📈 *Historique Lucky Jet*\n\n"
            f"{SEP}\n"
            f"│◉ Aucun signal dans l'historique\n"
            f"{SEP}\n\n"
            "Génère ton premier signal ! 🚀"
        )
    else:
        lines = [f"📈 *Historique Lucky Jet* (5 derniers)\n{SEP}"]
        for r in records:
            data = r.signal_data
            badge = "⭐" if r.is_premium else "🎯"
            ts = r.created_at.strftime("%d/%m %H:%M")
            lines.append(
                f"│{badge} *{ts}* — Cote: {data.get('cote', '?')} | Assurance: {data.get('assurance', '?')}"
            )
        lines.append(SEP)
        text = "\n".join(lines)

    await call.message.edit_text(
        text, parse_mode="Markdown",
        reply_markup=luckyjet_menu_keyboard(),
    )
    await call.answer()
