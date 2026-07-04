"""Unicode-styled message formatters matching the bot screenshots."""
from datetime import datetime
import pytz


SEP = "━━━━━━━━━━━━━━━━━━━━━━"


def format_luckyjet_signal(
    heure: str,
    cote: str,
    assurance: str,
    promo_code: str,
    is_premium: bool = False
) -> str:
    badge = "⭐ PREMIUM" if is_premium else "🎯 GRATUIT"
    return (
        f"🚀 *LUCKY JET PREDICTION* [{badge}]\n"
        f"{SEP}\n"
        f"│◉➤ *HEURE* : {heure} ⏰\n"
        f"│◉➤ *COTE* : {cote} 🚀\n"
        f"│◉➤ *ASSURANCE* : {assurance} ✅\n"
        f"{SEP}\n"
        f"code promo: `{promo_code}`"
    )


def format_luckyjet_analysis(
    heure: str,
    niveau: str,
    risque: str,
) -> str:
    return (
        f"🚀 *LUCKY JET ANALYSE*\n"
        f"{SEP}\n"
        f"│◉ *Heure* : {heure} ⏰\n"
        f"│◉ *Niveau conseillé* : {niveau}\n"
        f"│◉ *Gestion du risque* : {risque} ✅\n"
        f"{SEP}"
    )


def format_mines_signal(
    mines: int,
    niveau: str,
    risque: str,
    promo_code: str,
    is_premium: bool = False
) -> str:
    badge = "⭐ PREMIUM" if is_premium else "🎯 GRATUIT"
    return (
        f"💣 *MINES ANALYSE* [{badge}]\n"
        f"{SEP}\n"
        f"│◉➤ *Difficulté* : {mines} mines 💣\n"
        f"│◉➤ *Niveau conseillé* : {niveau}\n"
        f"│◉➤ *Gestion du risque* : {risque} ✅\n"
        f"{SEP}\n"
        f"code promo: `{promo_code}`"
    )


def format_countdown(seconds: int) -> str:
    return (
        f"🔄 Prochain signal disponible dans *{seconds}* secondes."
    )


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


def format_welcome(
    first_name: str,
    free_count: int,
    premium_count: int,
    promo_code: str,
    affiliate_link: str,
) -> str:
    return (
        f"🚀 *Bienvenue {first_name} sur Lucky Jet AI Bot !*\n\n"
        f"🤖 Ce bot prédit à l'avance le résultat du jeu "
        f"*Lucky Jet* en utilisant des technologies d'Intelligence Artificielle.\n\n"
        f"{SEP}\n"
        f"🎯 Signaux gratuits : *{free_count}*\n"
        f"⭐ Signaux premium : *{premium_count}*\n"
        f"{SEP}\n\n"
        f"🚀 *Pour commencer à gagner :*\n"
        f"1️⃣ Crée un nouveau compte *1WIN* avec le lien ci-dessous\n"
        f"2️⃣ Utilise le code promo `{promo_code}` lors de l'inscription\n"
        f"3️⃣ Effectue ton premier dépôt\n"
        f"4️⃣ Lance Lucky Jet et utilise nos signaux !\n\n"
        f"Choisis une option ci-dessous 👇"
    )


def format_admin_stats(
    total_users: int,
    premium_users: int,
    active_today: int,
    total_signals: int,
) -> str:
    return (
        f"📊 *DASHBOARD ADMIN*\n"
        f"{SEP}\n"
        f"│◉ *Utilisateurs totaux* : {total_users}\n"
        f"│◉ *Utilisateurs Premium* : {premium_users}\n"
        f"│◉ *Actifs aujourd'hui* : {active_today}\n"
        f"│◉ *Signaux générés* : {total_signals}\n"
        f"{SEP}"
    )
