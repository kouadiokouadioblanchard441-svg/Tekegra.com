# Déploiement — Guide complet

## 1. Admin Panel + API → Vercel

### Étape 1 — Importer le projet sur Vercel

1. Allez sur [vercel.com/new](https://vercel.com/new)
2. Cliquez **Import Git Repository** → sélectionnez ce dépôt
3. Vercel détecte automatiquement le `vercel.json` → ne changez rien aux paramètres du build

### Étape 2 — Variables d'environnement à ajouter sur Vercel

Dans **Settings → Environment Variables** de votre projet Vercel, ajoutez :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SUPABASE_DATABASE_URL` | URL de connexion PostgreSQL Supabase | `postgresql://postgres.xxx:password@aws-0-eu-west-3.pooler.supabase.com:5432/postgres` |
| `TELEGRAM_BOT_TOKEN` | Token du bot (pour la diffusion) | `7123456789:AAHdqTcvCH1vGWJxf...` |
| `ADMIN_PASSWORD` | Mot de passe de l'interface admin | `MonMotDePasse2024!` |
| `SESSION_SECRET` | Clé secrète JWT (min 32 caractères) | `une-chaine-aleatoire-tres-longue-et-securisee` |

> ⚠️ **SUPABASE_DATABASE_URL** : utilisez le **Session pooler (port 5432)** ou la **connexion directe**,
> **pas** le Transaction pooler (port 6543) qui est incompatible avec SQLAlchemy.

### Étape 3 — Paramètres Vercel (auto-détectés via vercel.json)

| Paramètre | Valeur |
|-----------|--------|
| Framework | Other (aucun) |
| Build Command | `pnpm install && pnpm --filter @workspace/admin-panel run build` |
| Output Directory | `artifacts/admin-panel/dist/public` |
| Install Command | `pnpm install` |
| Node.js Version | 20.x |

### Ce qui est déployé sur Vercel

- **`/`** → Panel admin React (dashboard, users, settings, broadcast)
- **`/api/*`** → API Express serverless (auth JWT, stats, gestion utilisateurs, broadcast)
- **`/api/healthz`** → Health check

---

## 2. Bot Telegram → Hébergement séparé

Le bot Telegram utilise le **long-polling** qui n'est pas compatible avec Vercel
(pas de processus persistant). Il doit être hébergé sur une plateforme qui supporte
les processus continus.

### Option A — Railway (recommandé, gratuit jusqu'à $5/mois)

1. Créer un projet sur [railway.app](https://railway.app)
2. Importer ce dépôt GitHub
3. **Start Command** : `cd artifacts/telegram-bot && pip install -r requirements.txt && python main.py`
4. Variables d'environnement à ajouter :

| Variable | Valeur |
|----------|--------|
| `SUPABASE_DATABASE_URL` | Même URL que Vercel |
| `TELEGRAM_BOT_TOKEN` | Token du bot |
| `ADMIN_IDS` | Vos IDs Telegram admin |
| `BOT_PROMO_CODE` | Code promo (ex: JRYVES) |
| `BOT_AFFILIATE_LINK` | Lien affiliation 1WIN |

### Option B — Mode Webhook (Railway / Render / Fly.io)

Utiliser `main_webhook.py` au lieu de `main.py` pour un démarrage plus rapide :

```bash
# Variable supplémentaire
WEBHOOK_HOST=https://votre-app.railway.app

# Start Command
cd artifacts/telegram-bot && pip install -r requirements.txt && python main_webhook.py
```

### Option C — Rester sur Replit

Le workflow **Telegram Bot** sur Replit est déjà configuré pour le polling.
Il suffit d'y mettre le bon `TELEGRAM_BOT_TOKEN` et il tourne en continu.

---

## 3. Architecture finale

```
┌─────────────────────────────────────────┐
│              VERCEL                      │
│                                          │
│  Panel Admin (React)  →  /              │
│  API Express (serverless)  →  /api/*    │
│    • Auth JWT                            │
│    • Stats & gestion users              │
│    • Broadcast Telegram                 │
│                                          │
│  DB: Supabase PostgreSQL                │
└─────────────────────────────────────────┘
              ↕ même DB
┌─────────────────────────────────────────┐
│         RAILWAY / RENDER / REPLIT        │
│                                          │
│  Bot Telegram Python (polling/webhook)  │
│    • Handlers aiogram                   │
│    • Signaux Lucky Jet / Mines          │
│    • Approbation utilisateurs           │
│                                          │
│  DB: Supabase PostgreSQL (partagée)     │
└─────────────────────────────────────────┘
```

---

## 4. Checklist avant déploiement

- [ ] Token Telegram valide dans les secrets (`TELEGRAM_BOT_TOKEN`)
- [ ] `SUPABASE_DATABASE_URL` = Session pooler (port 5432) ou Direct Connection
- [ ] `ADMIN_PASSWORD` défini (pour se connecter au panel)
- [ ] `SESSION_SECRET` généré aléatoirement (min 32 caractères)
- [ ] Build local OK : `pnpm --filter @workspace/admin-panel run build`
- [ ] Tables DB créées (automatique au 1er démarrage du bot)
