/**
 * Register Telegram's webhook during a Vercel production build.
 *
 * It intentionally does not print the token or the full Telegram response.
 * Local and preview builds skip this step; only a production Vercel build
 * may change Telegram's webhook target.
 */
const isProductionVercel =
  process.env.VERCEL === "1" && process.env.VERCEL_ENV === "production";
if (!isProductionVercel) {
  console.log("Telegram webhook registration skipped outside a Vercel production build.");
  process.exit(0);
}

const token = process.env.BOT_TOKEN;
// APP_URL is the stable production URL and should be configured explicitly.
// VERCEL_URL is a safe first-deployment fallback when the generated project
// domain is not known yet; the next production deploy will use APP_URL.
const appUrl = (
  process.env.APP_URL ||
  (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "")
).replace(/\/+$/, "");
const secret = process.env.WEBHOOK_SECRET;

if (!token || !appUrl || !secret) {
  console.log(
    "Telegram webhook registration skipped: configure BOT_TOKEN, APP_URL and WEBHOOK_SECRET, then redeploy Production.",
  );
  process.exit(0);
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