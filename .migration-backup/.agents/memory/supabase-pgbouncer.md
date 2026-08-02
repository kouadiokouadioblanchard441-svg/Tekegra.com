---
name: Supabase PgBouncer asyncpg fix
description: How to fix DuplicatePreparedStatementError when using asyncpg + SQLAlchemy with Supabase connection pooler
---

The Supabase transaction pooler (port 6543) uses PgBouncer in transaction mode, which is incompatible with asyncpg's prepared statement protocol.

**Fix:** Add `statement_cache_size: 0` to `connect_args` in `create_async_engine()`.

```python
connect_args = {"statement_cache_size": 0}
engine = create_async_engine(url, connect_args=connect_args)
```

**Why:** asyncpg caches prepared statements by default; PgBouncer transaction mode drops server-side prepared statements between transactions, causing `DuplicatePreparedStatementError`.

**How to apply:** Any time the project uses asyncpg with Supabase. Also applies to other PgBouncer transaction-mode proxies. File: `artifacts/telegram-bot/database/db.py` in `_get_db_url()`.

**Alternative:** Use the Supabase Session pooler (port 5432) or Direct connection — both support prepared statements and don't need this fix.
