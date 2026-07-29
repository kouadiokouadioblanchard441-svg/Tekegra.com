# Lucky Jet AI Bot

A Telegram bot for Lucky Jet signals with a React admin panel and Node.js/Express API server.

## Architecture

| Layer | Stack | Path |
|-------|-------|------|
| Telegram Bot | Python 3.12, aiogram 3, FastAPI, SQLAlchemy + asyncpg | `artifacts/telegram-bot/` |
| Admin Panel | React, Vite, Tailwind, shadcn/ui | `artifacts/admin-panel/` |
| API Server | Node.js, Express 5, Drizzle ORM, pg | `artifacts/api-server/` |
| DB Library | Drizzle ORM schema (shared) | `lib/db/` |
| API Spec | Zod schemas + OpenAPI spec | `lib/api-spec/`, `lib/api-zod/` |

Database: **Supabase PostgreSQL** (shared by bot and API server).

## Running on Replit

### Workflows

- **Telegram Bot** — `cd artifacts/telegram-bot && pip install -r requirements.txt && python main.py`
- **API Server** — `pnpm --filter @workspace/api-server run dev` (port 8080)
- **Admin Panel** — `pnpm --filter @workspace/admin-panel run dev` (port assigned by Replit)

### Required secrets (set via Replit Secrets)

| Secret | Description |
|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `DATABASE_URL` | Supabase Session pooler URL, port **5432** |
| `ADMIN_PASSWORD` | Password for the admin panel |
| `SESSION_SECRET` | JWT signing secret (32+ chars) ✅ already set |

### Already configured env vars

| Variable | Value |
|----------|-------|
| `ADMIN_IDS` | `8537454742` |
| `BOT_NAME` | `Lucky Jet AI Bot` |
| `BOT_PROMO_CODE` | `JRYVES` |
| `FREE_SIGNALS_PER_DAY` | `6` |
| `PREMIUM_SIGNALS_PER_DAY` | `9` |
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `INFO` |

### Database setup (first run)

```bash
cd lib/db && pnpm run push
```

## Deployment (Vercel)

See `DEPLOY.md` for the full Vercel deployment guide. The project deploys as:
- `/` → Admin Panel (React, static)
- `/api/*` → API Server (Express, serverless)
- `/webhook` → Telegram Bot (Python, serverless)

## User preferences

- Keep existing project structure — do not restructure or migrate without asking.
