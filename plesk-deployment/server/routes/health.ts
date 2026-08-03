import { Router } from "express";
import { pool } from "../db.js";
import { getTelegramBotRuntime } from "../bot-runtime.js";

const router = Router();

router.get("/healthz", async (_req, res) => {
  try {
    await pool.query("SELECT 1");
    res.json({
      status: "ok",
      database: "ok",
      telegramBot: getTelegramBotRuntime(),
    });
  } catch {
    res.status(503).json({ status: "degraded", database: "unavailable" });
  }
});

export default router;