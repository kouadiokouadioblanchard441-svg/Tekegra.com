# Déploiement GitHub → Plesk

Le dépôt contient le workspace Replit et une application autonome pour Plesk.
Le build synchronise les artefacts de production à la racine du dépôt afin que
Plesk puisse utiliser `/voltatrucks.online` comme **Application root**.

## Préparation avant le push GitHub

Depuis la racine du dépôt :

```bash
npm run build
cd plesk-deployment
npm run check:bot
npm run deploy:check
```

Les commandes doivent toutes réussir. Le build génère et met à jour les
artefacts versionnés :

- `client-dist/`
- `dist/index.cjs`

Le même build peut être lancé directement dans `plesk-deployment/` avec
`npm run build`.

Ensuite, depuis la racine du dépôt :

```bash
git add -A
git diff --cached --check
git commit -m "Prepare Plesk deployment"
git push origin main
```

Ne pousse jamais un fichier `.env`. Les seuls fichiers d'environnement
versionnés sont les `.env.example`.

Aucune archive ZIP n'est nécessaire pour ce déploiement. Les dossiers
`client-dist/` et `dist/index.cjs` sont compilés puis versionnés directement
dans GitHub.

## Configuration Plesk une seule fois

Dans **Websites & Domains → Node.js** :

| Paramètre | Valeur |
|---|---|
| Application root | `/voltatrucks.online` |
| Application startup file | `dist/index.cjs` |
| Node.js version | 20 ou supérieure |
| Application mode | Production |

Ajoute les variables de `plesk-deployment/.env.example` dans les variables
d'environnement de l'application Node Plesk. Le bot Python est démarré
automatiquement par `dist/index.cjs` et hérite du même environnement.

Si Plesk propose l'installation NPM, elle peut être désactivée : `dist/index.cjs`
est un bundle autonome. Le package de build se trouve dans
`plesk-deployment/`.

## À chaque mise à jour

1. Faire les changements.
2. Exécuter les commandes de build ci-dessus.
3. Faire `git add -A`, `git commit`, puis `git push`.
4. Dans Plesk, cliquer **Pull**.
5. Cliquer **Deploy Now**.
6. Cliquer **Restart App**.
7. Vérifier :

```text
https://TON-DOMAINE/api/healthz
```

La réponse attendue est :

```json
{"status":"ok","database":"ok"}
```

La migration PostgreSQL est exécutée au démarrage du serveur. Elle est
idempotente et ne supprime pas les données.

## Si Plesk ne reconstruit pas automatiquement

Ce n'est pas bloquant : les bundles `client-dist/` et `dist/index.cjs` sont déjà
committés dans Git. Après **Pull + Deploy Now + Restart App**, Plesk peut
démarrer directement `dist/index.cjs`.

Pour vérifier manuellement dans le terminal Plesk :

```bash
cd plesk-deployment
npm run deploy:check
```

Le chemin complet du fichier de démarrage sera donc :

```text
/voltatrucks.online/dist/index.cjs
```

Si Plesk affiche `/voltatrucks.online/app.js`, l'**Application root** ou le
champ **Application startup file** est configuré sur une ancienne valeur.
Il faut régler la racine sur `/voltatrucks.online` et le startup file sur
`dist/index.cjs`.

```bash
cd plesk-deployment/telegram-bot
bash start.sh
```

Après l'installation, le bot vérifie automatiquement le token Telegram avec
`getMe`, initialise PostgreSQL, supprime l'ancien webhook puis démarre le
polling. Pour vérifier uniquement les imports sans démarrer le bot :

```bash
python -c "import main; print('bot imports: ok')"
```

Le contrôle de build équivalent depuis `plesk-deployment/` est :

```bash
npm run check:bot
```

Le bot Telegram n'est pas lancé par Replit. Le démarrage Plesk de
`dist/index.cjs` lance automatiquement le bot Python comme processus séparé,
avec le même environnement que l'application Node.

La commande manuelle de diagnostic est :

```bash
bash /voltatrucks.online/plesk-deployment/telegram-bot/start.sh
```

Dans les variables d'environnement de l'application Node Plesk, ajouter :

```text
BOT_TOKEN=<token fourni par BotFather>
SUPABASE_DATABASE_URL=<URL PostgreSQL Supabase>
```

`DATABASE_URL` peut remplacer `SUPABASE_DATABASE_URL`. Le script accepte aussi
un fichier local
`/voltatrucks.online/plesk-deployment/telegram-bot/.env` (non versionné), mais
ce fichier n'est pas nécessaire lorsque les variables sont configurées dans
Plesk.

Le bot a son propre processus Python, mais il est automatiquement démarré par
`dist/index.cjs`. Ne configure pas un deuxième service Supervisor/systemd pour
le bot si `TELEGRAM_BOT_AUTOSTART` est absent ou vaut `true`.

Si tu utilises volontairement un superviseur Python externe, configure :

```text
TELEGRAM_BOT_AUTOSTART=false
```

dans l'application Node Plesk, afin d'éviter deux processus de polling.

Après avoir vérifié les variables, effectuer **Pull → Deploy Now → Restart
App`. Le démarrage doit afficher une connexion Telegram vérifiée,
l'initialisation PostgreSQL, puis `Starting polling`.
