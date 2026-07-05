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
    from bot.keyboards.main_menu import guide_keyboard
    SEP = "━━━━━━━━━━━━━━━━━━━━━━"
    text = (
        f"🤖 *Comment fonctionne le bot ?*\n\n"
        f"Notre bot utilise des algorithmes avancés et de l'intelligence artificielle (IA) "
        f"pour analyser en temps réel les tendances des jeux du casino 1win.\n"
        f"⬣ Grâce à cette technologie, il génère des *signaux ultra-précis* pour maximiser "
        f"vos gains et guider chacun de vos choix.\n\n"
        f"{SEP}\n\n"
        f"⚙️ *Comment l'activer ?*\n\n"
        f"⬤ *1 ➦ REJOINDRE LES CANAUX*\n"
        f"Abonnez-vous à nos canaux officiels (boutons ci-dessous) ✅\n\n"
        f"⬤ *2 ➦ INSCRIPTION*\n"
        f"Appuyez sur le bouton *« INSCRIPTION »* pour créer un nouveau compte "
        f"avec le code promo `{settings.BOT_PROMO_CODE}`.\n"
        f"◆ Si vous possédez déjà un compte, déconnectez-vous puis créez-en un nouveau.\n\n"
        f"⬤ *3 ➦ DÉPÔT*\n"
        f"Cliquez sur le bouton *« RECHARGER »*.\n"
        f"◆ Effectuez un dépôt minimum de *3 000 F (5 $)* sur votre compte 1win "
        f"afin d'activer le bot et profiter des prédictions.\n\n"
        f"{SEP}\n\n"
        f"🔹 *Une fois le dépôt confirmé sur votre compte* ✅\n"
        f"Le bot sera automatiquement activé ✔️\n"
        f"Et vous pourrez accéder aux différents *PREDICTORS*\n\n"
        f"{SEP}\n"
        f"🎁 Code promo : `{settings.BOT_PROMO_CODE}`"
    )
    await call.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=guide_keyboard(
            affiliate_link=settings.BOT_AFFILIATE_LINK,
            channel_1_link=settings.CHANNEL_1_LINK,
            channel_1_name=settings.CHANNEL_1_NAME,
            channel_2_link=settings.CHANNEL_2_LINK,
            channel_2_name=settings.CHANNEL_2_NAME,
        ),
    )
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
