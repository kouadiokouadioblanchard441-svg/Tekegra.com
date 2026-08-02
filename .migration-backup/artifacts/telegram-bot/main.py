"""Polling is intentionally disabled.

Production traffic must arrive through Vercel's ``/api/webhook`` function.
This file remains only so an old Replit workflow fails safely instead of
silently competing with Telegram's webhook.
"""
if __name__ == "__main__":
    print("Telegram polling is disabled. Use the Vercel POST endpoint /api/webhook.")
