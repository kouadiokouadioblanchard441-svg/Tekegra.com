import app from "./app.js";
import { closeDatabase, pool } from "./db.js";
import { logger } from "./lib/logger.js";
import { runMigrations } from "./scripts/migrate.js";

const port = Number(process.env.PORT ?? 3000);
if (!Number.isInteger(port) || port <= 0 || port > 65_535) {
  throw new Error("PORT must be a valid TCP port.");
}

await runMigrations();
await pool.query("SELECT 1");

const server = app.listen(port, "0.0.0.0", () => {
  logger.info({ port }, "Plesk production server listening");
});

async function shutdown(signal: string): Promise<void> {
  logger.info({ signal }, "Shutdown requested");
  server.close(async () => {
    await closeDatabase();
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 10_000).unref();
}

process.on("SIGTERM", () => void shutdown("SIGTERM"));
process.on("SIGINT", () => void shutdown("SIGINT"));