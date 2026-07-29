# Lucky Jet AI Bot

A Telegram bot with signals for Lucky Jet and Mines casino games, with a React admin panel and Node.js API — designed to deploy on Vercel with a Supabase PostgreSQL database.

## Architecture

```
┌─────────────────────────────────────────────┐
│                 VERCEL                       │
│  /              → Admin Panel (React/Vite)  │
│  /api/*         → API (Express Node.js)     │
│  /webhook       → Telegram Bot (Python)     │
│  /setup         → One-time setup endpoint   │
│  DB: Supabase PostgreSQL                    │
└─────────────────────────────────────────────┘
```

## Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Admin Panel | `artifacts/admin-panel/` | React + Vite + Tailwind dashboard |
| API Server | `artifacts/api-server/` | Express Node.js REST API |
| Telegram Bot | `artifacts/telegram-bot/` | aiogram 3 Python bot (polling on Replit) |

## Shared Libraries

| Library | Path | Description |
|---------|------|-------------|
| `@workspace/db` | `lib/db/` | Drizzle ORM + pg (used by API server) |
| `@workspace/api-zod` | `lib/api-zod/` | Zod schemas for API validation |
| `@workspace/api-client-react` | `lib/api-client-react/` | Generated React Query hooks + customFetch |

## Required Environment Secrets

| Secret | Description |
|--------|-------------|
| `SUPABASE_DATABASE_URL` | Supabase Session pooler URL (port 5432) |
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather |
| `ADMIN_PASSWORD` | Admin panel login password |
| `ADMIN_IDS` | Telegram admin IDs (comma-separated) |
| `SESSION_SECRET` | JWT signing secret (32+ chars) |

## Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_PROMO_CODE` | `JRYVES` | 1WIN promo code shown in signals |
| `BOT_AFFILIATE_LINK` | — | 1WIN affiliate link |
| `FREE_SIGNALS_PER_DAY` | `6` | Free signals per day |
| `PREMIUM_SIGNALS_PER_DAY` | `9` | Premium signals per day |
| `CHANNEL_1_ID` | — | Required channel ID (integer) |
| `CHANNEL_1_LINK` | — | Required channel invite link |
| `CHANNEL_1_NAME` | — | Required channel display name |
| `CHANNEL_2_ID` / `CHANNEL_2_LINK` / `CHANNEL_2_NAME` | — | Second optional channel |

## How to Run on Replit

- **Admin Panel**: workflow `artifacts/admin-panel: web` (Vite dev server)
- **API Server**: workflow `artifacts/api-server: API Server` (builds + starts Express)
- **Telegram Bot** (polling): workflow `Telegram Bot` — requires `TELEGRAM_BOT_TOKEN`

## How to Deploy on Vercel

See `DEPLOY.md` for full instructions. Summary:

1. Push to GitHub
2. Import on vercel.com — Vercel auto-detects `vercel.json` at project root
3. Set all env vars in Vercel dashboard (see table above)
4. After deploy, visit `https://YOUR-APP.vercel.app/setup?token=ADMIN_PASSWORD` once to register the webhook

## Database Notes

- The **Telegram bot** uses SQLAlchemy + asyncpg (Python)
- The **API server** uses Drizzle ORM + pg (Node.js)
- Both connect via `SUPABASE_DATABASE_URL`
- Use **Session pooler (port 5432)**, NOT the Transaction pooler (port 6543)
- Tables are created automatically on first run (`init_db()` in Python, `drizzle-kit push` for Node.js schema)

## User Preferences

- French preferred for communication
