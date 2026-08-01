import { Router } from "express";
import bcrypt from "bcryptjs";
import { pool } from "@workspace/db";
import { requireAuth, signToken } from "../middleware/auth.js";

const router = Router();

/** Récupère le hash du mot de passe depuis Supabase. */
async function getStoredPasswordHash(): Promise<string | null> {
  const { rows } = await pool.query(
    `SELECT value FROM bot_settings WHERE key = 'admin_password_hash' LIMIT 1`
  );
  return rows[0]?.value ?? null;
}

// ─── Auth ────────────────────────────────────────────────────────────────────

router.post("/admin/login", async (req, res) => {
  const { password } = req.body as { password?: string };
  if (!password) {
    res.status(401).json({ error: "Invalid password" });
    return;
  }

  try {
    const hash = await getStoredPasswordHash();
    if (!hash) {
      res.status(503).json({ error: "Admin password is not configured in Supabase" });
      return;
    }

    const valid = await bcrypt.compare(password, hash);

    if (!valid) {
      res.status(401).json({ error: "Invalid password" });
      return;
    }
    const token = signToken();
    res.json({ token });
  } catch (e: any) {
    res.status(500).json({ error: e.message });
  }
});

// ─── Change password ──────────────────────────────────────────────────────────

router.post("/admin/change-password", requireAuth, async (req, res) => {
  const { currentPassword, newPassword } = req.body as {
    currentPassword?: string;
    newPassword?: string;
  };

  if (!currentPassword || !newPassword) {
    res.status(400).json({ error: "currentPassword and newPassword are required" });
    return;
  }
  if (newPassword.length < 6) {
    res.status(400).json({ error: "New password must be at least 6 characters" });
    return;
  }

  try {
    // Vérifie le mot de passe actuel dans Supabase.
    const hash = await getStoredPasswordHash();
    if (!hash) {
      res.status(503).json({ error: "Admin password is not configured in Supabase" });
      return;
    }

    const validCurrent = await bcrypt.compare(currentPassword, hash);

    if (!validCurrent) {
      res.status(401).json({ error: "Current password is incorrect" });
      return;
    }

    // Hash le nouveau mot de passe et l'enregistre dans bot_settings
    const newHash = await bcrypt.hash(newPassword, 12);
    await pool.query(`
      INSERT INTO bot_settings (key, value)
      VALUES ('admin_password_hash', $1)
      ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
    `, [newHash]);

    res.json({ success: true, message: "Password updated successfully" });
  } catch (e: any) {
    res.status(500).json({ error: e.message });
  }
});

// ─── Stats ───────────────────────────────────────────────────────────────────

router.get("/admin/stats", requireAuth, async (_req, res) => {
  try {
    const { rows } = await pool.query(`
      SELECT
        COUNT(*) FILTER (WHERE TRUE)                         AS "totalUsers",
        COUNT(*) FILTER (WHERE approval_status = 'approved') AS "approvedUsers",
        COUNT(*) FILTER (WHERE is_premium = TRUE)            AS "premiumUsers",
        COUNT(*) FILTER (WHERE approval_status = 'pending')  AS "pendingUsers",
        COUNT(*) FILTER (WHERE is_banned = TRUE)             AS "bannedUsers",
        COUNT(*) FILTER (
          WHERE last_active >= NOW() - INTERVAL '24 hours'
        )                                                    AS "activeToday"
      FROM users
    `);

    const sigRow = await pool.query(`SELECT COALESCE(SUM(total_analyses),0) AS total FROM users`);

    res.json({
      totalUsers:    Number(rows[0].totalUsers),
      approvedUsers: Number(rows[0].approvedUsers),
      premiumUsers:  Number(rows[0].premiumUsers),
      pendingUsers:  Number(rows[0].pendingUsers),
      bannedUsers:   Number(rows[0].bannedUsers),
      activeToday:   Number(rows[0].activeToday),
      totalSignals:  Number(sigRow.rows[0].total),
    });
  } catch (e: any) {
    res.status(500).json({ error: e.message });
  }
});

// ─── Users ───────────────────────────────────────────────────────────────────

router.get("/admin/users", requireAuth, async (req, res) => {
  const status  = (req.query.status  as string) || "all";
  const page    = Math.max(1, parseInt((req.query.page  as string) || "1", 10));
  const limit   = Math.min(100, Math.max(1, parseInt((req.query.limit as string) || "20", 10)));
  const search  = (req.query.search as string) || "";
  const offset  = (page - 1) * limit;

  const ALLOWED_STATUSES = ["all","pending","approved","rejected","banned"];
  if (!ALLOWED_STATUSES.includes(status)) {
    res.status(400).json({ error: "Invalid status" }); return;
  }

  const conditions: string[] = [];
  const params: (string | number)[] = [];
  let pi = 1;

  if (status === "banned") {
    conditions.push(`is_banned = TRUE`);
  } else if (status !== "all") {
    conditions.push(`approval_status = $${pi++}`);
    params.push(status);
    conditions.push(`is_banned = FALSE`);
  }

  if (search) {
    conditions.push(`(
      CAST(telegram_id AS TEXT) ILIKE $${pi} OR
      COALESCE(username,'') ILIKE $${pi} OR
      COALESCE(first_name,'') ILIKE $${pi}
    )`);
    params.push(`%${search}%`);
    pi++;
  }

  const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";

  const countQ = await pool.query(
    `SELECT COUNT(*) AS total FROM users ${where}`,
    params
  );
  const total = Number(countQ.rows[0].total);

  const dataQ = await pool.query(
    `SELECT
       telegram_id           AS "telegramId",
       username,
       first_name            AS "firstName",
       last_name             AS "lastName",
       language_code         AS "languageCode",
       is_premium            AS "isPremium",
       is_banned             AS "isBanned",
       has_registered        AS "hasRegistered",
       approval_status       AS "approvalStatus",
       total_analyses        AS "totalAnalyses",
       free_signals_used_today AS "freeSignalsUsedToday",
       registered_at         AS "registeredAt",
       last_active           AS "lastActive"
     FROM users ${where}
     ORDER BY registered_at DESC
     LIMIT $${pi} OFFSET $${pi + 1}`,
    [...params, limit, offset]
  );

  res.json({ users: dataQ.rows, total, page, limit });
});

// helper — fetch one user or 404
async function getUser(telegramId: number, res: any) {
  const { rows } = await pool.query(
    `SELECT telegram_id FROM users WHERE telegram_id = $1`,
    [telegramId]
  );
  if (!rows.length) { res.status(404).json({ error: "User not found" }); return null; }
  return rows[0];
}

router.post("/admin/users/:telegramId/approve", requireAuth, async (req, res) => {
  const id = parseInt(String(req.params.telegramId), 10);
  if (isNaN(id)) { res.status(400).json({ error: "Bad id" }); return; }
  const user = await getUser(id, res);
  if (!user) return;
  await pool.query(`UPDATE users SET approval_status='approved', is_banned=FALSE WHERE telegram_id=$1`, [id]);
  res.json({ success: true, message: "User approved" });
});

router.post("/admin/users/:telegramId/reject", requireAuth, async (req, res) => {
  const id = parseInt(String(req.params.telegramId), 10);
  if (isNaN(id)) { res.status(400).json({ error: "Bad id" }); return; }
  const user = await getUser(id, res);
  if (!user) return;
  await pool.query(`UPDATE users SET approval_status='rejected' WHERE telegram_id=$1`, [id]);
  res.json({ success: true, message: "User rejected" });
});

router.post("/admin/users/:telegramId/ban", requireAuth, async (req, res) => {
  const id = parseInt(String(req.params.telegramId), 10);
  if (isNaN(id)) { res.status(400).json({ error: "Bad id" }); return; }
  const user = await getUser(id, res);
  if (!user) return;
  await pool.query(`UPDATE users SET is_banned=TRUE WHERE telegram_id=$1`, [id]);
  res.json({ success: true, message: "User banned" });
});

router.post("/admin/users/:telegramId/unban", requireAuth, async (req, res) => {
  const id = parseInt(String(req.params.telegramId), 10);
  if (isNaN(id)) { res.status(400).json({ error: "Bad id" }); return; }
  const user = await getUser(id, res);
  if (!user) return;
  await pool.query(`UPDATE users SET is_banned=FALSE, approval_status='approved' WHERE telegram_id=$1`, [id]);
  res.json({ success: true, message: "User unbanned" });
});

router.post("/admin/users/:telegramId/premium", requireAuth, async (req, res) => {
  const id = parseInt(String(req.params.telegramId), 10);
  if (isNaN(id)) { res.status(400).json({ error: "Bad id" }); return; }
  const user = await getUser(id, res);
  if (!user) return;

  const { active, days } = req.body as { active: boolean; days: number };

  if (active) {
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + (days || 30));
    await pool.query(`UPDATE users SET is_premium=TRUE WHERE telegram_id=$1`, [id]);
    // Upsert premium subscription
    await pool.query(`
      INSERT INTO premium_subscriptions (user_id, expires_at, is_active, payment_method, amount)
      VALUES ($1, $2, TRUE, 'admin', 0)
      ON CONFLICT (user_id) DO UPDATE SET
        expires_at=EXCLUDED.expires_at, is_active=TRUE
    `, [id, expiresAt]);
  } else {
    await pool.query(`UPDATE users SET is_premium=FALSE WHERE telegram_id=$1`, [id]);
    await pool.query(`UPDATE premium_subscriptions SET is_active=FALSE WHERE user_id=$1`, [id]);
  }

  res.json({ success: true, message: active ? `Premium activated for ${days} days` : "Premium removed" });
});

// ─── Settings ─────────────────────────────────────────────────────────────────

async function getSetting(key: string): Promise<string | null> {
  const { rows } = await pool.query(
    `SELECT value FROM bot_settings WHERE key=$1`, [key]
  );
  return rows[0]?.value ?? null;
}

async function setSetting(key: string, value: string): Promise<void> {
  await pool.query(`
    INSERT INTO bot_settings (key, value, updated_at)
    VALUES ($1, $2, NOW())
    ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value, updated_at=NOW()
  `, [key, value]);
}

router.get("/admin/settings", requireAuth, async (_req, res) => {
  const keys = [
    "promo_code","affiliate_link",
    "free_signals_per_day","premium_signals_per_day",
    "channel_1_id","channel_1_link","channel_1_name",
    "channel_2_id","channel_2_link","channel_2_name",
    "support_username",
    "price_7_days_fcfa","price_30_days_fcfa",
    "menu_banner","register_banner","luckyjet_banner","mines_banner","guide_banner",
  ];
  const { rows } = await pool.query(
    `SELECT key, value FROM bot_settings WHERE key = ANY($1::text[])`,
    [keys]
  );
  const map = Object.fromEntries(rows.map((r: any) => [r.key, r.value]));

  res.json({
    promoCode:            map["promo_code"]              ?? "JRYVES",
    affiliateLink:        map["affiliate_link"]          ?? "",
    freeSignalsPerDay:    parseInt(map["free_signals_per_day"]     ?? "3", 10),
    premiumSignalsPerDay: parseInt(map["premium_signals_per_day"]  ?? "50", 10),
    channel1Id:           map["channel_1_id"]            ?? "",
    channel1Link:         map["channel_1_link"]          ?? "",
    channel1Name:         map["channel_1_name"]          ?? "",
    channel2Id:           map["channel_2_id"]            ?? "",
    channel2Link:         map["channel_2_link"]          ?? "",
    channel2Name:         map["channel_2_name"]          ?? "",
    supportUsername:      map["support_username"]        ?? "",
    price7DaysFcfa:       parseInt(map["price_7_days_fcfa"]  ?? "5594", 10),
    price30DaysFcfa:      parseInt(map["price_30_days_fcfa"] ?? "16794", 10),
    menuBanner:           map["menu_banner"]              ?? null,
    registerBanner:       map["register_banner"]          ?? null,
    luckyjetBanner:       map["luckyjet_banner"]          ?? null,
    minesBanner:          map["mines_banner"]             ?? null,
    guideBanner:          map["guide_banner"]             ?? null,
  });
});

router.put("/admin/settings", requireAuth, async (req, res) => {
  const body = req.body as Record<string, unknown>;

  const mapping: Record<string, string> = {
    promoCode:            "promo_code",
    affiliateLink:        "affiliate_link",
    freeSignalsPerDay:    "free_signals_per_day",
    premiumSignalsPerDay: "premium_signals_per_day",
    channel1Id:           "channel_1_id",
    channel1Link:         "channel_1_link",
    channel1Name:         "channel_1_name",
    channel2Id:           "channel_2_id",
    channel2Link:         "channel_2_link",
    channel2Name:         "channel_2_name",
    supportUsername:      "support_username",
    price7DaysFcfa:       "price_7_days_fcfa",
    price30DaysFcfa:      "price_30_days_fcfa",
  };

  for (const [jsKey, dbKey] of Object.entries(mapping)) {
    if (body[jsKey] !== undefined) {
      await setSetting(dbKey, String(body[jsKey]));
    }
  }

  // Re-read and return
  const keys = [
    "promo_code","affiliate_link",
    "free_signals_per_day","premium_signals_per_day",
    "channel_1_id","channel_1_link","channel_1_name",
    "channel_2_id","channel_2_link","channel_2_name",
    "support_username",
    "price_7_days_fcfa","price_30_days_fcfa",
    "menu_banner","register_banner","luckyjet_banner","mines_banner","guide_banner",
  ];
  const { rows } = await pool.query(
    `SELECT key, value FROM bot_settings WHERE key = ANY($1::text[])`,
    [keys]
  );
  const map = Object.fromEntries(rows.map((r: any) => [r.key, r.value]));
  res.json({
    promoCode:            map["promo_code"]              ?? "JRYVES",
    affiliateLink:        map["affiliate_link"]          ?? "",
    freeSignalsPerDay:    parseInt(map["free_signals_per_day"]     ?? "3", 10),
    premiumSignalsPerDay: parseInt(map["premium_signals_per_day"]  ?? "50", 10),
    channel1Id:           map["channel_1_id"]            ?? "",
    channel1Link:         map["channel_1_link"]          ?? "",
    channel1Name:         map["channel_1_name"]          ?? "",
    channel2Id:           map["channel_2_id"]            ?? "",
    channel2Link:         map["channel_2_link"]          ?? "",
    channel2Name:         map["channel_2_name"]          ?? "",
    supportUsername:      map["support_username"]        ?? "",
    price7DaysFcfa:       parseInt(map["price_7_days_fcfa"]  ?? "5594", 10),
    price30DaysFcfa:      parseInt(map["price_30_days_fcfa"] ?? "16794", 10),
    menuBanner:           map["menu_banner"]              ?? null,
    registerBanner:       map["register_banner"]          ?? null,
    luckyjetBanner:       map["luckyjet_banner"]          ?? null,
    minesBanner:          map["mines_banner"]             ?? null,
    guideBanner:          map["guide_banner"]             ?? null,
  });
});

// ─── Broadcast ────────────────────────────────────────────────────────────────

router.post("/admin/broadcast", requireAuth, async (req, res) => {
  const { message } = req.body as { message: string };
  if (!message?.trim()) { res.status(400).json({ error: "Message required" }); return; }

  const BOT_TOKEN = process.env.BOT_TOKEN;
  if (!BOT_TOKEN) { res.status(500).json({ error: "Bot token not configured" }); return; }

  const { rows: users } = await pool.query(
    `SELECT telegram_id FROM users WHERE approval_status='approved' AND is_banned=FALSE`
  );

  let sent = 0, failed = 0;
  const TG = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;

  for (const user of users) {
    try {
      const r = await fetch(TG, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: user.telegram_id,
          text: message,
          parse_mode: "Markdown",
        }),
      });
      if (r.ok) sent++; else failed++;
    } catch {
      failed++;
    }
    // Throttle: ~30 msgs/sec max
    await new Promise(r => setTimeout(r, 35));
  }

  res.json({ sent, failed });
});

export default router;
