"""Premium subscription handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.premium_service import PremiumService
from bot.services.user_service import UserService
from bot.services.settings_service import BotSettingsService
from bot.keyboards.premium import premium_keyboard
from bot.keyboards.main_menu import back_to_main_keyboard
from bot.utils.message_cleaner import (
    delete_incoming_message,
    send_tracked_message,
    track_existing_message,
)
from config import settings

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


def _format_fcfa(amount: int) -> str:
    """Formate un montant en FCFA avec séparateur de milliers."""
    return f"{amount:,} F".replace(",", " ")


async def _get_prices(session: AsyncSession) -> tuple[str, str]:
    """Lit les prix depuis la DB. Retourne (prix_7j, prix_30j) formatés en FCFA."""
    svc = BotSettingsService(session)
    p7  = int(await svc.get("price_7_days_fcfa",  "5594"))
    p30 = int(await svc.get("price_30_days_fcfa", "16794"))
    return _format_fcfa(p7), _format_fcfa(p30)


async def show_premium(event: Message | CallbackQuery, session: AsyncSession | None = None):
    price_7, price_30 = ("5 594 F", "16 794 F")
    if session is not None:
        price_7, price_30 = await _get_prices(session)

    text = (
        "🏆 *PASSE PREMIUM*\n"
        f"{SEP}\n\n"
        "✅ *Ce qui est inclus :*\n\n"
        "│ 🎯 Signaux *illimités* — 24h/24\n"
        "│ 📈 Cotes ultra-élevées jusqu'à *25x+*\n"
        "│ 🤖 Analyses IA *avancées*\n"
        "│ 💎 Lucky Jet *+* Mines débloqués\n"
        "│ ⚡ Traitement *prioritaire*\n"
        "│ 🎧 Support *dédié*\n\n"
        f"{SEP}\n\n"
        f"💰 *7 jours* ➜ {price_7}\n"
        f"💰 *30 jours* ➜ {price_30}\n\n"
        f"🎁 Code promo : *{settings.BOT_PROMO_CODE}*"
    )
    kb = premium_keyboard(price_7, price_30)
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
        await event.answer()
    else:
        await delete_incoming_message(event)
        await send_tracked_message(
            event,
            event.from_user.id,
            text,
            parse_mode="Markdown",
            reply_markup=kb,
        )


@router.callback_query(F.data.startswith("premium:buy_"))
async def cb_buy_premium(call: CallbackQuery, session: AsyncSession):
    days = call.data.split("_")[-1]

    svc = BotSettingsService(session)
    price_7_raw  = int(await svc.get("price_7_days_fcfa",  "5594"))
    price_30_raw = int(await svc.get("price_30_days_fcfa", "16794"))
    price_7  = _format_fcfa(price_7_raw)
    price_30 = _format_fcfa(price_30_raw)
    price = price_7 if days == "7" else price_30

    # Support username — configurable via admin panel
    support_raw = await svc.get("support_username", "JRYV14")
    support_username = support_raw if support_raw.startswith("@") else f"@{support_raw}"

    user_tag = f"@{call.from_user.username}" if call.from_user.username else "_(pas de pseudo)_"

    text = (
        f"⭐ *ACTIVATION PREMIUM — {days} JOURS*\n"
        f"{SEP}\n"
        f"│ ⏳ Durée : *{days} jours*\n"
        f"│ 💰 Prix : *{price}*\n"
        f"│ 🚀 Signaux illimités inclus\n"
        f"{SEP}\n\n"
        f"📋 *Étapes pour activer :*\n\n"
        f"*1️⃣* Contactez *{support_username}* sur Telegram\n"
        f"*2️⃣* Envoyez votre *ID Telegram* ci-dessous\n"
        f"*3️⃣* Effectuez le paiement de *{price}*\n"
        f"*4️⃣* Votre accès Premium est activé ✅\n\n"
        f"{SEP}\n"
        f"🆔 *Votre ID :* `{call.from_user.id}`\n"
        f"👤 *Votre pseudo :* {user_tag}\n"
        f"🎁 *Code promo : {settings.BOT_PROMO_CODE}*\n"
        f"{SEP}"
    )
    await call.message.edit_text(text, parse_mode="Markdown",
                                 reply_markup=premium_keyboard(price_7, price_30))
    await track_existing_message(call.from_user.id, call.message)
    await call.answer()


@router.callback_query(F.data == "premium:status")
async def cb_premium_status(call: CallbackQuery, session: AsyncSession):
    svc = PremiumService(session)
    sub = await svc.get_subscription(call.from_user.id)

    user_svc = UserService(session)
    db_user = await user_svc.get_by_id(call.from_user.id)
    is_premium = db_user.is_premium if db_user else False

    if sub and is_premium:
        expires = sub.expires_at.strftime("%d/%m/%Y à %H:%M") if sub.expires_at else "Illimité"
        text = (
            f"⭐ *Statut Premium*\n\n"
            f"{SEP}\n"
            f"│◉ Statut : ✅ *ACTIF*\n"
            f"│◉ Expire le : *{expires}*\n"
            f"│◉ Méthode : {sub.payment_method or 'Manuel'}\n"
            f"{SEP}"
        )
    else:
        text = (
            f"⭐ *Statut Premium*\n\n"
            f"{SEP}\n"
            f"│◉ Statut : ❌ *INACTIF*\n"
            f"│◉ Tu es sur le plan *Gratuit*\n"
            f"{SEP}\n\n"
            "Passe en Premium pour débloquer toutes les fonctionnalités !"
        )

    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=premium_keyboard())
    await track_existing_message(call.from_user.id, call.message)
    await call.answer()
