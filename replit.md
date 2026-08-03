# Lucky Jet AI Bot

Bot Telegram de signaux de jeu (Lucky Jet / Mines / Rocket Queen) avec panneau d'administration React et API Node.js.

## Architecture

| Composant | Stack | Emplacement |
|-----------|-------|-------------|
| Panneau Admin | React / Vite / TypeScript | `artifacts/admin-panel/` |
| API Server | Node.js / Express / TypeScript | `artifacts/api-server/` |
| Bot Telegram production | Python 3 / aiogram 3 / SQLAlchemy | `plesk-deployment/telegram-bot/` |
| Base de données | Supabase PostgreSQL | variable `SUPABASE_DATABASE_URL` |

## Démarrage

Les services de développement Replit disponibles sont :

- **`artifacts/admin-panel: web`** — Panneau admin React sur `/admin-panel/`
- **`artifacts/api-server: API Server`** — API Express sur `/api`

Le bot Telegram **n'est pas lancé par Replit**. Il est exécuté sur le **même VPS
qui héberge Plesk**, comme service Python `systemd` avec :

```bash
systemctl enable --now telegram-bot
```

Replit sert uniquement d'environnement de développement et de préparation du
build GitHub → Plesk. En production, les variables du panel/API et du bot sont
configurées sur ce même serveur Plesk.

## Variables d'environnement de développement

Les secrets éventuellement présents dans Replit servent uniquement aux tests
et au développement. La production utilise les variables configurées dans
Plesk pour le panel/API et dans le service Python du même VPS Plesk.

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
