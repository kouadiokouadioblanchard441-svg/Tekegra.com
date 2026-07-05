"""Admin panel keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📊 Statistiques", callback_data="admin:stats"),
            InlineKeyboardButton(text="👥 Utilisateurs", callback_data="admin:users"),
        ],
        [
            InlineKeyboardButton(text="⏳ En attente", callback_data="admin:pending"),
            InlineKeyboardButton(text="⭐ Gérer Premium", callback_data="admin:premium"),
        ],
        [
            InlineKeyboardButton(text="📢 Diffusion", callback_data="admin:broadcast"),
            InlineKeyboardButton(text="🖼 Bannières", callback_data="admin:banners"),
        ],
        [
            InlineKeyboardButton(text="🏠 Menu principal", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_user_action_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Full action keyboard for managing a specific user."""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Approuver", callback_data=f"admin:approve:{user_id}"),
            InlineKeyboardButton(text="❌ Refuser", callback_data=f"admin:reject:{user_id}"),
        ],
        [
            InlineKeyboardButton(text="⭐ Activer Premium 30j", callback_data=f"admin:prem_on:{user_id}"),
            InlineKeyboardButton(text="🚫 Bannir", callback_data=f"admin:ban:{user_id}"),
        ],
        [
            InlineKeyboardButton(text="🔙 Retour admin", callback_data="admin:stats"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_approve_reject_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Compact approve/reject keyboard sent in new-user notifications."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Accepter", callback_data=f"admin:approve:{user_id}"),
            InlineKeyboardButton(text="❌ Refuser", callback_data=f"admin:reject:{user_id}"),
        ]
    ])


def admin_premium_action_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Legacy — kept for backward compat with /admin_user command."""
    return admin_user_action_keyboard(user_id)


def admin_confirm_broadcast_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Envoyer", callback_data="admin:broadcast_confirm"),
            InlineKeyboardButton(text="❌ Annuler", callback_data="admin:broadcast_cancel"),
        ]
    ])
