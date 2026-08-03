# Lucky Jet AI Bot

Bot Telegram de signaux de jeu (Lucky Jet / Mines / Rocket Queen) avec panneau d'administration React et API Node.js.

## Architecture

| Composant | Stack | Emplacement |
|-----------|-------|-------------|
| Panneau Admin | React / Vite / TypeScript | `artifacts/admin-panel/` |
| API Server | Node.js / Express / TypeScript | `artifacts/api-server/` |
| Bot Telegram | Python 3 / aiogram 3 / SQLAlchemy | `artifacts/telegram-bot/` |
| Base de données | Supabase PostgreSQL | variable `SUPABASE_DATABASE_URL` |

## Démarrage

Les workflows gérés démarrent automatiquement :

- **`artifacts/admin-panel: web`** — Panneau admin React sur `/admin-panel/`
- **`artifacts/api-server: API Server`** — API Express sur `/api`
- **`Telegram Bot`** — Bot Python (démarrer manuellement après avoir configuré les secrets)

## Variables d'environnement requises (Replit Secrets)

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Token du bot (@BotFather) |
| `SUPABASE_DATABASE_URL` | URL Supabase Session pooler (port 5432) |
| `SESSION_SECRET` | Clé JWT pour le panneau admin |

## Variables d'environnement optionnelles (userenv)

Configurées dans `.replit` sous `[userenv.shared]` :

| Variable | Valeur par défaut |
|----------|-------------------|
| `BOT_NAME` | Lucky Jet AI Bot |
| `BOT_PROMO_CODE` | JRYVES |
| `FREE_SIGNALS_PER_DAY` | 6 |
| `PREMIUM_SIGNALS_PER_DAY` | 9 |
| `ADMIN_ID` | ID Telegram de l'administrateur |
| `BOT_AFFILIATE_LINK` | Lien d'affiliation 1WIN |
| `CHANNEL_1_ID` / `CHANNEL_1_LINK` / `CHANNEL_1_NAME` | Chaîne obligatoire 1 |

## User preferences

- Communication en français
