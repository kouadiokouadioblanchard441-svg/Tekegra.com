/**
 * Prepares a self-contained Vercel deployment rooted at artifacts/admin-panel/.
 *
 * Run AFTER:
 *   pnpm --filter @workspace/admin-panel run build
 *   pnpm --filter @workspace/api-server exec node build-vercel-app.mjs
 *
 * This script does NOT import esbuild — it only copies already-built files:
 *
 *   1. artifacts/api-server/dist/vercel-app.mjs
 *      → artifacts/admin-panel/api/index.mjs   (Node serverless function)
 *
 *   2. api/webhook.py, api/webhook_admin.py, api/telegram_webhook.py,
 *      api/requirements.txt
 *      → artifacts/admin-panel/api/            (Python serverless functions)
 *
 *   3. artifacts/telegram-bot/
 *      → artifacts/admin-panel/artifacts/telegram-bot/
 *         (bot code imported by Python functions via ../artifacts/telegram-bot)
 *
 *   4. Ensures React build is at artifacts/admin-panel/dist/index.html
 */

import path from "node:path";
import { fileURLToPath } from "node:url";
import fs from "node:fs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const adminPanel = path.resolve(root, "artifacts/admin-panel");
const apiDest = path.resolve(adminPanel, "api");

// ─── 1. Node function: copy bundled Express app ───────────────────────────────

const distVercel = path.resolve(root, "artifacts/api-server/dist-vercel");
const vercelAppSrc = path.resolve(distVercel, "vercel-app.mjs");
if (!fs.existsSync(vercelAppSrc)) {
  throw new Error(
    `artifacts/api-server/dist-vercel/vercel-app.mjs not found.\n` +
    `Run: pnpm --filter @workspace/api-server exec node build-vercel-app.mjs`
  );
}

fs.rmSync(apiDest, { recursive: true, force: true });
fs.mkdirSync(apiDest, { recursive: true });

fs.copyFileSync(vercelAppSrc, path.resolve(apiDest, "index.mjs"));
console.log("  ✓ api/index.mjs copied from api-server bundle");

// Copy pino worker bundles emitted alongside the main bundle
for (const file of fs.readdirSync(distVercel)) {
  if (file.startsWith("pino-") || file === "thread-stream-worker.mjs") {
    fs.copyFileSync(
      path.resolve(distVercel, file),
      path.resolve(apiDest, file)
    );
    console.log(`  ✓ api/${file} copied (pino worker)`);
  }
}

// ─── 2. Python functions ──────────────────────────────────────────────────────

for (const file of ["webhook.py", "webhook_admin.py", "telegram_webhook.py", "requirements.txt"]) {
  const src = path.resolve(root, "api", file);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, path.resolve(apiDest, file));
    console.log(`  ✓ api/${file} copied`);
  } else {
    console.warn(`  ⚠ api/${file} not found — skipping`);
  }
}

// ─── 3. Telegram bot ─────────────────────────────────────────────────────────

const botSrc = path.resolve(root, "artifacts/telegram-bot");
const botDest = path.resolve(adminPanel, "artifacts", "telegram-bot");
if (fs.existsSync(botSrc)) {
  fs.rmSync(botDest, { recursive: true, force: true });
  fs.mkdirSync(path.dirname(botDest), { recursive: true });
  fs.cpSync(botSrc, botDest, {
    recursive: true,
    filter: (src) => !src.includes("__pycache__") && !src.endsWith(".pyc"),
  });
  console.log("  ✓ artifacts/telegram-bot/ copied");
} else {
  console.warn("  ⚠ artifacts/telegram-bot/ not found — Python functions will fail at runtime");
}

// ─── 4. Ensure dist/ is at artifacts/admin-panel/dist/index.html ─────────────

const distCandidates = [
  path.resolve(adminPanel, "dist"),
  path.resolve(adminPanel, "dist/public"),
];
const reactDist = distCandidates.find((d) => fs.existsSync(path.join(d, "index.html")));
const vercelDist = path.resolve(adminPanel, "dist");

if (!reactDist) {
  throw new Error("React build output not found. Run vite build first.");
}
if (path.resolve(reactDist) !== vercelDist) {
  // Move dist/public/* → dist/
  fs.rmSync(vercelDist, { recursive: true, force: true });
  fs.cpSync(reactDist, vercelDist, { recursive: true });
  console.log("  ✓ dist/public → dist/ moved for Vercel");
} else {
  console.log("  ✓ dist/ already in place");
}

if (!fs.existsSync(path.join(vercelDist, "index.html"))) {
  throw new Error("dist/index.html missing — Vercel static output is incomplete");
}

console.log("\n✅ Admin-panel Vercel deployment assets ready.");
