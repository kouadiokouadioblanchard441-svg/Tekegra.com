import { pool } from "../db.js";
import { logger } from "../lib/logger.js";

const statements = [
  `CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'fr',
    is_premium BOOLEAN NOT NULL DEFAULT FALSE,
    is_banned BOOLEAN NOT NULL DEFAULT FALSE,
    approval_status VARCHAR(20) NOT NULL DEFAULT 'approved',
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    has_registered BOOLEAN NOT NULL DEFAULT FALSE,
    total_analyses INTEGER NOT NULL DEFAULT 0,
    free_signals_used_today INTEGER NOT NULL DEFAULT 0,
    last_signal_date VARCHAR(20),
    free_signals_used_total INTEGER NOT NULL DEFAULT 0
  )`,
  `CREATE TABLE IF NOT EXISTS premium_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    payment_method VARCHAR(100),
    amount DOUBLE PRECISION,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
  )`,
  `CREATE TABLE IF NOT EXISTS signal_history (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    game_type VARCHAR(50) NOT NULL,
    signal_data JSONB NOT NULL,
    is_premium BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  )`,
  `CREATE TABLE IF NOT EXISTS bot_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  )`,
  `CREATE TABLE IF NOT EXISTS broadcast_logs (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    sent_count INTEGER NOT NULL DEFAULT 0,
    failed_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    admin_id BIGINT NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    action VARCHAR(255) NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  )`,
  `CREATE INDEX IF NOT EXISTS users_telegram_id_idx ON users (telegram_id)`,
  `CREATE INDEX IF NOT EXISTS users_registered_at_idx ON users (registered_at DESC)`,
  `CREATE INDEX IF NOT EXISTS users_approval_status_idx ON users (approval_status)`,
  `CREATE INDEX IF NOT EXISTS users_last_active_idx ON users (last_active DESC)`,
  `CREATE INDEX IF NOT EXISTS signal_history_user_id_idx ON signal_history (user_id)`,
  `CREATE INDEX IF NOT EXISTS activity_logs_created_at_idx ON activity_logs (created_at DESC)`,
  `ALTER TABLE users ADD COLUMN IF NOT EXISTS approval_status VARCHAR(20) NOT NULL DEFAULT 'approved'`,
  `ALTER TABLE users ADD COLUMN IF NOT EXISTS has_registered BOOLEAN NOT NULL DEFAULT FALSE`,
  `ALTER TABLE users ADD COLUMN IF NOT EXISTS free_signals_used_total INTEGER NOT NULL DEFAULT 0`,
];

export async function runMigrations(): Promise<void> {
  for (const statement of statements) {
    await pool.query(statement);
  }
  logger.info({ statements: statements.length }, "Database migrations complete");
}