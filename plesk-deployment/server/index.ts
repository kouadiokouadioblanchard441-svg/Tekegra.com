import { spawn, type ChildProcess } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import app from "./app.js";
import { closeDatabase, pool } from "./db.js";
import { logger } from "./lib/logger.js";
import { runMigrations } from "./scripts/migrate.js";
import { setTelegramBotRuntime } from "./bot-runtime.js";

const port = Number(process.env.PORT ?? 3000);
if (!Number.isInteger(port) || port <= 0 || port > 65_535) {
  throw new Error("PORT must be a valid TCP port.");
}

async function start(): Promise<void> {
  await runMigrations();
  await pool.query("SELECT 1");

  let botProcess: ChildProcess | undefined;
  let botRestartTimer: NodeJS.Timeout | undefined;
  let shuttingDown = false;

  function scheduleBotRestart(): void {
    if (shuttingDown || botRestartTimer) return;
    botRestartTimer = setTimeout(() => {
      botRestartTimer = undefined;
      startTelegramBot();
    }, 10_000);
    botRestartTimer.unref();
  }

  function startTelegramBot(): void {
    if (shuttingDown) return;

    const executableDir = path.dirname(
      path.resolve(process.argv[1] ?? process.cwd()),
    );
    const botStartScript = [
      path.resolve(
        process.cwd(),
        "plesk-deployment",
        "telegram-bot",
        "start.sh",
      ),
      path.resolve(process.cwd(), "telegram-bot", "start.sh"),
      path.resolve(
        executableDir,
        "..",
        "plesk-deployment",
        "telegram-bot",
        "start.sh",
      ),
      path.resolve(executableDir, "..", "telegram-bot", "start.sh"),
    ].find((candidate) => existsSync(candidate));

    if (!botStartScript) {
      setTelegramBotRuntime({
        state: "missing",
        lastError: "telegram-bot/start.sh was not found",
      });
      logger.error(
        {
          cwd: process.cwd(),
          executableDir,
        },
        "Telegram bot start.sh was not found in the Plesk deployment",
      );
      return;
    }

    setTelegramBotRuntime({
      state: "starting",
      script: botStartScript,
      lastError: undefined,
    });

    botProcess = spawn("bash", [botStartScript], {
      cwd: path.dirname(botStartScript),
      env: process.env,
      stdio: "inherit",
    });
    setTelegramBotRuntime({
      state: "running",
      pid: botProcess.pid,
      startedAt: new Date().toISOString(),
    });
    logger.info(
      { pid: botProcess.pid, script: botStartScript },
      "Telegram bot started by the Plesk app",
    );

    botProcess.once("error", (error) => {
      setTelegramBotRuntime({
        state: "exited",
        lastError: error.message,
      });
      logger.error({ err: error }, "Telegram bot could not be started");
    });
    botProcess.once("exit", (code, signal) => {
      botProcess = undefined;
      if (shuttingDown) {
        setTelegramBotRuntime({ state: "stopped", pid: undefined });
        logger.info("Telegram bot stopped");
        return;
      }
      setTelegramBotRuntime({
        state: "exited",
        pid: undefined,
        lastExit: {
          code,
          signal,
          at: new Date().toISOString(),
        },
      });
      logger.error(
        { code, signal },
        "Telegram bot exited unexpectedly; retrying in 10 seconds",
      );
      scheduleBotRestart();
    });
  }

  if (process.env.TELEGRAM_BOT_AUTOSTART !== "false") {
    startTelegramBot();
  } else {
    setTelegramBotRuntime({ state: "disabled" });
    logger.info("Telegram bot autostart disabled by TELEGRAM_BOT_AUTOSTART=false");
  }

  const server = app.listen(port, "0.0.0.0", () => {
    logger.info({ port }, "Plesk production server listening");
  });

  async function shutdown(signal: string): Promise<void> {
    logger.info({ signal }, "Shutdown requested");
    shuttingDown = true;
    if (botRestartTimer) {
      clearTimeout(botRestartTimer);
      botRestartTimer = undefined;
    }
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