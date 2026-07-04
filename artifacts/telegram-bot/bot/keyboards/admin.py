from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📊 Statistiques", callback_data="admin:stats"),
            InlineKeyboardButton(text="👥 Utilisateurs", callback_data="admin:users"),
        ],
        [
            InlineKeyboardButton(text="⭐ Gérer Premium", callback_data="admin:premium"),
            InlineKeyboardButton(text="📢 Diffusion", callback_data="admin:broadcast"),
        ],
        [
            InlineKeyboardButton(text="🌍 Langues", callback_data="admin:languages"),
            InlineKeyboardButton(text="📋 Logs", callback_data="admin:logs"),
        ],
        [
            InlineKeyboardButton(text="🏠 Menu principal", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_premium_action_keyboard(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✅ Activer 30j", callback_data=f"admin:prem_on:{user_id}"),
            InlineKeyboardButton(text="❌ Désactiver", callback_data=f"admin:prem_off:{user_id}"),
        ],
        [
            InlineKeyboardButton(text="🔙 Retour admin", callback_data="admin:stats"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_confirm_broadcast_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Envoyer", callback_data="admin:broadcast_confirm"),
            InlineKeyboardButton(text="❌ Annuler", callback_data="admin:broadcast_cancel"),
        ]
    ])
