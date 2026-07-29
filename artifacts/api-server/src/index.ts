import app from "./app";
import { logger } from "./lib/logger";
import { pool } from "@workspace/db";
import bcrypt from "bcryptjs";

const rawPort = process.env["PORT"];

if (!rawPort) {
  throw new Error(
    "PORT environment variable is required but was not provided.",
  );
}

const port = Number(rawPort);

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

/**
 * Au premier démarrage, si ADMIN_PASSWORD est défini et qu'aucun hash
 * n'existe encore dans bot_settings, on hash et on stocke automatiquement.
 * Cela garantit que la DB est toujours la source de vérité pour le mot de passe.
 */
async function seedAdminPassword(): Promise<void> {
  const envPassword = process.env.ADMIN_PASSWORD;
  if (!envPassword) return;

  try {
    const { rows } = await pool.query(
      `SELECT value FROM bot_settings WHERE key = 'admin_password_hash' LIMIT 1`
    );

    if (rows.length === 0) {
      // Aucun hash en base — on hash et on stocke
      const hash = await bcrypt.hash(envPassword, 12);
      await pool.query(
        `INSERT INTO bot_settings (key, value)
         VALUES ('admin_password_hash', $1)
         ON CONFLICT (key) DO NOTHING`,
        [hash]
      );
      logger.info("Admin password seeded into database from ADMIN_PASSWORD env var");
    } else {
      logger.info("Admin password already stored in database — skipping seed");
    }
  } catch (err) {
    logger.warn({ err }, "Could not seed admin password (DB may not be ready yet)");
  }
}

app.listen(port, async (err) => {
  if (err) {
    logger.error({ err }, "Error listening on port");
    process.exit(1);
  }

  logger.info({ port }, "Server listening");
  await seedAdminPassword();
});
