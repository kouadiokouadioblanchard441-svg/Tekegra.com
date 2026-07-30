# Lucky Jet AI Bot

Bot Telegram de signaux Lucky Jet avec panneau d'administration React et API Node.js.

## Architecture

| Composant | Technologie | Chemin |
|-----------|-------------|--------|
| Bot Telegram | Python 3.12 / Aiogram 3 / FastAPI | `artifacts/telegram-bot/` |
| Panneau admin | React / Vite | `artifacts/admin-panel/` |
| API backend | Node.js / Express / TypeScript | `artifacts/api-server/` |
| Base de données | Supabase PostgreSQL | via `SUPABASE_DATABASE_URL` |

## Lancer le projet

Les trois services démarrent automatiquement via les workflows Replit :

- **Telegram Bot** — `cd artifacts/telegram-bot && pip install -r requirements.txt && python main.py`
- **API Server** — `pnpm --filter @workspace/api-server run dev`
- **Admin Panel** — `pnpm --filter @workspace/admin-panel run dev`

## Secrets requis

| Clé | Description |
|-----|-------------|
| `SUPABASE_DATABASE_URL` | URL Session pooler Supabase (port 5432) |
| `TELEGRAM_BOT_TOKEN` | Token du bot (@BotFather) |
| `ADMIN_PASSWORD` | Mot de passe panneau admin |

## Variables d'environnement (optionnelles)

Voir `DEPLOY.md` pour la liste complète (`ADMIN_IDS`, `CHANNEL_1_ID`, `BOT_PROMO_CODE`, etc.).

## Déploiement Vercel

Voir `DEPLOY.md` — le projet est conçu pour Vercel + Supabase.  
Après déploiement, enregistrer le webhook via : `https://TON-APP.vercel.app/setup?token=ADMIN_PASSWORD`

## User preferences

- Langue de communication : français
