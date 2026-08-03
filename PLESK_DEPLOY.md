# Déploiement GitHub → Plesk

Le dépôt contient le workspace Replit et une application autonome pour Plesk.
Dans Plesk, il faut utiliser **`plesk-deployment/` comme Application root**.
Ne sélectionne pas la racine du dépôt : son `package.json` est le workspace
PNPM Replit et n'est pas le package de production Plesk.

## Préparation avant le push GitHub

Depuis la racine du dépôt :

```bash
cd plesk-deployment
npm ci
npm run typecheck
npm run build
npm run check:bot
npm run deploy:check
```

Les commandes doivent toutes réussir. Le build génère et met à jour les
artefacts versionnés :

- `plesk-deployment/client-dist/`
- `plesk-deployment/dist/index.cjs`

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
| Application root | `plesk-deployment` |
| Application startup file | `dist/index.cjs` |
| Node.js version | 20 ou supérieure |
| Application mode | Production |

Ajoute les variables de `plesk-deployment/.env.example` dans les variables
d'environnement Plesk. Le bot Telegram utilise les variables de
`plesk-deployment/telegram-bot/.env.example` dans son propre processus.
Les variables du bot doivent être présentes dans l'environnement du processus
Python lancé par Supervisor/systemd ou le gestionnaire de processus Plesk.

Active l'installation NPM si Plesk propose cette option. Elle doit s'exécuter
dans `plesk-deployment/`, là où se trouvent `package.json` et
`package-lock.json`.

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
/voltatrucks.online/plesk-deployment/dist/index.cjs
```

Si Plesk affiche `/voltatrucks.online/app.js`, l'**Application root** ou le
champ **Application startup file** est configuré sur une ancienne valeur.
Il faut régler la racine sur `/voltatrucks.online/plesk-deployment` et le
startup file sur `dist/index.cjs`.

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

Pour Supervisor ou un gestionnaire de processus Plesk, utiliser cette commande
avec `plesk-deployment` comme répertoire de travail :

```bash
bash /voltatrucks.online/plesk-deployment/telegram-bot/start.sh
```

Le processus Python doit recevoir `BOT_TOKEN` et
`DATABASE_URL` ou `SUPABASE_DATABASE_URL` dans son propre environnement. Les
variables configurées uniquement dans l'application Node.js Plesk ne sont pas
forcément transmises à Supervisor.
