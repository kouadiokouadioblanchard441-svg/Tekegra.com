"""Main menu callback handler — new flow with photo banners and registration gate."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main_menu import (
    main_menu_keyboard,
    language_keyboard,
    guide_keyboard,
    register_keyboard,
    game_select_keyboard,
    back_to_main_keyboard,
)
from bot.keyboards.luckyjet import luckyjet_reglage_keyboard
from bot.keyboards.mines import mines_premium_type_keyboard
from bot.services.user_service import UserService
from bot.services.settings_service import BotSettingsService
from bot.utils.navigation import navigate
from bot.utils.user_prefs import get_cote_pref, get_star_pref
from config import settings

router = Router()

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


# ── Helper: fetch banner file_id ──────────────────────────────────────────────
async def _banner(session: AsyncSession, key: str) -> str | None:
    svc = BotSettingsService(session)
    return await svc.get(key)


# ── Main menu ─────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "menu:main")
async def cb_main_menu(call: CallbackQuery, session: AsyncSession):
    photo = await _banner(session, "menu_banner")
    text = "🎮 *Menu*\n\nChoisis une option ci-dessous 👇"
    await navigate(call, text, main_menu_keyboard(settings.BOT_AFFILIATE_LINK), photo_id=photo)
    await call.answer()


@router.callback_query(F.data == "menu:noop")
async def cb_noop(call: CallbackQuery):
    await call.answer()


# ── GET SIGNAL gate ───────────────────────────────────────────────────────────
@router.callback_query(F.data == "menu:get_signal")
async def cb_get_signal(call: CallbackQuery, session: AsyncSession):
    user = call.from_user
    svc = UserService(session)
    db_user = await svc.get_by_id(user.id)

    # If not registered → show inscription page
    if not db_user or not db_user.has_registered:
        photo = await _banner(session, "register_banner")
        text = (
            "🔷 *Pour profiter pleinement du bot, suivez ces 3 étapes :* ↓\n\n"
            "◇──────────────────────────◇\n\n"
            "◉ *1 ➜* Appuyez sur le bouton *INSCRIPTION* pour créer un nouveau compte\n"
            "◆ Si vous avez déjà un compte, déconnectez-vous puis créez-en un nouveau\n\n"
            "◇──────────────────────────◇\n\n"
            f"◉ *2 ➜* Utilisez le code promo *{settings.BOT_PROMO_CODE}* lors de l'inscription\n\n"
            "◇──────────────────────────◇\n\n"
            "◉ *3 ➜* 📱 Une notification de confirmation vous sera envoyée "
            "automatiquement après l'inscription ✅\n\n"
            "◇──────────────────────────◇"
        )
        await navigate(call, text, register_keyboard(settings.BOT_AFFILIATE_LINK), photo_id=photo)
        await call.answer()
        return

    # Registered → game selection
    await cb_game_select_inner(call, session)


@router.callback_query(F.data == "menu:confirm_registered")
async def cb_confirm_registered(call: CallbackQuery, session: AsyncSession):
    """User confirms they've created their 1WIN account."""
    svc = UserService(session)
    await svc.mark_registered(call.from_user.id)
    await call.answer("✅ Compte confirmé ! Accès aux signaux débloqué.", show_alert=True)
    await cb_game_select_inner(call, session)


@router.callback_query(F.data == "menu:game_select")
async def cb_game_select(call: CallbackQuery, session: AsyncSession):
    await cb_game_select_inner(call, session)


async def cb_game_select_inner(call: CallbackQuery, session: AsyncSession):
    photo = await _banner(session, "game_select_banner")
    text = (
        "🎮 *Choisissez votre jeu :*\n\n"
        f"{SEP}\n"
        "│◉ 🎯 *Lucky Jet* — Prédictions de cotes\n"
        "│◉ 💣 *Mines* — Grille de cases sûres\n"
        f"{SEP}"
    )
    await navigate(call, text, game_select_keyboard(), photo_id=photo)
    await call.answer()


# ── Game pages ────────────────────────────────────────────────────────────────
async def _show_luckyjet_page(
    call: CallbackQuery,
    session: AsyncSession,
    premium_cote_type: str | None = None,
):
    photo = await _banner(session, "luckyjet_banner")
    text = (
        "🚀 *LUCKY JET*\n\n"
        f"{SEP}\n"
        "│◉ Notre IA analyse les tendances en temps réel\n"
        "│◉ Signaux ultra-précis pour maximiser vos gains\n"
        "│◉ Cotes de 1.10x jusqu'à 25x+\n"
        f"{SEP}\n\n"
        "▶ Appuyez sur *GET SIGNAL* pour obtenir votre prédiction !"
    )
    await navigate(
        call,
        text,
        luckyjet_page_keyboard(premium_cote_type),
        photo_id=photo,
    )
    await call.answer()


@router.callback_query(F.data == "menu:luckyjet")
async def cb_luckyjet_page(call: CallbackQuery, session: AsyncSession):
    """Sélection Lucky Jet → affiche directement l'écran de réglage (Petite/Grosse)."""
    current = get_cote_pref(call.from_user.id)
    photo = await _banner(session, "luckyjet_banner")
    text = (
        "🎯 *LUCKY JET — Réglage*\n\n"
        f"{SEP}\n"
        "│◉ Choisissez votre plage de coefficient :\n"
        "│◉ Ce réglage sera appliqué à vos signaux\n"
        f"{SEP}\n\n"
        "👇 Sélectionnez ci-dessous :"
    )
    await navigate(call, text, luckyjet_reglage_keyboard(current), photo_id=photo)
    await call.answer()


@router.callback_query(F.data.startswith("menu:luckyjet:premium:"))
async def cb_luckyjet_premium_page(call: CallbackQuery, session: AsyncSession):
    cote_type = call.data.rsplit(":", 1)[-1]
    if cote_type not in ("petite", "grosse"):
        await call.answer("Mode Premium invalide", show_alert=True)
        return
    await _show_luckyjet_page(call, session, cote_type)


@router.callback_query(F.data == "menu:mines")
async def cb_mines_page(call: CallbackQuery, session: AsyncSession):
    """Sélection Mines → affiche directement l'écran de réglage (Petite/Grosse étoiles)."""
    current = get_star_pref(call.from_user.id)
    photo = await _banner(session, "mines_banner")
    text = (
        "💣 *MINES — Réglage*\n\n"
        f"{SEP}\n"
        "│◉ Choisissez le nombre d'étoiles ⭐ à afficher :\n"
        "│◉ Ce réglage s'applique à tous vos signaux Mines\n"
        f"{SEP}\n\n"
        "👇 Sélectionnez ci-dessous :"
    )
    await navigate(call, text, mines_premium_type_keyboard(current), photo_id=photo)
    await call.answer()


# ── Language ──────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "menu:language")
async def cb_language_menu(call: CallbackQuery, session: AsyncSession):
    await navigate(
        call,
        "🌍 *Choisissez votre langue :*",
        language_keyboard(),
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

    photo = await _banner(session, "menu_banner")
    text = f"✅ Langue changée : *{name}*\n\nChoisis une option ci-dessous 👇"
    await navigate(call, text, main_menu_keyboard(settings.BOT_AFFILIATE_LINK), photo_id=photo)
    await call.answer(f"✅ {name}")


# ── Guide ─────────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "menu:guide")
async def cb_guide(call: CallbackQuery, session: AsyncSession):
    photo = await _banner(session, "guide_banner")
    text = (
        "🤖 *Comment fonctionne le bot ?*\n\n"
        "Notre bot utilise des algorithmes avancés et de l'intelligence artificielle (IA) "
        "pour analyser en temps réel les tendances des jeux du casino 1win.\n"
        "⬣ Grâce à cette technologie, il génère des *signaux ultra-précis* pour maximiser "
        "vos gains et guider chacun de vos choix.\n\n"
        f"{SEP}\n\n"
        "⚙️ *Comment l'activer ?*\n\n"
        "⬤ *1 ➦ REJOINDRE LES CANAUX*\n"
        "Abonnez-vous à nos canaux officiels (boutons ci-dessous) ✅\n\n"
        "⬤ *2 ➦ INSCRIPTION*\n"
        f"Appuyez sur *« INSCRIPTION »* et créez un compte avec le code promo *{settings.BOT_PROMO_CODE}*.\n"
        "◆ Si vous possédez déjà un compte, déconnectez-vous puis créez-en un nouveau.\n\n"
        "⬤ *3 ➦ DÉPÔT*\n"
        "Effectuez un dépôt minimum de *3 000 F (5 $)* pour activer les prédictions.\n\n"
        f"{SEP}\n"
        f"🎁 Code promo : *{settings.BOT_PROMO_CODE}*"
    )
    await navigate(
        call, text,
        guide_keyboard(
            affiliate_link=settings.BOT_AFFILIATE_LINK,
            channel_1_link=settings.CHANNEL_1_LINK,
            channel_1_name=settings.CHANNEL_1_NAME,
            channel_2_link=settings.CHANNEL_2_LINK,
            channel_2_name=settings.CHANNEL_2_NAME,
        ),
        photo_id=photo,
    )
    await call.answer()


# ── Support ───────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "menu:support")
async def cb_support(call: CallbackQuery, session: AsyncSession):
    text = (
        "☎ *SUPPORT*\n\n"
        f"{SEP}\n"
        "│◉ Pour toute question, contactez notre équipe.\n"
        "│◉ Temps de réponse : < 24h\n"
        f"{SEP}\n\n"
        "📧 Contacte-nous via Telegram."
    )
    await navigate(call, text, back_to_main_keyboard())
    await call.answer()


# ── Premium (kept for /premium command compatibility) ─────────────────────────
@router.callback_query(F.data == "menu:premium")
async def cb_premium_menu(call: CallbackQuery, session: AsyncSession):
    from bot.handlers.premium import show_premium
    await show_premium(call, session)
