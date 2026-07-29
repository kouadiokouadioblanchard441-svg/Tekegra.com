"""Mines signal and analysis handlers — with interactive 5×5 grid."""
import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.signals import generate_mines_signal
from bot.services.user_service import UserService
from bot.utils.formatters import format_mines_signal, format_countdown
from bot.keyboards.mines import mines_menu_keyboard, mines_after_signal_keyboard
from bot.keyboards.mines_grid import mines_grid_keyboard
from bot.keyboards.premium import premium_locked_keyboard
from config import settings
from loguru import logger

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


# ── Simplified GET SIGNAL (new menu flow) ─────────────────────────────────────
@router.callback_query(F.data == "mines:get_signal")
async def cb_mines_get_signal(call: CallbackQuery, session: AsyncSession):
    """New simplified mines signal button."""
    user = call.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )

    await call.message.edit_text("⏳ *Chargement du signal Mines...*", parse_mode="Markdown")
    await asyncio.sleep(2)

    is_premium = db_user.is_premium

    if is_premium:
        signal = generate_mines_signal(is_premium=True)
        await svc.consume_premium_signal(db_user)
    else:
        allowed, remaining = await svc.try_consume_free_signal(db_user)
        if not allowed:
            text = (
                f"⛔ *Limite journalière atteinte*\n\n{SEP}\n"
                f"│◉ Limite : *{settings.FREE_SIGNALS_PER_DAY} signaux/jour*\n"
                "│◉ Renouvellement : minuit UTC\n"
                f"{SEP}\n\n⭐ Passe en *Premium* pour des signaux illimités !"
            )
            await call.message.edit_text(text, parse_mode="Markdown",
                                         reply_markup=premium_locked_keyboard())
            await call.answer("⛔ Limite atteinte")
            return

    await svc.save_signal(user.id, "mines", signal, is_premium=is_premium)
    await _show_mines_grid(call, signal, is_premium=is_premium)
    await call.answer("✅ Grille générée !")
    logger.info(f"Mines get_signal for user {user.id} (premium={is_premium})")


def _render_grid_text(grid: list[list[str]]) -> str:
    """Render the 5×5 grid as compact text. ⭐ stays visible, mines hidden as ▫️."""
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
        f"|●>*PIÈGES : {signal['mines']} mines* 💣",
        f"|●>*RISQUE : {signal['risque']}* ⚠️",
        f"|●>*CONFIANCE : {signal['confidence']}%* 🎯",
        SEP,
        "",
        grid_text,
        "",
    ]
    if remaining is not None and not is_premium:
        lines.append(f"🎯 Signaux restants : *{remaining}/{settings.FREE_SIGNALS_PER_DAY}*")
    lines.append(f"🎁 code promo: `{settings.BOT_PROMO_CODE}`")
    return "\n".join(lines)


async def _show_mines_grid(
    call: CallbackQuery,
    signal: dict,
    is_premium: bool,
    remaining: int | None = None,
):
    """Send the analysis header then edit into the 5×5 grid keyboard."""
    header = _grid_header(signal, is_premium, remaining)
    grid = signal.get("grid", [])
    keyboard = mines_grid_keyboard(
        grid=grid,
        is_premium=is_premium,
        affiliate_link=settings.BOT_AFFILIATE_LINK,
    )
    await call.message.edit_text(header, parse_mode="Markdown", reply_markup=keyboard)


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

    await call.message.edit_text("⏳ *Chargement du signal Mines...*", parse_mode="Markdown")
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

    signal = generate_mines_signal(is_premium=False)
    await svc.save_signal(user.id, "mines", signal, is_premium=False)
    await _show_mines_grid(call, signal, is_premium=False, remaining=remaining)
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
        await call.message.edit_text(text, parse_mode="Markdown",
                                     reply_markup=premium_locked_keyboard())
        await call.answer("🔒 Premium requis")
        return

    await call.message.edit_text("⏳ *Chargement du signal Premium Mines...*", parse_mode="Markdown")
    await asyncio.sleep(2.5)

    signal = generate_mines_signal(is_premium=True)
    await svc.consume_premium_signal(db_user)
    await svc.save_signal(user.id, "mines", signal, is_premium=True)
    await _show_mines_grid(call, signal, is_premium=True)
    await call.answer("⭐ Grille Premium Mines générée !")
    logger.info(f"Premium Mines grid for user {user.id} — {signal['mines']} mines")


# Tap on a cell — just acknowledge, grid is read-only prediction display
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
async def cb_mines_analyse(call: CallbackQuery):
    await call.message.edit_text("⏳ *Chargement Mines...*", parse_mode="Markdown")
    await asyncio.sleep(1.5)

    signal = generate_mines_signal(is_premium=False)
    await _show_mines_grid(call, signal, is_premium=False)
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
            lines.append(
                f"│{badge} *{ts}* — {data.get('mines', '?')} mines | Risque: {data.get('risque', '?')}"
            )
        lines.append(SEP)
        text = "\n".join(lines)

    await call.message.edit_text(text, parse_mode="Markdown",
                                 reply_markup=mines_menu_keyboard())
    await call.answer()
