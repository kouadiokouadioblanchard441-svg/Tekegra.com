"""Main menu callback handler."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_menu import main_menu_keyboard, language_keyboard
from bot.keyboards.luckyjet import luckyjet_menu_keyboard
from bot.keyboards.mines import mines_menu_keyboard
from bot.keyboards.rocketqueen import rocketqueen_menu_keyboard
from bot.keyboards.premium import premium_keyboard
from bot.services.user_service import UserService
from config import settings

router = Router()


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(call: CallbackQuery):
    await call.message.edit_text(
        "🎯 *Menu principal* — Choisis une option :",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(settings.BOT_AFFILIATE_LINK),
    )
    await call.answer()


@router.callback_query(F.data == "menu:luckyjet")
async def cb_luckyjet_menu(call: CallbackQuery):
    await call.message.edit_text(
        "🎯 *Lucky Jet* — Choisis une option :",
        parse_mode="Markdown",
        reply_markup=luckyjet_menu_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "menu:mines")
async def cb_mines_menu(call: CallbackQuery):
    await call.message.edit_text(
        "💣 *Mines* — Choisis une option :",
        parse_mode="Markdown",
        reply_markup=mines_menu_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "menu:rocketqueen")
async def cb_rocketqueen_menu(call: CallbackQuery):
    await call.message.edit_text(
        "👑 *Rocket Queen* — Choisis ton type de signal :",
        parse_mode="Markdown",
        reply_markup=rocketqueen_menu_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data == "menu:premium")
async def cb_premium_menu(call: CallbackQuery):
    text = (
        "⭐ *PREMIUM — Avantages*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"│◉ Signaux illimités : *{settings.PREMIUM_SIGNALS_PER_DAY}/jour*\n"
        "│◉ Cotes ultra-élevées (jusqu'à 25x+)\n"
        "│◉ Analyses IA avancées\n"
        "│◉ Priorité sur les signaux\n"
        "│◉ Support dédié\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=premium_keyboard())
    await call.answer()


@router.callback_query(F.data == "menu:language")
async def cb_language_menu(call: CallbackQuery):
    await call.message.edit_text(
        "🌍 *Choisissez votre langue :*",
        parse_mode="Markdown",
        reply_markup=language_keyboard(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("lang:"))
async def cb_set_language(call: CallbackQuery, session: AsyncSession):
    lang = call.data.split(":")[1]
    lang_names = {
        "fr": "🇫🇷 Français", "en": "🇬🇧 English", "ar": "🇸🇦 العربية",
        "es": "🇪🇸 Español", "ru": "🇷🇺 Русский", "pt": "🇧🇷 Português",
        "tr": "🇹🇷 Türkçe", "hi": "🇮🇳 हिंदी",
    }
    svc = UserService(session)
    await svc.set_language(call.from_user.id, lang)
    name = lang_names.get(lang, lang)
    await call.message.edit_text(
        f"✅ Langue changée : *{name}*",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(settings.BOT_AFFILIATE_LINK),
    )
    await call.answer(f"✅ Langue : {name}")


@router.callback_query(F.data == "menu:guide")
async def cb_guide(call: CallbackQuery):
    from bot.keyboards.main_menu import back_to_main_keyboard
    text = (
        "📚 *GUIDE — Comment utiliser le bot*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "│◉ *Étape 1* : Crée un compte 1WIN\n"
        f"│◉ *Étape 2* : Utilise le code `{settings.BOT_PROMO_CODE}`\n"
        "│◉ *Étape 3* : Effectue un dépôt\n"
        "│◉ *Étape 4* : Lance Lucky Jet ou Rocket Queen\n"
        "│◉ *Étape 5* : Demande un signal ici\n"
        "│◉ *Étape 6* : Mise selon la cote indiquée\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "⚠️ *Important* : Joue de manière responsable.\n"
        "Ne mise jamais plus que ce que tu peux perdre."
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=back_to_main_keyboard())
    await call.answer()


@router.callback_query(F.data == "menu:support")
async def cb_support(call: CallbackQuery):
    from bot.keyboards.main_menu import back_to_main_keyboard
    text = (
        "☎ *SUPPORT*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "│◉ Pour toute question, contacte\n"
        "│   notre équipe de support.\n"
        "│◉ Temps de réponse : < 24h\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📧 Contacte-nous via Telegram."
    )
    await call.message.edit_text(text, parse_mode="Markdown", reply_markup=back_to_main_keyboard())
    await call.answer()
