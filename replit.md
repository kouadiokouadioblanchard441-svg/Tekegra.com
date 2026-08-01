# Lucky Jet AI Bot

Un bot Telegram de signaux de jeu (Lucky Jet / Mines / Rocket Queen) avec panneau d'administration React et API Node.js.

## Architecture

| Composant | Stack | Emplacement |
|-----------|-------|-------------|
| Bot Telegram | Python 3 / aiogram 3 / SQLAlchemy | `artifacts/telegram-bot/` |
| Panneau Admin | React / Vite / TypeScript | `artifacts/admin-panel/` |
| API Server | Node.js / Express / TypeScript | `artifacts/api-server/` |
| Base de données | Supabase PostgreSQL (asyncpg) | variable `SUPABASE_DATABASE_URL` |

## Lancer le projet

### Bot Telegram (workflow principal)
Le workflow **"Telegram Bot"** démarre automatiquement :
```
cd artifacts/telegram-bot && pip install -r requirements.txt && python main.py
```

### Admin Panel & API
```bash
pnpm install          # à la racine du projet
pnpm --filter @workspace/admin-panel run dev
pnpm --filter @workspace/api-server run dev
```

## Variables d'environnement requises (Replit Secrets)

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Token du bot (@BotFather), stocké comme secret |
| `APP_URL` | URL HTTPS de production Vercel |
| `WEBHOOK_SECRET` | Secret Telegram du webhook, stocké comme secret |
| `SUPABASE_DATABASE_URL` | URL Supabase Session pooler (port 5432) |
| `ADMIN_ID` | ID Telegram de l’administrateur du webhook |
| `SESSION_SECRET` | Clé JWT pour le panneau admin |

## Variables optionnelles

| Variable | Défaut | Description |
|----------|--------|-------------|
| `BOT_PROMO_CODE` | `JRYVES` | Code promo 1WIN |
| `BOT_AFFILIATE_LINK` | `https://1win.com` | Lien d'affiliation |
| `FREE_SIGNALS_PER_DAY` | `6` | Signaux gratuits/jour |
| `PREMIUM_SIGNALS_PER_DAY` | `9` | Signaux premium/jour |
| `CHANNEL_1_ID` / `CHANNEL_1_LINK` / `CHANNEL_1_NAME` | — | Chaîne obligatoire 1 |
| `CHANNEL_2_ID` / `CHANNEL_2_LINK` / `CHANNEL_2_NAME` | — | Chaîne obligatoire 2 |

## Déploiement Vercel

Voir `DEPLOY.md` pour le guide complet de déploiement sur Vercel avec webhook Telegram.

Le mot de passe du panneau admin est géré uniquement dans Supabase, dans
`bot_settings.admin_password_hash`. `ADMIN_PASSWORD` n'est pas utilisé par
l'application et ne doit pas être configuré sur Vercel.

## User preferences

- Communication en français
