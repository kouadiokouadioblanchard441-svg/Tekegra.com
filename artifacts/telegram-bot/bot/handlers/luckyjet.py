"""Lucky Jet signal and analysis handlers — with petite/grosse cote and auto-delete."""
import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.signals import generate_luckyjet_signal
from bot.services.user_service import UserService
from bot.utils.formatters import (
    format_luckyjet_signal, format_luckyjet_analysis,
)
from bot.utils.message_cleaner import schedule_delete, delete_previous_signal, track_signal_message
from bot.keyboards.luckyjet import (
    luckyjet_menu_keyboard,
    luckyjet_after_signal_keyboard,
    luckyjet_after_premium_keyboard,
)
from bot.keyboards.premium import premium_locked_keyboard
from config import settings
from loguru import logger

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


# ── Simplified GET SIGNAL (new menu flow) ─────────────────────────────────────
@router.callback_query(F.data == "lj:get_signal")
async def cb_lj_get_signal(call: CallbackQuery, session: AsyncSession):
    """New simplified signal button — auto cote, free or premium."""
    from bot.keyboards.main_menu import luckyjet_after_signal_keyboard
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
    await call.message.edit_text("⏳ *Chargement du signal Lucky Jet...*", parse_mode="Markdown")
    await asyncio.sleep(0.5)

    is_premium = db_user.is_premium

    if is_premium:
        signal = generate_luckyjet_signal(is_premium=True, cote_type="grosse")
        await svc.consume_premium_signal(db_user)
    else:
        allowed, remaining = await svc.try_consume_free_signal(db_user)
        if not allowed:
            text = (
                f"⛔ *Quota gratuit épuisé*\n\n{SEP}\n"
                f"│◉ Tu as utilisé tes *{settings.FREE_SIGNALS_TOTAL} signaux gratuits*\n"
                f"│◉ Passe Premium pour continuer 🚀\n"
                f"{SEP}\n\n⭐ Abonne-toi pour des signaux *illimités* !"
            )
            await call.message.edit_text(text, parse_mode="Markdown",
                                         reply_markup=premium_locked_keyboard())
            await call.answer("⛔ Quota gratuit épuisé")
            return
        signal = generate_luckyjet_signal(is_premium=False, cote_type="auto")

    await svc.save_signal(user.id, "luckyjet", signal, is_premium=is_premium)

    text = format_luckyjet_signal(
        heure=signal["heure"],
        cote=signal["cote"],
        assurance=signal["assurance"],
        promo_code=settings.BOT_PROMO_CODE,
        is_premium=is_premium,
        cote_type=signal.get("cote_type", "auto"),
        mise_seconde=signal.get("mise_seconde", 0.0),
        confidence=signal.get("confidence", 0),
        quality=signal.get("quality", ""),
        trend=signal.get("trend", ""),
        volatilite=signal.get("volatilite", ""),
        force_bar=signal.get("force_bar", ""),
        verification_code=signal.get("verification_code", ""),
        rounds_analysed=signal.get("rounds_analysed", 0),
    )

    await call.message.edit_text(
        text, parse_mode="Markdown",
        reply_markup=luckyjet_after_signal_keyboard(),
    )
    track_signal_message(user.id, call.message.chat.id, call.message.message_id)
    schedule_delete(call.message.chat.id, call.message.message_id, delete_in_seconds=30)
    await call.answer("✅ Signal généré !")
    logger.info(f"LJ get_signal for user {user.id} (premium={is_premium})")


@router.callback_query(F.data.startswith("lj:signal_free:"))
async def cb_free_signal(call: CallbackQuery, session: AsyncSession):
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
    await delete_previous_signal(user.id)
    await call.message.edit_text(
        f"⏳ *Chargement du signal Lucky Jet [{label}]...*",
        parse_mode="Markdown",
    )
    await asyncio.sleep(0.5)

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
        await call.message.edit_text(text, parse_mode="Markdown",
                                     reply_markup=premium_locked_keyboard())
        await call.answer("⛔ Quota gratuit épuisé")
        return

    signal = generate_luckyjet_signal(is_premium=False, cote_type=cote_type)
    await svc.save_signal(user.id, "luckyjet", signal, is_premium=False)

    text = format_luckyjet_signal(
        heure=signal["heure"],
        cote=signal["cote"],
        assurance=signal["assurance"],
        promo_code=settings.BOT_PROMO_CODE,
        is_premium=False,
        cote_type=cote_type,
        mise_seconde=signal.get("mise_seconde", 0.0),
        confidence=signal.get("confidence", 0),
        quality=signal.get("quality", ""),
        trend=signal.get("trend", ""),
        volatilite=signal.get("volatilite", ""),
        force_bar=signal.get("force_bar", ""),
        verification_code=signal.get("verification_code", ""),
        rounds_analysed=signal.get("rounds_analysed", 0),
    )

    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=luckyjet_after_signal_keyboard(settings.BOT_AFFILIATE_LINK, cote_type),
    )

    # Auto-delete 2 minutes after game time
    track_signal_message(user.id, call.message.chat.id, call.message.message_id)
    schedule_delete(call.message.chat.id, call.message.message_id, delete_in_seconds=30)

    await call.answer("✅ Signal généré !")
    logger.info(f"Free LJ {cote_type} signal for user {user.id}")


@router.callback_query(F.data.startswith("lj:signal_premium:"))
async def cb_premium_signal(call: CallbackQuery, session: AsyncSession):
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
            f"🔒 *Signal Premium Lucky Jet — Accès restreint*\n\n"
            f"{SEP}\n"
            f"│◉ Cette fonctionnalité est réservée aux membres *Premium*\n"
            f"│◉ {settings.PREMIUM_SIGNALS_PER_DAY} signaux/jour\n"
            f"│◉ Grosses cotes jusqu'à 25x+ 🚀\n"
            f"│◉ Analyses IA avancées\n"
            f"{SEP}"
        )
        await call.message.edit_text(
            text, parse_mode="Markdown",
            reply_markup=premium_locked_keyboard(),
        )
        await call.answer("🔒 Premium requis")
        return

    label = "Petite Cote" if cote_type == "petite" else "Grosse Cote"
    await delete_previous_signal(user.id)
    await call.message.edit_text(
        f"⏳ *Chargement du signal Premium Lucky Jet [{label}]...*",
        parse_mode="Markdown",
    )
    await asyncio.sleep(0.5)

    signal = generate_luckyjet_signal(is_premium=True, cote_type=cote_type)
    await svc.consume_premium_signal(db_user)
    await svc.save_signal(user.id, "luckyjet", signal, is_premium=True)

    text = format_luckyjet_signal(
        heure=signal["heure"],
        cote=signal["cote"],
        assurance=signal["assurance"],
        promo_code=settings.BOT_PROMO_CODE,
        is_premium=True,
        cote_type=cote_type,
        mise_seconde=signal.get("mise_seconde", 0.0),
        confidence=signal.get("confidence", 0),
        quality=signal.get("quality", ""),
        trend=signal.get("trend", ""),
        volatilite=signal.get("volatilite", ""),
        force_bar=signal.get("force_bar", ""),
        verification_code=signal.get("verification_code", ""),
        rounds_analysed=signal.get("rounds_analysed", 0),
    )

    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=luckyjet_after_premium_keyboard(settings.BOT_AFFILIATE_LINK, cote_type),
    )

    track_signal_message(user.id, call.message.chat.id, call.message.message_id)
    schedule_delete(call.message.chat.id, call.message.message_id, delete_in_seconds=30)

    await call.answer("⭐ Signal Premium généré !")
    logger.info(f"Premium LJ {cote_type} signal for user {user.id}")


@router.callback_query(F.data == "lj:analyse")
async def cb_analyse(call: CallbackQuery):
    await call.message.edit_text("⏳ *Chargement Lucky Jet...*", parse_mode="Markdown")
    await asyncio.sleep(0.5)

    signal = generate_luckyjet_signal(is_premium=False, cote_type="auto")
    text = format_luckyjet_analysis(
        heure=signal["heure"],
        niveau=signal["niveau"],
        risque=signal["risque"],
    )
    await call.message.edit_text(
        text, parse_mode="Markdown",
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
            ct = data.get("cote_type", "auto")
            lines.append(
                f"│{badge} *{ts}* — {data.get('cote', '?')} [{ct}]"
            )
        lines.append(SEP)
        text = "\n".join(lines)

    await call.message.edit_text(
        text, parse_mode="Markdown",
        reply_markup=luckyjet_menu_keyboard(),
    )
    await call.answer()
