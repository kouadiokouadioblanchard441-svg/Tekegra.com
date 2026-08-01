# Déploiement — Guide complet

## Architecture

```
┌──────────────────────────────────────────────────┐
│                    VERCEL                         │
│                                                   │
│  /              → Panneau Admin (React)           │
│  /api/*         → API Express Node.js (serverless)│
│  /api/webhook   → Bot Telegram Python (serverless)│
│  /api/webhook/* → Gestion sécurisée du webhook       │
│                                                   │
│  DB : Supabase PostgreSQL (partagée)              │
└──────────────────────────────────────────────────┘
```

> ⚠️ **Limite importante :** Vercel Functions sont stateless et ne gardent pas
> un processus Python actif entre deux requêtes. Le webhook répond bien aux
> messages Telegram, mais les tâches d'arrière-plan (comme la suppression
> automatique des signaux après 10 minutes) ne fonctionnent pas de manière
> fiable dans cette architecture. Pour ce comportement et un bot réellement
> continu, utilisez un déploiement **VM** ou un hébergeur qui maintient le
> processus Python actif.

---

## Étape 1 — Pousser le code sur GitHub

Si ce n'est pas déjà fait :

1. Crée un dépôt sur [github.com/new](https://github.com/new)
2. Dans le shell Replit :

```bash
git remote add origin https://github.com/TON_USERNAME/NOM_DU_REPO.git
git add -A
git commit -m "Initial commit"
git push -u origin main
```

---

## Étape 2 — Créer le projet sur Vercel

1. Va sur [vercel.com/new](https://vercel.com/new)
2. Clique **"Add New Project"** → **"Import Git Repository"**
3. Sélectionne ton dépôt GitHub
4. Vercel détecte le `vercel.json` — **ne modifie rien** aux paramètres de build

---

## Étape 3 — Variables d'environnement

**Avant de cliquer "Deploy"**, développe la section **"Environment Variables"** et ajoute :

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SUPABASE_DATABASE_URL` | URL Supabase **Session pooler (port 5432)** | `postgresql://postgres.xxx:pass@aws-0-eu.pooler.supabase.com:5432/postgres` |
| `BOT_TOKEN` | Token du bot (@BotFather) | secret |
| `ADMIN_PASSWORD` | Mot de passe du panneau admin | `MonMotDePasse2024!` |
| `SESSION_SECRET` | Clé JWT aléatoire (32+ caractères) | `xK9mP2qL7nR4vW8yZ1aB3cD5eF` |
| `ADMIN_ID` | ID Telegram admin | `123456789` |
| `CHANNEL_1_ID` | _(optionnel)_ Ancienne configuration de chaîne | `-1001234567890` |
| `CHANNEL_1_LINK` | _(optionnel)_ Lien de chaîne | `https://t.me/moncanal` |
| `CHANNEL_1_NAME` | _(optionnel)_ Nom affiché | `📢 Canal Officiel` |

> ⚠️ `SUPABASE_DATABASE_URL` : utilise le **Session pooler (port 5432)** obligatoirement,
> **pas** le Transaction pooler (port 6543).
>
> Les chaînes obligatoires se configurent désormais dans **Panel admin →
> Configuration → Canaux requis**. L'ID numérique et le lien sont enregistrés
> dans la base de données.

---

## Étape 4 — Déployer

Clique **"Deploy"**. Le build prend ~2–3 minutes :
- ✅ `pnpm install`
- ✅ Build admin panel React
- ✅ Compilation API Node.js
- ✅ Packaging fonction Python (bot webhook)

---

## Étape 5 — Enregistrement automatique du webhook

Le build de production Vercel appelle automatiquement Telegram avec :

```
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
```

Le webhook enregistré est toujours :

```
https://TON-APP.vercel.app/api/webhook
```

Le secret `WEBHOOK_SECRET` est envoyé à Telegram et exigé par l’endpoint.
Il n’y a donc pas de route `/setup` publique ni de token dans une URL.

---

## Étape 6 — Vérifier

| URL | Ce que tu dois voir |
|-----|---------------------|
| `https://TON-APP.vercel.app/` | Panneau admin (page de login) |
| `https://TON-APP.vercel.app/api/healthz` | `{"status":"ok"}` |
| `https://TON-APP.vercel.app/api/webhook` | `POST uniquement — secret Telegram requis` |

Teste le bot Telegram — envoie `/start`.

---

## Gestion et vérification du webhook

Les routes de gestion sont POST uniquement et nécessitent simultanément :

```
Authorization: Bearer WEBHOOK_SECRET
X-Admin-ID: ADMIN_ID
```

Routes disponibles :

- `POST /api/webhook/setup` — enregistre puis vérifie le webhook ;
- `POST /api/webhook/info` — affiche l’URL, l’état, les erreurs et les updates en attente ;
- `POST /api/webhook/delete` — supprime le webhook.

## Redéploiements automatiques

Chaque `git push` sur la branche `main` redéclenche automatiquement le build Vercel.  
Le webhook reste enregistré — **pas besoin de refaire l'étape 5**.

---

## Dépannage

| Symptôme | Cause probable | Solution |
|----------|---------------|----------|
| Build échoue | Erreur TypeScript | Vérifie les logs Vercel → onglet "Build" |
| Bot ne répond pas | Webhook non enregistré | Refais l'étape 5 |
| Erreur DB au démarrage | Mauvaise URL Supabase | Vérifie que c'est le port **5432** (Session pooler) |
| Panneau admin inaccessible | Build admin panel raté | Vérifie `SUPABASE_DATABASE_URL` dans Vercel env vars |
| `/setup` répond 401 | Mauvais token | Le `?token=` doit être égal à `ADMIN_PASSWORD` |

---

## Variables optionnelles

Ces variables peuvent être ajoutées dans Vercel → Settings → Environment Variables :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `BOT_PROMO_CODE` | `JRYVES` | Code promo 1WIN affiché dans les signaux |
| `BOT_AFFILIATE_LINK` | _(vide)_ | Lien d'inscription 1WIN |
| `FREE_SIGNALS_TOTAL` | `10` | Quota gratuit total par utilisateur |
| `PREMIUM_SIGNALS_PER_DAY` | `9` | Signaux premium par jour |
| `CHANNEL_2_ID` | _(vide)_ | 2ème chaîne obligatoire |
| `CHANNEL_2_LINK` | _(vide)_ | Lien 2ème chaîne |
| `CHANNEL_2_NAME` | _(vide)_ | Nom 2ème chaîne |
