import pg from "pg";

const { Pool } = pg;
const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error("DATABASE_URL is required for the PostgreSQL connection.");
}

const sslEnabled = process.env.DB_SSL === "true";

export const pool = new Pool({
  connectionString,
  max: Number(process.env.DB_POOL_MAX ?? 10),
  idleTimeoutMillis: 30_000,
  connectionTimeoutMillis: 10_000,
  ...(sslEnabled ? { ssl: { rejectUnauthorized: false } } : {}),
});

pool.on("error", (error) => {
  process.stderr.write(`[db] unexpected idle client error: ${error.message}\n`);
});

export async function closeDatabase(): Promise<void> {
  await pool.end();
}