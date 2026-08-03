import { access } from "node:fs/promises";

const requiredFiles = [
  "client-dist/index.html",
  "dist/index.cjs",
  "telegram-bot/main.py",
  "telegram-bot/start.sh",
  "telegram-bot/requirements.txt",
  "telegram-bot/.env.example",
  "package-lock.json",
];

for (const file of requiredFiles) {
  try {
    await access(file);
  } catch {
    console.error(`Missing deployment artifact: ${file}`);
    console.error("Run `npm run build` before restarting the Plesk application.");
    process.exit(1);
  }
}

console.log("Plesk deployment artifacts are present.");