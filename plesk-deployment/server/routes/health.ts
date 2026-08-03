import { Router } from "express";
import { pool } from "../db.js";
import { getTelegramBotRuntime } from "../bot-runtime.js";

const router = Router();

router.get("/healthz", async (_req, res) => {
  try {
    await pool.query("SELECT 1");
    const telegramBot = getTelegramBotRuntime();
    const healthy = telegramBot.state === "running";
    res.status(healthy ? 200 : 503).json({
      status: healthy ? "ok" : "degraded",
      database: "ok",
      telegramBot,
    });
  } catch {
    res.status(503).json({ status: "degraded", database: "unavailable" });
  }
});

export default router;