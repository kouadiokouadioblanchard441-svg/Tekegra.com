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
d'environnement de l'application Node Plesk. Plesk héberge uniquement le panel
administrateur et l'API Node.js. Le bot Telegram est installé sur le VPS avec
le service systemd fourni dans `deployment/`.

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

Le bot Telegram n'est pas lancé par Replit ni par Plesk. Sur le VPS, copie le
dépôt, crée l'utilisateur `telegrambot`, puis installe le service :

```bash
sudo mkdir -p /opt/lucky-jet-ai-bot
sudo chown -R telegrambot:telegrambot /opt/lucky-jet-ai-bot
cd /opt/lucky-jet-ai-bot
sudo -u telegrambot git clone <URL_DU_DEPOT> .
sudo -u telegrambot cp deployment/telegram-bot.env.example \
  plesk-deployment/telegram-bot/.env
sudo cp deployment/telegram-bot.service.example \
  /etc/systemd/system/telegram-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-bot
sudo systemctl status telegram-bot
```

Modifie le chemin `/opt/lucky-jet-ai-bot` dans le fichier systemd si
nécessaire. Remplis le fichier `.env` du VPS avec `BOT_TOKEN` et
`SUPABASE_DATABASE_URL` ou `DATABASE_URL`. Le service crée automatiquement le
virtualenv, installe les dépendances, vérifie Telegram, initialise PostgreSQL
et démarre le polling.

Pour suivre les logs du bot :

```bash
sudo journalctl -u telegram-bot -f
```

Le contrôle de build du bot depuis `plesk-deployment/` est :

```bash
npm run check:bot
```

Pour vérifier uniquement les imports du bot sans le démarrer :

```text
cd /opt/lucky-jet-ai-bot/plesk-deployment/telegram-bot
python3 -c "import main; print('bot imports: ok')"
```

## Initialisation du mot de passe administrateur

Dans les variables d'environnement Node.js de Plesk, configure :

```text
ADMIN_PASSWORD=<mot de passe admin choisi>
ADMIN_PASSWORD_RESET=false
```

Au premier démarrage, le backend crée automatiquement le hash
`bot_settings.admin_password_hash` dans PostgreSQL. Si un hash ancien existe
déjà et que le mot de passe est inconnu, mets temporairement :

```text
ADMIN_PASSWORD_RESET=true
```

Redémarre l'application Plesk une fois, puis remets immédiatement
`ADMIN_PASSWORD_RESET=false` et redémarre encore une fois. Ne mets jamais le
mot de passe en clair dans GitHub.

Après le **Pull → Deploy Now → Restart App** de Plesk, vérifie :

```text
https://TON-DOMAINE/api/healthz
```

Puis redémarre le bot sur le VPS :

```bash
sudo systemctl restart telegram-bot
sudo systemctl status telegram-bot
```
