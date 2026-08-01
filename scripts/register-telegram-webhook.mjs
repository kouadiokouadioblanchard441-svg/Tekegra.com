/**
 * Register Telegram's webhook during a Vercel production build.
 *
 * It intentionally does not print the token or the full Telegram response.
 * Local builds skip this step; Vercel builds fail clearly if the required
 * production values are missing.
 */
const isVercel = process.env.VERCEL === "1";
if (!isVercel) {
  console.log("Telegram webhook registration skipped outside Vercel.");
  process.exit(0);
}

const token = process.env.BOT_TOKEN;
const appUrl = (process.env.APP_URL || "").replace(/\/+$/, "");
const secret = process.env.WEBHOOK_SECRET;

if (!token || !appUrl || !secret) {
  throw new Error("BOT_TOKEN, APP_URL and WEBHOOK_SECRET are required for Vercel webhook registration.");
}
if (!appUrl.startsWith("https://")) {
  throw new Error("APP_URL must start with https://");
}

const result = await fetch(`https://api.telegram.org/bot${token}/setWebhook`, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    url: `${appUrl}/api/webhook`,
    secret_token: secret,
    // Telegram interprets [] as all update types.
    allowed_updates: [],
    drop_pending_updates: false,
  }),
});
const payload = await result.json();
if (!result.ok || !payload.ok) {
  throw new Error(`Telegram webhook registration failed with HTTP ${result.status}.`);
}
console.log(`Telegram webhook registered at ${appUrl}/api/webhook.`);