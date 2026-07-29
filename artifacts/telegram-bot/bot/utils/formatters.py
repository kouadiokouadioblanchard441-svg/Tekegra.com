"""Unicode-styled message formatters — v2 avec indicateurs IA."""
from datetime import datetime
import pytz


SEP = "━━━━━━━━━━━━━━━━━━━━━━"


def _cote_label(cote_type: str) -> str:
    return "🎯 PETITE COTE" if cote_type == "petite" else "💰 GROSSE COTE"


def _quality_medal(quality: str) -> str:
    return {"GOLD": "🥇 GOLD", "SILVER": "🥈 SILVER", "BRONZE": "🥉 BRONZE"}.get(quality, quality)


def _confidence_bar(confidence: int) -> str:
    filled = round(confidence / 10)
    return "█" * filled + "░" * (10 - filled)


# ─── Lucky Jet ────────────────────────────────────────────────────────────────

def format_luckyjet_signal(
    heure: str,
    cote: str,
    assurance: str,
    promo_code: str,
    is_premium: bool = False,
    cote_type: str = "auto",
    mise_seconde: float = 0.0,
    confidence: int = 0,
    quality: str = "",
    trend: str = "",
    volatilite: str = "",
    force_bar: str = "",
    verification_code: str = "",
    rounds_analysed: int = 0,
) -> str:
    badge = "⭐ PREMIUM" if is_premium else "🎯 GRATUIT"
    medal = _quality_medal(quality) if quality else ""
    ct_label = f" | {_cote_label(cote_type)}" if cote_type != "auto" else ""
    seconde_line = f"│◉ ⚡ *PLACER À* : *{mise_seconde}s* après le départ\n" if mise_seconde else ""
    conf_bar = _confidence_bar(confidence) if confidence else (force_bar or "")
    verif = f"\n│◉ 🔐 *CODE* : `{verification_code}`" if verification_code else ""
    rounds_line = f"│◉ 🔬 *Rounds analysés* : {rounds_analysed}\n" if rounds_analysed else ""
    trend_line = f"│◉ {trend}\n" if trend else ""
    volatilite_line = f"│◉ 📊 *Volatilité* : {volatilite}\n" if volatilite else ""

    return (
        f"🚀 *LUCKY JET AI PREDICTION*\n"
        f"[{badge}{ct_label}] {medal}\n"
        f"{SEP}\n"
        f"│◉ ⏰ *HEURE* : *{heure}*\n"
        f"│◉ 🚀 *COTE CIBLE* : *{cote}*\n"
        f"│◉ 🛡 *ASSURANCE* : {assurance}\n"
        f"{seconde_line}"
        f"{SEP}\n"
        f"│◉ 🤖 *Confiance IA* : *{confidence}%*\n"
        f"│◉ [{conf_bar}]\n"
        f"{trend_line}"
        f"{volatilite_line}"
        f"{rounds_line}"
        f"{SEP}"
        f"{verif}\n"
        f"🎁 Code promo : `{promo_code}`"
    )


# ─── Rocket Queen ─────────────────────────────────────────────────────────────

def format_rocketqueen_signal(
    heure: str,
    cote: str,
    assurance: str,
    promo_code: str,
    is_premium: bool = False,
    cote_type: str = "auto",
    confidence: int = 0,
    quality: str = "",
    trend: str = "",
    volatilite: str = "",
    force_bar: str = "",
    verification_code: str = "",
    rounds_analysed: int = 0,
) -> str:
    badge = "⭐ PREMIUM" if is_premium else "🎯 GRATUIT"
    medal = _quality_medal(quality) if quality else ""
    ct_label = f" | {_cote_label(cote_type)}" if cote_type != "auto" else ""
    conf_bar = _confidence_bar(confidence) if confidence else (force_bar or "")
    verif = f"\n│◉ 🔐 *CODE* : `{verification_code}`" if verification_code else ""
    trend_line = f"│◉ {trend}\n" if trend else ""
    volatilite_line = f"│◉ 📊 *Volatilité* : {volatilite}\n" if volatilite else ""
    rounds_line = f"│◉ 🔬 *Rounds analysés* : {rounds_analysed}\n" if rounds_analysed else ""

    return (
        f"👑 *ROCKET QUEEN AI PREDICTION*\n"
        f"[{badge}{ct_label}] {medal}\n"
        f"{SEP}\n"
        f"│◉ ⏰ *HEURE* : *{heure}*\n"
        f"│◉ 🚀 *COTE CIBLE* : *{cote}*\n"
        f"│◉ 🛡 *ASSURANCE* : {assurance}\n"
        f"{SEP}\n"
        f"│◉ 🤖 *Confiance IA* : *{confidence}%*\n"
        f"│◉ [{conf_bar}]\n"
        f"{trend_line}"
        f"{volatilite_line}"
        f"{rounds_line}"
        f"{SEP}"
        f"{verif}\n"
        f"🎁 Code promo : `{promo_code}`"
    )


# ─── Aviator ──────────────────────────────────────────────────────────────────

def format_aviator_signal(
    heure: str,
    cote: str,
    cashout_second: float,
    mise_start: int,
    mise_end: int,
    assurance: str,
    promo_code: str,
    is_premium: bool = False,
    confidence: int = 0,
    quality: str = "",
    trend: str = "",
    volatilite: str = "",
    force_bar: str = "",
    verification_code: str = "",
    rounds_analysed: int = 0,
) -> str:
    badge = "⭐ PREMIUM" if is_premium else "🎯 GRATUIT"
    medal = _quality_medal(quality) if quality else ""
    conf_bar = _confidence_bar(confidence) if confidence else (force_bar or "")
    verif = f"\n│◉ 🔐 *CODE* : `{verification_code}`" if verification_code else ""
    trend_line = f"│◉ {trend}\n" if trend else ""
    volatilite_line = f"│◉ 📊 *Volatilité* : {volatilite}\n" if volatilite else ""
    rounds_line = f"│◉ 🔬 *Rounds analysés* : {rounds_analysed}\n" if rounds_analysed else ""

    return (
        f"✈️ *AVIATOR AI PREDICTION*\n"
        f"[{badge}] {medal}\n"
        f"{SEP}\n"
        f"│◉ ⏰ *HEURE DU ROUND* : *{heure}*\n"
        f"│◉ 🕐 *MISE* : entre *{mise_start}s* et *{mise_end}s* avant décollage\n"
        f"│◉ ⚡ *RETIRER À* : *{cashout_second}s* après décollage\n"
        f"│◉ 🚀 *COTE CIBLE* : *{cote}*\n"
        f"│◉ 🛡 *ASSURANCE* : {assurance}\n"
        f"{SEP}\n"
        f"│◉ 🤖 *Confiance IA* : *{confidence}%*\n"
        f"│◉ [{conf_bar}]\n"
        f"{trend_line}"
        f"{volatilite_line}"
        f"{rounds_line}"
        f"{SEP}"
        f"{verif}\n"
        f"🎁 Code promo : `{promo_code}`"
    )


# ─── Lucky Jet — Analyse ──────────────────────────────────────────────────────

def format_luckyjet_analysis(
    heure: str,
    niveau: str,
    risque: str,
    confidence: int = 0,
    trend: str = "",
    volatilite: str = "",
) -> str:
    conf_bar = _confidence_bar(confidence) if confidence else ""
    trend_line = f"│◉ *Tendance* : {trend}\n" if trend else ""
    volatilite_line = f"│◉ *Volatilité* : {volatilite}\n" if volatilite else ""
    conf_line = (
        f"│◉ 🤖 *Confiance IA* : *{confidence}%*\n│◉ [{conf_bar}]\n"
        if confidence else ""
    )
    return (
        f"🚀 *LUCKY JET — ANALYSE IA*\n"
        f"{SEP}\n"
        f"│◉ *Heure* : {heure} ⏰\n"
        f"│◉ *Niveau conseillé* : {niveau}\n"
        f"│◉ *Gestion du risque* : {risque} ✅\n"
        f"{trend_line}"
        f"{volatilite_line}"
        f"{conf_line}"
        f"{SEP}"
    )


# ─── Mines ────────────────────────────────────────────────────────────────────

def format_mines_signal(
    mines: int,
    niveau: str,
    risque: str,
    promo_code: str,
    is_premium: bool = False,
    confidence: int = 0,
    quality: str = "",
    volatilite: str = "",
    force_bar: str = "",
    verification_code: str = "",
    safe_probability: int = 0,
    rounds_analysed: int = 0,
) -> str:
    badge = "⭐ PREMIUM" if is_premium else "🎯 GRATUIT"
    medal = _quality_medal(quality) if quality else ""
    conf_bar = _confidence_bar(confidence) if confidence else (force_bar or "")
    verif = f"\n│◉ 🔐 *CODE* : `{verification_code}`" if verification_code else ""
    volatilite_line = f"│◉ 📊 *Volatilité* : {volatilite}\n" if volatilite else ""
    prob_line = f"│◉ 📐 *Prob. case sûre* : {safe_probability}%\n" if safe_probability else ""
    rounds_line = f"│◉ 🔬 *Rounds analysés* : {rounds_analysed}\n" if rounds_analysed else ""

    return (
        f"💣 *MINES AI PREDICTION* [{badge}] {medal}\n"
        f"{SEP}\n"
        f"│◉ 💣 *Pièges* : {mines} mines\n"
        f"│◉ *Niveau conseillé* : {niveau}\n"
        f"│◉ *Gestion du risque* : {risque} ✅\n"
        f"{prob_line}"
        f"{SEP}\n"
        f"│◉ 🤖 *Confiance IA* : *{confidence}%*\n"
        f"│◉ [{conf_bar}]\n"
        f"{volatilite_line}"
        f"{rounds_line}"
        f"{SEP}"
        f"{verif}\n"
        f"🎁 Code promo : `{promo_code}`"
    )


# ─── Countdown ────────────────────────────────────────────────────────────────

def format_countdown(seconds: int) -> str:
    return f"⏱ Signal valable encore *{seconds}* secondes."


# ─── Profil ───────────────────────────────────────────────────────────────────

def format_profile(
    first_name: str,
    telegram_id: int,
    registered_at: datetime,
    total_analyses: int,
    is_premium: bool,
    language: str,
    signals_today: int,
    max_signals: int,
) -> str:
    status = "⭐ *PREMIUM*" if is_premium else "🆓 *Gratuit*"
    reg_date = registered_at.strftime("%d/%m/%Y") if registered_at else "—"
    return (
        f"👤 *MON PROFIL*\n"
        f"{SEP}\n"
        f"│◉ *Nom* : {first_name}\n"
        f"│◉ *ID Telegram* : `{telegram_id}`\n"
        f"│◉ *Inscrit le* : {reg_date}\n"
        f"│◉ *Analyses totales* : {total_analyses}\n"
        f"│◉ *Signaux aujourd'hui* : {signals_today}/{max_signals}\n"
        f"│◉ *Statut* : {status}\n"
        f"│◉ *Langue* : {language}\n"
        f"{SEP}"
    )


# ─── Accueil ──────────────────────────────────────────────────────────────────

def format_welcome(
    first_name: str,
    free_count: int,
    premium_count: int,
    promo_code: str,
    affiliate_link: str,
) -> str:
    return (
        f"🚀 *Bienvenue {first_name} !*\n\n"
        f"🤖 Ce bot prédit à l'avance les résultats de *Lucky Jet* "
        f"et *Rocket Queen* sur 1WIN grâce à l'Intelligence Artificielle.\n\n"
        f"{SEP}\n"
        f"🎯 Signaux gratuits : *{free_count}/jour*\n"
        f"⭐ Signaux premium : *{premium_count}/jour*\n"
        f"{SEP}\n\n"
        f"🚀 *Pour commencer à gagner :*\n"
        f"1️⃣ Crée un nouveau compte *1WIN* avec le lien ci-dessous\n"
        f"2️⃣ Utilise le code promo `{promo_code}` lors de l'inscription\n"
        f"3️⃣ Effectue ton premier dépôt\n"
        f"4️⃣ Lance Lucky Jet ou Rocket Queen et utilise nos signaux !\n\n"
        f"🎁 Code promo : `{promo_code}`\n\n"
        "Choisis une option ci-dessous 👇"
    )


# ─── Admin ────────────────────────────────────────────────────────────────────

def format_admin_stats(
    total_users: int,
    premium_users: int,
    active_today: int,
    total_signals: int,
    pending_users: int = 0,
) -> str:
    return (
        f"📊 *DASHBOARD ADMIN*\n"
        f"{SEP}\n"
        f"│◉ *Utilisateurs totaux* : {total_users}\n"
        f"│◉ *Utilisateurs Premium* : {premium_users}\n"
        f"│◉ *Actifs aujourd'hui* : {active_today}\n"
        f"│◉ *Signaux générés* : {total_signals}\n"
        f"│◉ *En attente d'approbation* : {pending_users} ⏳\n"
        f"{SEP}"
    )
