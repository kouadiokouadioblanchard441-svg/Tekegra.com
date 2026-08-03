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
d'environnement de l'application Node Plesk. **Plesk héberge toute la
production sur ce même VPS** : le panel et l'API avec Node.js, et le bot
Telegram avec Python/systemd. Il n'y a pas de deuxième serveur.

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

Le bot Telegram n'est pas lancé par Replit. Il est lancé sur le **même VPS
Plesk** avec Python et systemd. Depuis le terminal du serveur Plesk, installe
le service :

```bash
sudo useradd --system --home /voltatrucks.online --shell /usr/sbin/nologin telegrambot || true
sudo chown -R telegrambot:telegrambot /voltatrucks.online/plesk-deployment/telegram-bot
sudo cp deployment/telegram-bot.env.example \
  /voltatrucks.online/plesk-deployment/telegram-bot/.env
sudo chmod 600 /voltatrucks.online/plesk-deployment/telegram-bot/.env
sudo cp deployment/telegram-bot.service.example \
  /etc/systemd/system/telegram-bot.service
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-bot
sudo systemctl status telegram-bot
```

Si le compte système de l'abonnement Plesk doit être utilisé, remplace
`telegrambot` par ce compte dans le fichier systemd et conserve les droits
d'accès au dossier. Remplis le fichier `.env` sur Plesk avec `BOT_TOKEN` et
`SUPABASE_DATABASE_URL` ou `DATABASE_URL`. Le service Python crée
automatiquement le virtualenv, installe les dépendances, vérifie Telegram,
initialise PostgreSQL et démarre le polling.

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
cd /voltatrucks.online/plesk-deployment/telegram-bot
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

Puis redémarre le bot sur le même serveur Plesk :

```bash
sudo systemctl restart telegram-bot
sudo systemctl status telegram-bot
```
