import { spawn, type ChildProcess } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import app from "./app.js";
import { closeDatabase, pool } from "./db.js";
import { logger } from "./lib/logger.js";
import { runMigrations } from "./scripts/migrate.js";

const port = Number(process.env.PORT ?? 3000);
if (!Number.isInteger(port) || port <= 0 || port > 65_535) {
  throw new Error("PORT must be a valid TCP port.");
}

async function start(): Promise<void> {
  await runMigrations();
  await pool.query("SELECT 1");

  let botProcess: ChildProcess | undefined;
  if (process.env.TELEGRAM_BOT_AUTOSTART !== "false") {
    const executableDir = path.dirname(path.resolve(process.argv[1] ?? process.cwd()));
    const botStartScript = [
      path.resolve(process.cwd(), "plesk-deployment", "telegram-bot", "start.sh"),
      path.resolve(process.cwd(), "telegram-bot", "start.sh"),
      path.resolve(executableDir, "..", "plesk-deployment", "telegram-bot", "start.sh"),
      path.resolve(executableDir, "..", "telegram-bot", "start.sh"),
    ].find((candidate) => existsSync(candidate));

    if (!botStartScript) {
      logger.error("Telegram bot start.sh was not found in the Plesk deployment.");
    } else {
      botProcess = spawn("bash", [botStartScript], {
        cwd: path.dirname(botStartScript),
        env: process.env,
        stdio: "inherit",
      });
      logger.info({ pid: botProcess.pid }, "Telegram bot started by the Plesk app");
      botProcess.once("error", (error) => {
        logger.error({ err: error }, "Telegram bot could not be started");
      });
      botProcess.once("exit", (code, signal) => {
        if (code === 0) {
          logger.info("Telegram bot stopped");
        } else {
          logger.error({ code, signal }, "Telegram bot exited unexpectedly");
        }
      });
    }
  } else {
    logger.info("Telegram bot autostart disabled by TELEGRAM_BOT_AUTOSTART=false");
  }

  const server = app.listen(port, "0.0.0.0", () => {
    logger.info({ port }, "Plesk production server listening");
  });

  async function shutdown(signal: string): Promise<void> {
    logger.info({ signal }, "Shutdown requested");
    if (botProcess && !botProcess.killed) {
      botProcess.kill("SIGTERM");
    }
    server.close(async () => {
      await closeDatabase();
      process.exit(0);
    });
    setTimeout(() => process.exit(1), 10_000).unref();
  }

  process.once("SIGTERM", () => void shutdown("SIGTERM"));
  process.once("SIGINT", () => void shutdown("SIGINT"));
}

void start().catch(async (error: unknown) => {
  logger.error({ err: error }, "Plesk production server failed to start");
  await closeDatabase().catch(() => undefined);
  process.exit(1);
});