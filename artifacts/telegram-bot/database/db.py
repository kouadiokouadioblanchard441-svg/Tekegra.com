from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from loguru import logger
import os


class Base(DeclarativeBase):
    pass


def _get_db_url() -> tuple[str, dict]:
    """Return (cleaned_url, connect_args) for asyncpg, stripping sslmode query param.

    asyncpg does not accept sslmode= as a URL query parameter.
    We use urllib.parse to safely rebuild the query string so we don't
    accidentally corrupt other params, then map sslmode → ssl connect_arg
    with full certificate verification kept intact.
    """
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

    raw = os.environ.get("DATABASE_URL", "")
    if not raw:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    # Normalise scheme for SQLAlchemy + asyncpg
    if raw.startswith("postgresql://"):
        raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql+asyncpg://", 1)

    parsed = urlparse(raw)
    params = parse_qs(parsed.query, keep_blank_values=True)

    # Extract sslmode before stripping it (asyncpg rejects it as a query param)
    sslmode_values = params.pop("sslmode", [])
    sslmode = sslmode_values[0] if sslmode_values else ""

    # Rebuild query string without sslmode
    clean_query = urlencode({k: v[0] for k, v in params.items()})
    clean_parsed = parsed._replace(query=clean_query)
    url = urlunparse(clean_parsed)

    # Map sslmode → ssl connect_arg with full verification (no CERT_NONE)
    connect_args: dict = {}
    if sslmode in ("require", "verify-ca", "verify-full"):
        connect_args["ssl"] = True   # asyncpg uses Python's default SSL ctx (CERT_REQUIRED)
    elif sslmode == "prefer":
        connect_args["ssl"] = "prefer"  # asyncpg supports this string value

    return url, connect_args


engine = None
AsyncSessionLocal = None


def get_engine():
    global engine
    if engine is None:
        url, connect_args = _get_db_url()
        engine = create_async_engine(
            url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    return engine


def get_session_factory():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return AsyncSessionLocal


async def get_session():
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_db():
    """Create all tables and apply lightweight schema migrations."""
    from . import models  # noqa: F401
    from sqlalchemy import text
    eng = get_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Idempotent migrations: add columns that may not exist yet in older DBs
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
            "approval_status VARCHAR(20) NOT NULL DEFAULT 'approved'"
        ))
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
            "has_registered BOOLEAN NOT NULL DEFAULT false"
        ))
    logger.info("✅ Database tables initialized")
