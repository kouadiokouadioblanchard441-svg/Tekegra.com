# Lucky Jet AI Bot

Bot Telegram de prédiction Lucky Jet et Mines avec IA, multilingue, premium et panneau admin.

## Run & Operate

- `cd artifacts/telegram-bot && python main.py` — démarrer le bot Telegram
- Bot workflow: **Telegram Bot**

## Stack

- Python 3.12 + Aiogram 3 + FastAPI
- PostgreSQL + SQLAlchemy async
- Traductions dans `/locales/` (8 langues)
- Signaux générés via algorithme IA simulé

## Architecture

```
artifacts/telegram-bot/
├── main.py                  — Point d'entrée
├── config/settings.py       — Configuration via env vars
├── database/                — Modèles SQLAlchemy + init
│   ├── models.py            — User, SignalHistory, Premium, etc.
│   └── db.py                — Engine + session factory
├── bot/
│   ├── handlers/            — start, menu, luckyjet, mines, profile, premium, admin
│   ├── keyboards/           — Claviers inline Telegram
│   ├── middlewares/         — Throttling anti-spam + DB session
│   ├── filters/             — Filtre admin
│   ├── services/            — signals.py, user_service.py, premium_service.py
│   └── utils/               — formatters.py (style Unicode) + cache.py
└── locales/                 — fr, en, ar, es, ru, pt, tr, hi
```

## Secrets requis

- `TELEGRAM_BOT_TOKEN` — Token du bot (via @BotFather)
- `ADMIN_IDS` — IDs Telegram des admins (virgule-séparé)
- `DATABASE_URL` — Auto-géré par Replit

## Variables d'environnement

- `BOT_PROMO_CODE` — Code promo 1WIN
- `BOT_AFFILIATE_LINK` — Lien affiliation 1WIN
- `FREE_SIGNALS_PER_DAY` — Signaux gratuits/jour (défaut: 6)
- `PREMIUM_SIGNALS_PER_DAY` — Signaux premium/jour (défaut: 9)

## Commandes du bot

`/start`, `/menu`, `/luckyjet`, `/mines`, `/profile`, `/history`, `/premium`, `/help`, `/language`, `/settings`, `/admin` (admin only)

## User preferences

- Bot en français par défaut, multilingue (8 langues)
- Style Unicode identique aux captures d'écran
- Architecture modulaire prête pour scaling

## Gotchas

- Sans `TELEGRAM_BOT_TOKEN`, le bot refuse de démarrer
- La DB est initialisée automatiquement au démarrage
- L'admin doit avoir son ID dans `ADMIN_IDS`
