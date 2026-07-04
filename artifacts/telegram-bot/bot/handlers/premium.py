"""Premium subscription handlers."""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services.premium_service import PremiumService
from bot.services.user_service import UserService
from bot.keyboards.premium import premium_keyboard
from bot.keyboards.main_menu import back_to_main_keyboard
from config import settings

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


async def show_premium(event: Message | CallbackQuery):
    text = (
        "⭐ *PREMIUM — Avantages*\n\n"
        f"{SEP}\n"
        f"│◉ *{settings.PREMIUM_SIGNALS_PER_DAY} signaux/jour* (vs {settings.FREE_SIGNALS_PER_DAY} gratuits)\n"
        "│◉ Cotes ultra-élevées (jusqu'à *25x+*)\n"
        "│◉ Analyses IA avancées\n"
        "│◉ Accès aux 2 jeux (Lucky Jet + Mines)\n"
        "│◉ Priorité de traitement\n"
        "│◉ Support dédié\n"
        f"{SEP}\n\n"
        f"📣 Code promo : `{settings.BOT_PROMO_CODE}`"
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="Markdown", reply_markup=premium_keyboard())
        await event.answer()
    else:
        await event.answer(text, parse_mode="Markdown", reply_markup=premium_keyboard())


@router.callback_query(F.data.startswith("premium:buy_"))
async def cb_buy_premium(call: CallbackQuery):
    days = call.data.split("_")[-1]
    price_map = {"7": "9.99$", "30": "29.99$"}
    price = price_map.get(days, "?")

    text = (
        f"⭐ *Activation Premium — {days} jours*\n\n"
        f"{SEP}\n"
        f"│◉ Durée : *{days} jours*\n"
        f"│◉ Prix : *{price}*\n"
        f"{SEP}\n\n"
        "📩 Pour activer votre abonnement, contactez notre support en mentionnant votre ID Telegram.\n\n"
        f"🆔 Votre ID : `{call.from_user.id}`\n\n"
        f"📣 Code promo : `{settings.BOT_PROMO_CODE}`"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=premium_keyboard())
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
    await call.answer()
