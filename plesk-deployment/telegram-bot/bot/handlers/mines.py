"""Mines signal handlers — signals sent as new messages, deleted on next request."""
import asyncio
from pathlib import Path
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

_MINES_IMAGE = Path(__file__).parent.parent / "assets" / "mines.jpg"

from bot.services.signals import generate_mines_signal
from bot.services.user_service import UserService
from bot.services.settings_service import get_affiliate_link
from bot.utils.formatters import format_mines_signal, format_countdown
from bot.utils.message_cleaner import (
    delete_previous_signal,
    is_tracked_message,
    track_existing_message,
    track_signal_message,
    schedule_delete,
)
from bot.utils.cooldown import (
    get_cooldown_remaining,
    record_signal,
    format_cooldown_message,
)
from bot.keyboards.mines import (
    mines_menu_keyboard,
    mines_after_signal_keyboard,
    mines_choose_keyboard,
    mines_premium_type_keyboard,
)
from bot.keyboards.mines_grid import mines_grid_keyboard
from bot.keyboards.premium import premium_locked_keyboard
from config import settings
from loguru import logger

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


def _render_grid_text(grid: list[list[str]]) -> str:
    rows = []
    for row in grid:
        cells = []
        for cell in row:
            if cell == "⭐":
                cells.append("⭐")
            else:
                cells.append("🟦")
        rows.append("".join(cells))
    return "\n".join(rows)


def _grid_header(signal: dict, is_premium: bool, remaining: int | None = None) -> str:
    badge = "⭐ PREMIUM" if is_premium else "🎯 GRATUIT"
    grid_text = _render_grid_text(signal.get("grid", []))
    lines = [
        f"🎯 *MINES PREDICTION* [{badge}]",
        SEP,
        f"|●>*HEURE : {signal['heure']}* ⏰",
        f"|●>*PIÈGES : 3 mines* 💣",
        f"|●>*RISQUE : {signal['risque']}* ⚠️",
        f"|●>*CONFIANCE : {signal['confidence']}%* 🎯",
        SEP,
        "",
        grid_text,
        "",
    ]
    if is_premium and signal.get("star_mode") in ("petite", "grosse"):
        mode_label = (
            "🎯 Petite"
            if signal["star_mode"] == "petite"
            else "🚀 Grosse"
        )
        lines.insert(
            5,
            f"|●>*MODE : {mode_label} — "
            f"{signal.get('star_count', 0)} étoiles* ⭐",
        )
    if remaining is not None and not is_premium:
        lines.append(f"🎯 Signaux gratuits restants : *{remaining}/{settings.FREE_SIGNALS_TOTAL}*")
    lines.append(f"🎁 code promo: *{settings.BOT_PROMO_CODE}*")
    return "\n".join(lines)


async def _send_mines_signal(
    call: CallbackQuery,
    signal: dict,
    is_premium: bool,
    remaining: int | None = None,
    star_mode: str = "auto",
    affiliate_link: str = "",
) -> None:
    """Send the Mines image with a loading caption, then edit it to the final grid."""
    # The previous response can be a menu or an older signal. Remove it before
    # creating the loading/final message so two bot messages cannot coexist.
    trigger_was_tracked = is_tracked_message(call.from_user.id, call.message)
    await delete_previous_signal(call.from_user.id)
    try:
        if not trigger_was_tracked:
            await call.message.delete()
    except Exception:
        pass

    loading = await call.message.answer_photo(
        photo=FSInputFile(_MINES_IMAGE),
        caption="⏳ *Analyse de la grille...*",
        parse_mode="Markdown",
    )
    # Track the loading message immediately so it cannot become orphaned if
    # Telegram or the process fails before the final grid edit.
    track_signal_message(call.from_user.id, loading.chat.id, loading.message_id)
    schedule_delete(loading.chat.id, loading.message_id)
    await asyncio.sleep(0.15)

    header = _grid_header(signal, is_premium, remaining)
    keyboard = mines_grid_keyboard(
        grid=signal.get("grid", []),
        is_premium=is_premium,
        affiliate_link=affiliate_link,
        star_mode=signal.get("star_mode", star_mode),
    )
    try:
        await loading.edit_caption(
            caption=header,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    except Exception:
        # Loading was deleted by a concurrent callback — send a fresh photo.
        try:
            sent = await call.message.answer_photo(
                photo=FSInputFile(_MINES_IMAGE),
                caption=header,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
            track_signal_message(call.from_user.id, sent.chat.id, sent.message_id)
            schedule_delete(sent.chat.id, sent.message_id)
        except Exception:
            pass


# ── Écran de choix : Gratuit ou Premium ───────────────────────────────────────
@router.callback_query(F.data == "mines:choose_type")
async def cb_mines_choose_type(call: CallbackQuery, session: AsyncSession):
    user = call.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )
    remaining = settings.FREE_SIGNALS_TOTAL - db_user.free_signals_used_total
    remaining = max(0, remaining)

    text = (
        "💣 *MINES — Choisissez votre signal*\n\n"
        f"{SEP}\n"
        f"│◉ Signaux gratuits restants : *{remaining}/{settings.FREE_SIGNALS_TOTAL}*\n"
        f"│◉ Premium : signaux *illimités* ⭐\n"
        f"{SEP}\n\n"
        "👇 Sélectionnez le type de signal :"
    )
    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=mines_choose_keyboard(remaining, settings.FREE_SIGNALS_TOTAL),
    )
    await track_existing_message(user.id, call.message)
    await call.answer()


# ── Simplified GET SIGNAL ─────────────────────────────────────────────────────
@router.callback_query(F.data == "mines:get_signal")
async def cb_mines_get_signal(call: CallbackQuery, session: AsyncSession):
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
    is_premium = db_user.is_premium

    if is_premium:
        await call.message.edit_text(
            "💣 *MINES PREMIUM*\n\n"
            f"{SEP}\n\n"
            "Choisissez le mode d'étoiles :",
            parse_mode="Markdown",
            reply_markup=mines_premium_type_keyboard(),
        )
        await track_existing_message(user.id, call.message)
        await call.answer()
        return
    else:
        # Cooldown check — free users only
        wait = get_cooldown_remaining(user.id)
        if wait > 0:
            text = format_cooldown_message(wait)
            await call.message.edit_text(text, parse_mode="Markdown",
                                         reply_markup=mines_menu_keyboard())
            await track_existing_message(user.id, call.message)
            await call.answer("⏳ Attends encore un moment")
            return

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
            await track_existing_message(user.id, call.message)
            await call.answer("⛔ Quota gratuit épuisé")
            return
        signal = generate_mines_signal(is_premium=False)
        record_signal(user.id)

    await svc.save_signal(user.id, "mines", signal, is_premium=is_premium)
    affiliate_link = await get_affiliate_link(session, settings.BOT_AFFILIATE_LINK)
    await _send_mines_signal(
        call,
        signal,
        is_premium=is_premium,
        affiliate_link=affiliate_link,
    )
    await call.answer("✅ Grille générée !")
    logger.info(f"Mines get_signal for user {user.id} (premium={is_premium})")


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

    await delete_previous_signal(user.id)

    # Cooldown check — free users only
    wait = get_cooldown_remaining(user.id)
    if wait > 0:
        text = format_cooldown_message(wait)
        try:
            await call.message.edit_text(text, parse_mode="Markdown",
                                         reply_markup=mines_menu_keyboard())
            await track_existing_message(user.id, call.message)
        except Exception:
            from bot.utils.message_cleaner import send_tracked_message
            await send_tracked_message(call.message, user.id, text,
                                       parse_mode="Markdown",
                                       reply_markup=mines_menu_keyboard())
        await call.answer("⏳ Attends encore un moment")
        return

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
            await send_tracked_message(call.message, user.id, text,
                                       parse_mode="Markdown",
                                       reply_markup=premium_locked_keyboard())
        await call.answer("⛔ Quota gratuit épuisé")
        return

    signal = generate_mines_signal(is_premium=False)
    record_signal(user.id)
    await svc.save_signal(user.id, "mines", signal, is_premium=False)
    affiliate_link = await get_affiliate_link(session, settings.BOT_AFFILIATE_LINK)
    await _send_mines_signal(
        call,
        signal,
        is_premium=False,
        remaining=remaining,
        affiliate_link=affiliate_link,
    )
    await call.answer("✅ Grille Mines générée !")
    logger.info(f"Free Mines grid for user {user.id} — {signal['mines']} mines")


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
            f"│◉ Plus de cases ⭐ révélées (5 vs 3)\n"
            f"│◉ Moins de pièges, plus de gains\n"
            f"{SEP}\n\n"
            "⭐ Passe Premium pour débloquer !"
        )
        try:
            await call.message.edit_text(text, parse_mode="Markdown",
                                         reply_markup=premium_locked_keyboard())
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

    await call.message.edit_text(
        "💣 *MINES PREMIUM*\n\n"
        f"{SEP}\n\n"
        "Choisissez le mode d'étoiles :",
        parse_mode="Markdown",
        reply_markup=mines_premium_type_keyboard(),
    )
    await track_existing_message(user.id, call.message)
    await call.answer()
    return


@router.callback_query(F.data.startswith("mines:signal_premium:"))
async def cb_mines_premium_type(call: CallbackQuery, session: AsyncSession):
    star_mode = call.data.split(":")[-1]
    if star_mode not in ("petite", "grosse"):
        await call.answer("❌ Mode d'étoiles invalide", show_alert=True)
        return

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
        await call.answer("🔒 Premium requis", show_alert=True)
        return

    await delete_previous_signal(user.id)

    signal = generate_mines_signal(is_premium=True, star_mode=star_mode)
    await svc.consume_premium_signal(db_user)
    await svc.save_signal(user.id, "mines", signal, is_premium=True)
    affiliate_link = await get_affiliate_link(session, settings.BOT_AFFILIATE_LINK)
    await _send_mines_signal(
        call,
        signal,
        is_premium=True,
        affiliate_link=affiliate_link,
    )
    await call.answer("⭐ Grille Premium Mines générée !")
    logger.info(
        f"Premium Mines {star_mode} grid for user {user.id} — "
        f"{signal['mines']} mines"
    )


# Tap on a cell — just acknowledge
@router.callback_query(F.data.startswith("mines:cell:"))
async def cb_cell_tap(call: CallbackQuery):
    parts = call.data.split(":")
    cell_type = parts[3] if len(parts) > 3 else "🟦"
    if cell_type == "⭐":
        await call.answer("⭐ Case sûre — Clique ici !", show_alert=False)
    elif cell_type == "💣":
        await call.answer("⚠️ Case dangereuse — Évite cette case !", show_alert=True)
    else:
        await call.answer("🟦 Case inconnue", show_alert=False)


@router.callback_query(F.data == "mines:analyse")
async def cb_mines_analyse(call: CallbackQuery, session: AsyncSession):
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
        await call.message.edit_text(text, parse_mode="Markdown",
                                     reply_markup=premium_locked_keyboard())
        await track_existing_message(user.id, call.message)
        await call.answer("⛔ Quota gratuit épuisé")
        return

    signal = generate_mines_signal(is_premium=False)
    affiliate_link = await get_affiliate_link(session, settings.BOT_AFFILIATE_LINK)
    await _send_mines_signal(
        call,
        signal,
        is_premium=False,
        affiliate_link=affiliate_link,
    )
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
            "Génère ta première grille ! 💣"
        )
    else:
        lines = [f"📈 *Historique Mines* (5 derniers)\n{SEP}"]
        for r in records:
            data = r.signal_data
            badge = "⭐" if r.is_premium else "🎯"
            ts = r.created_at.strftime("%d/%m %H:%M")
            star_mode = data.get("star_mode")
            mode_label = (
                f" | 🎯 Petite — {data.get('star_count', '?')} étoiles"
                if star_mode == "petite"
                else f" | 🚀 Grosse — {data.get('star_count', '?')} étoiles"
                if star_mode == "grosse"
                else ""
            )
            lines.append(
                f"│{badge} *{ts}* — {data.get('mines', '?')} mines | "
                f"Risque: {data.get('risque', '?')}{mode_label}"
            )
        lines.append(SEP)
        text = "\n".join(lines)

    await call.message.edit_text(text, parse_mode="Markdown",
                                 reply_markup=mines_menu_keyboard())
    await track_existing_message(call.from_user.id, call.message)
    await call.answer()
