# Lucky Jet AI Bot — package Plesk

Ce dossier est une variante autonome pour un hébergement Plesk Linux. Il
contient :

- `client-dist/` : panneau admin React déjà compilé ;
- `dist/index.cjs` : build final CommonJS du serveur Node.js ;
- `telegram-bot/` : bot Telegram séparé, conservé en Python/aiogram ;
- `database/` : emplacement réservé aux migrations SQL complémentaires ;
- `.env.example` : variables du serveur Node ;
- `telegram-bot/.env.example` : variables du bot.

Le panneau admin et l’API sont servis par **un seul processus Node.js**. Le
bot Telegram Python/aiogram est un second service `systemd` sur **le même VPS
qui héberge Plesk**. Il n'y a pas de VPS externe. Replit sert uniquement au
développement et au build.

## Prérequis

- Plesk Linux avec Node.js **20 ou supérieur** ;
- npm 10 ou supérieur ;
- PostgreSQL 14 ou supérieur, local ou managé ;
- Python 3.10 ou supérieur pour le bot ;
- certificat TLS actif sur le domaine.

## Installation du serveur Node

1. Dans Plesk, créer une application Node.js pour le domaine.
2. Choisir `/voltatrucks.online` comme **Application root**.
3. Choisir `dist/index.cjs` comme **Application startup file**.
4. Définir les variables d’environnement de `.env.example` dans Plesk
   (ne jamais téléverser un fichier `.env` contenant des secrets).
5. Dans Plesk, activer **NPM install** si l’option est proposée.
6. Depuis le dossier de l’application, vérifier les artefacts :

```bash
npm ci --omit=dev
npm run deploy:check
```

Les bundles de production `client-dist/` et `dist/index.cjs` sont versionnés dans
Git pour que **Pull + Deploy Now**, puis **Restart App**, fonctionne sans
dépendre d’un hook de build Plesk. Si le code source a été modifié localement,
reconstruire avant le push depuis la racine du dépôt :

```bash
cd ..
npm run build
cd plesk-deployment
npm run check:bot
npm run deploy:check
```

Plesk démarre ensuite :

```bash
npm start
```

Le démarrage exécute les migrations PostgreSQL idempotentes avant d’ouvrir le
port. Il initialise aussi le hash du mot de passe admin si `ADMIN_PASSWORD` est
configuré. Il ne supprime jamais de table et ne remplace jamais de données.
Il démarre également le bot Python local avec les mêmes variables Plesk, sauf
si `TELEGRAM_BOT_AUTOSTART=false`.

## Configuration PostgreSQL

Utiliser une URL PostgreSQL complète dans `DATABASE_URL` :

```text
postgresql://user:password@host:5432/database
```

Activer `DB_SSL=true` pour un fournisseur qui impose TLS. Avec Supabase,
utiliser l’URL de connexion PostgreSQL fournie par Supabase et vérifier que le
pooler choisi est compatible avec l’application.

Vérifier ensuite :

```bash
curl -fsS https://example.com/api/healthz
```

Une réponse saine ressemble à :

```json
{"status":"ok","database":"ok"}
```

## Déploiement du bot Telegram sur le même VPS Plesk

Le bot n'est pas lancé par Replit. Par défaut, il est lancé automatiquement par
le processus Node Plesk avec Python :

```bash
bash /voltatrucks.online/plesk-deployment/telegram-bot/start.sh
```

Le fichier `deployment/telegram-bot.service.example` fournit le service
systemd. Le fichier `deployment/telegram-bot.env.example` fournit les variables
du processus Python. Le script crée automatiquement le virtualenv, installe
les dépendances et lance `main.py`.

```text
BOT_TOKEN=<token fourni par BotFather>
SUPABASE_DATABASE_URL=<URL PostgreSQL Supabase>
```

`DATABASE_URL` peut remplacer `SUPABASE_DATABASE_URL`. Les variables définies
dans l'application Node Plesk sont transmises au bot. Le fichier privé
`/voltatrucks.online/plesk-deployment/telegram-bot/.env` peut aussi être utilisé
et ne doit jamais être ajouté à Git.

Le code du bot utilise la syntaxe Python 3.10 (`X | Y`) et nécessite donc
Python 3.10 ou supérieur. Si Plesk installe Python 3.10+ hors du `PATH`, définis
`BOT_PYTHON` avec le chemin complet vers l'interpréteur, par exemple :

```text
BOT_PYTHON=/opt/plesk/python/3.12/bin/python3
```

Si tu choisis systemd au lieu de l'autostart Node, définis
`TELEGRAM_BOT_AUTOSTART=false` dans Plesk et configure alors les variables dans
le `EnvironmentFile` du service systemd. N'utilise pas les deux méthodes en
même temps.

## Mot de passe admin

Configure `ADMIN_PASSWORD` dans les variables Node.js de Plesk. Au démarrage,
le backend crée le hash dans `bot_settings` s'il n'existe pas. Pour réinitialiser
un hash existant, utilise temporairement `ADMIN_PASSWORD_RESET=true`, redémarre
Plesk une fois, puis remets la variable à `false`.

## Checklist de mise en production

- [ ] Domaine et certificat TLS configurés.
- [ ] Node.js 20+ sélectionné dans Plesk.
- [ ] `DATABASE_URL` renseignée et testée.
- [ ] `SESSION_SECRET` générée avec au moins 32 caractères aléatoires.
- [ ] `DOMAIN_URL` et `CORS_ORIGINS` limités au domaine public exact.
- [ ] `BOT_TOKEN`, `ADMIN_ID` et l'URL PostgreSQL du bot sont renseignés dans
      le fichier privé `.env` du même VPS Plesk.
- [ ] `npm ci` terminé sans erreur.
- [ ] `npm run deploy:check` confirme les bundles présents.
- [ ] Startup file réglé sur `dist/index.cjs`.
- [ ] Le port de l’application est celui fourni par Plesk via `PORT`.
- [ ] `GET /api/healthz` retourne `database: ok`.
- [ ] La page `/login` s’affiche après un redémarrage de l’application.
- [ ] Le mot de passe admin est déjà présent sous la clé
      `bot_settings.admin_password_hash`.
- [ ] Le bot démarre automatiquement avec l'application Plesk et reçoit les
      mises à jour Telegram.
- [ ] Les logs Node sont consultables dans Plesk et les logs Python avec
      `journalctl -u telegram-bot`.
- [ ] Les sauvegardes PostgreSQL et la rotation des logs sont activées.
- [ ] Les fichiers `.env` et `node_modules/` ne sont pas publiés dans Git.
- [ ] Les bundles `dist/index.cjs` et `client-dist/` sont présents dans Git
      pour le déploiement Pull + Deploy Now.

## Flux GitHub → Plesk

Aucune archive ZIP n’est nécessaire. Le build produit les dossiers
`client-dist/` et `dist/index.cjs`, qui sont versionnés dans GitHub. Après le
push, Plesk utilise **Pull → Deploy Now → Restart App**.

Depuis la racine du dépôt, le contrôle complet du package, y compris les
imports Python du bot, est :

```bash
npm run typecheck
npm run build
npm run check:bot
npm run deploy:check
```

Aucune archive ZIP n'est nécessaire et le script de génération d'archive a été
supprimé. Le seul livrable est le dossier `plesk-deployment/` avec ses bundles
compilés, à pousser dans GitHub.