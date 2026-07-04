"""User profile and history handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.user_service import UserService
from bot.utils.formatters import format_profile
from bot.keyboards.main_menu import back_to_main_keyboard
from config import settings

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"

LANG_NAMES = {
    "fr": "🇫🇷 Français", "en": "🇬🇧 English", "ar": "🇸🇦 العربية",
    "es": "🇪🇸 Español", "ru": "🇷🇺 Русский", "pt": "🇧🇷 Português",
    "tr": "🇹🇷 Türkçe", "hi": "🇮🇳 हिंदी",
}


async def show_profile(event: Message | CallbackQuery, session: AsyncSession):
    user = event.from_user
    svc = UserService(session)
    db_user = await svc.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code,
    )

    max_signals = settings.PREMIUM_SIGNALS_PER_DAY if db_user.is_premium else settings.FREE_SIGNALS_PER_DAY
    lang_name = LANG_NAMES.get(db_user.language_code, db_user.language_code)

    text = format_profile(
        first_name=user.first_name or "Joueur",
        telegram_id=user.id,
        registered_at=db_user.registered_at,
        total_analyses=db_user.total_analyses,
        is_premium=db_user.is_premium,
        language=lang_name,
        signals_today=db_user.free_signals_used_today,
        max_signals=max_signals,
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="Markdown",
                                      reply_markup=back_to_main_keyboard())
        await event.answer()
    else:
        await event.answer(text, parse_mode="Markdown",
                           reply_markup=back_to_main_keyboard())


async def show_history(event: Message | CallbackQuery, session: AsyncSession):
    user = event.from_user
    svc = UserService(session)
    records = await svc.get_history(user.id, limit=10)

    if not records:
        text = (
            f"📈 *Historique des signaux*\n\n"
            f"{SEP}\n"
            f"│◉ Aucun signal dans l'historique\n"
            f"{SEP}\n\n"
            "Génère ton premier signal ! 🚀"
        )
    else:
        lines = [f"📈 *Historique des signaux* (10 derniers)\n{SEP}"]
        for r in records:
            data = r.signal_data
            badge = "⭐" if r.is_premium else "🎯"
            ts = r.created_at.strftime("%d/%m %H:%M")
            game = "🚀 LJ" if r.game_type == "luckyjet" else "💣 Mines"
            if r.game_type == "luckyjet":
                detail = f"Cote: {data.get('cote', '?')}"
            else:
                detail = f"Mines: {data.get('mines', '?')}"
            lines.append(f"│{badge} {game} *{ts}* — {detail}")
        lines.append(SEP)
        text = "\n".join(lines)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="Markdown",
                                      reply_markup=back_to_main_keyboard())
        await event.answer()
    else:
        await event.answer(text, parse_mode="Markdown",
                           reply_markup=back_to_main_keyboard())


@router.callback_query(F.data == "menu:profile")
async def cb_profile(call: CallbackQuery, session: AsyncSession):
    await show_profile(call, session)
